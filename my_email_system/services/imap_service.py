import imaplib
import email
from email.header import decode_header
from my_email_system.utils.logger import get_logger

logger = get_logger(__name__)

def connect_imap(username, password, server="imap.gmail.com", port=993):
    """
    Connect to IMAP server with SSL.
    For Outlook, use: "imap-mail.outlook.com"
    """
    try:
        mail = imaplib.IMAP4_SSL(server, port)
        mail.login(username, password)
        return mail
    except Exception as e:
        logger.error(f"[IMAP] Login failed: {e}")
        raise

def fetch_unread_emails(mail, folder="INBOX"):
    """
    Fetch unread emails (their msg_id + parsed message) from a given folder.
    """
    mail.select(folder)
    status, messages = mail.search(None, '(UNSEEN)')
    if status != "OK":
        logger.info(f"No unread messages found in {folder}.")
        return []

    email_ids = messages[0].split()
    logger.info(f"Found {len(email_ids)} unread messages in {folder}.")
    fetched_emails = []

    for msg_id in email_ids:
        status, msg_data = mail.fetch(msg_id, '(RFC822)')
        if status == "OK":
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            fetched_emails.append((msg_id, msg))

    return fetched_emails

def move_to_inbox(mail, msg_id):
    """
    For Gmail: Copy message from Spam to INBOX, then mark original as deleted.
    Outlook: you'd do a move command using a different IMAP folder name for 'Junk'.
    """
    try:
        copy_result = mail.copy(msg_id, "INBOX")
        if copy_result[0] == 'OK':
            mail.store(msg_id, '+FLAGS', '\\Deleted')
            mail.expunge()
            logger.info(f"Message {msg_id} moved to INBOX.")
        else:
            logger.warning(f"Could not copy {msg_id} to INBOX.")
    except Exception as e:
        logger.error(f"Error moving message {msg_id} to INBOX: {e}")
