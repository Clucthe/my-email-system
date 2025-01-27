from my_email_system.tasks import (
    read_and_reply_task,
    send_specific_content_task,
    pull_from_spam_task
)
from my_email_system import config

def run_demo():
    # 1. Read & Reply to INBOX
    read_and_reply_task.delay(
        username=config.GMAIL_USERNAME,
        password=config.GMAIL_PASSWORD,
        imap_server="imap.gmail.com",
        folder="INBOX"
    )

    # 2. Send Specific (Templated) Content
    send_specific_content_task.delay(
        from_addr=config.GMAIL_USERNAME,
        password=config.GMAIL_PASSWORD,
        to_addrs=["recipient@example.com"],
        subject="Special Offer Just for You",
        template_path="templates/offer_template.txt",
        context={"name": "John Doe", "offer": "50% discount"}
    )

    # 3. Pull from Spam (Gmail)
    pull_from_spam_task.delay(
        username=config.GMAIL_USERNAME,
        password=config.GMAIL_PASSWORD,
        imap_server="imap.gmail.com",
        subject_keyword="Important"  # or None to move all spam
    )

if __name__ == "__main__":
    run_demo()
