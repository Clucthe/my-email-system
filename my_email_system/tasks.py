from celery import Celery
from celery.exceptions import Retry

from my_email_system import config
from my_email_system.utils.logger import get_logger

logger = get_logger(__name__)

celery_app = Celery(
    'my_email_system',
    broker=config.BROKER_URL,
    backend=config.RESULT_BACKEND
)

# 1. Read/Reply
@celery_app.task(bind=True, max_retries=3)
def read_and_reply_task(self, username, password, imap_server="imap.gmail.com", folder="INBOX"):
    """
    Read unread emails in the 'folder', then reply with a basic message.
    """
    from my_email_system.services.imap_service import connect_imap, fetch_unread_emails
    from my_email_system.services.smtp_service import send_email_smtp

    try:
        mail = connect_imap(username, password, server=imap_server)
        emails = fetch_unread_emails(mail, folder)
        
        for msg_id, msg in emails:
            sender = msg["From"]
            subject = msg["Subject"] or "(No Subject)"
            
            # Basic auto-reply
            reply_body = (
                "Hello,\n\n"
                "Thank you for your email. We will get back to you shortly.\n\n"
                "Best regards,\nEmail Control System"
            )
            send_email_smtp(username, password, [sender], f"Re: {subject}", reply_body)
        
        mail.close()
        mail.logout()
        logger.info(f"Replied to {len(emails)} emails in {folder} for {username}.")
        return True
    except Exception as exc:
        logger.error(f"[read_and_reply_task] Error: {exc} - Retrying...")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

# 2. Send Templated Content
@celery_app.task(bind=True, max_retries=3)
def send_specific_content_task(self, from_addr, password, to_addrs, subject, template_path, context):
    """
    Sends an email with specific (templated) content to the recipient(s).
    """
    from my_email_system.services.smtp_service import send_templated_email_smtp
    try:
        send_templated_email_smtp(from_addr, password, to_addrs, subject, template_path, context)
        return True
    except Exception as exc:
        logger.error(f"[send_specific_content_task] Error: {exc} - Retrying...")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

# 3. Pull from Spam
@celery_app.task(bind=True, max_retries=3)
def pull_from_spam_task(self, username, password, imap_server="imap.gmail.com", subject_keyword=None):
    """
    Move spam emails to the Inbox if they match a certain keyword in the subject.
    """
    from my_email_system.services.imap_service import connect_imap, fetch_unread_emails, move_to_inbox
    try:
        mail = connect_imap(username, password, server=imap_server)
        
        # For Gmail, Spam folder = "[Gmail]/Spam"
        spam_emails = fetch_unread_emails(mail, "[Gmail]/Spam")
        logger.info(f"Checking {len(spam_emails)} spam messages...")

        count_moved = 0
        for msg_id, msg in spam_emails:
            subject = msg["Subject"] or ""
            if subject_keyword:
                if subject_keyword in subject:
                    move_to_inbox(mail, msg_id)
                    count_moved += 1
            else:
                # Move all spam
                move_to_inbox(mail, msg_id)
                count_moved += 1
        
        mail.close()
        mail.logout()
        logger.info(f"Moved {count_moved} messages from Spam to Inbox for {username}.")
        return True
    except Exception as exc:
        logger.error(f"[pull_from_spam_task] Error: {exc} - Retrying...")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
