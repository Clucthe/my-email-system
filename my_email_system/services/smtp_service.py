import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from jinja2 import Template
from my_email_system.utils.logger import get_logger

logger = get_logger(__name__)

def send_email_smtp(from_addr, password, to_addrs, subject, body):
    """
    Basic SMTP sending with TLS to Gmail or Outlook.
    Gmail: smtp.gmail.com:587
    Outlook: smtp-mail.outlook.com:587
    """
    msg = MIMEText(body, "plain", "utf-8")
    msg['Subject'] = subject
    msg['From'] = formataddr(("My Email System", from_addr))
    msg['To'] = ", ".join(to_addrs) if isinstance(to_addrs, list) else to_addrs

    try:
        # Adjust host/port for Outlook if needed
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(from_addr, password)
        server.sendmail(from_addr, to_addrs, msg.as_string())
        server.quit()
        logger.info(f"Email sent to {to_addrs} - Subject: {subject}")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise

def send_templated_email_smtp(from_addr, password, to_addrs, subject, template_path, context):
    """
    Load a text template from disk, render with Jinja2, then send.
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_str = f.read()
        template = Template(template_str)
        body = template.render(**context)
        send_email_smtp(from_addr, password, to_addrs, subject, body)
    except Exception as e:
        logger.error(f"Error sending templated email: {e}")
        raise
