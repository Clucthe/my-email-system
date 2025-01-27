import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file if present

BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Example: Gmail or Outlook credentials
GMAIL_USERNAME = os.environ.get("GMAIL_USERNAME", "your_gmail_user@gmail.com")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD", "your_app_password")

# Example: Outlook credentials
OUTLOOK_USERNAME = os.environ.get("OUTLOOK_USERNAME", "your_outlook_user@outlook.com")
OUTLOOK_PASSWORD = os.environ.get("OUTLOOK_PASSWORD", "your_outlook_password")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
