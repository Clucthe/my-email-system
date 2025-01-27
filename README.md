# README

## 1. Overview

**my_email_system** is a scalable email control program built in Python. It manages 100k+ emails across multiple providers (Gmail, Outlook, etc.) with the following capabilities:

- **Read and Reply** to Emails in bulk (e.g., auto-responses).
- **Send Specific (Templated) Content** to thousands of recipients.
- **Pull Certain Emails Out of Spam** (or Promotions in Gmail, if using Gmail API).
- Maintain **Good IP Reputation** by using Celery concurrency controls and best practices for email sending (rate-limiting, domain authentication, etc.).

This project demonstrates how to structure a Python application with Celery for concurrency, IMAP for reading emails, SMTP for sending emails, and Jinja2 for templating.

---

## 2. Features & Capabilities

- **High Volume Support**: Can handle over 100k emails, using Celery to distribute tasks.
- **Read & Reply**: Automatically read unread emails from an IMAP mailbox and send replies.
- **Templated Emails**: Send dynamic emails (e.g., personalized promotions) using Jinja2 templates.
- **Spam Management**: Pull target messages from the Spam (and optionally Promotions with the Gmail API).
- **Queue-Based Architecture**: Uses Celery + Redis (or RabbitMQ) for asynchronous task management.
- **Logging & Monitoring**: Built-in logging with rotating file handlers, can integrate with Celery monitoring tools like Flower.
- **Extensible**: Ready to integrate with OAuth (Gmail API, Microsoft Graph) for more advanced usage and better security.

---

## 3. Project Structure

```bash
my_email_system/
├── __init__.py              # Marks this folder as a Python package
├── config.py                # Configuration (env variables, credentials)
├── main.py                  # Orchestrator script to schedule tasks
├── tasks.py                 # Celery task definitions (read, reply, pull spam, etc.)
├── services/
│   ├── __init__.py
│   ├── imap_service.py      # Handles IMAP connections, reading emails, moving spam
│   └── smtp_service.py      # Handles SMTP sending, templated emails
└── utils/
    ├── __init__.py
    └── logger.py            # Logging setup (rotating file handler, console logs)
templates/
└── offer_template.txt       # Example Jinja2 template for sending specific content
docker-compose.yml           # (Optional) Docker config for Redis + Celery worker
run_celery.sh                # Shell script to run Celery worker
requirements.txt             # Python dependencies
README.md                    # This file
```

### Key Directories & Files

- **`my_email_system/config.py`**: Configure environment variables (like `GMAIL_USERNAME`, `GMAIL_PASSWORD`).
- **`my_email_system/tasks.py`**: Contains all Celery tasks: read-and-reply, send-specific-content, pull-from-spam, etc.
- **`my_email_system/services`**: The business logic for IMAP and SMTP.
- **`templates/`**: Holds your templated content files (Jinja2 format).
- **`docker-compose.yml`**: For spinning up a Redis (or RabbitMQ) service, plus Celery workers, if you want a containerized deployment.

---

## 4. Requirements & Installation

### Prerequisites

- **Docker (optional)**: If you want to use the `docker-compose.yml` file.
- **Python 3.8+**: The code uses modern Python features.
- **Celery and Redis (or RabbitMQ)** for queueing tasks.

### Installing Python Packages

1. Clone or download this repository.
2. Navigate into the project folder:

   ```bash
   cd my_email_system
   ```

3. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   ```

4. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Docker Setup (Optional)

If you want to use Docker Compose for running Redis and Celery:

```bash
docker compose up -d
```

This spins up a Redis container (or you can use RabbitMQ if you modify the config).

---

## 5. Configuration

**`my_email_system/config.py`** uses environment variables by default. You can set them in a `.env` file or in your shell. For example:

```bash
# .env (example)
GMAIL_USERNAME=your_gmail_account@gmail.com
GMAIL_PASSWORD=your_app_password

OUTLOOK_USERNAME=your_outlook_account@outlook.com
OUTLOOK_PASSWORD=your_outlook_password
```

The code attempts to read environment variables like `GMAIL_USERNAME` and `GMAIL_PASSWORD`.

> **Important**: For large-scale usage, consider using OAuth tokens or more secure credential storage.

---

## 6. Usage

### A. Running Celery

#### Without Docker:

```bash
# In the project root
sh run_celery.sh
```

or directly:

```bash
celery -A my_email_system.tasks worker --loglevel=INFO --concurrency=4
```

#### With Docker Compose:

```bash
docker compose up -d
```

This will build and run:

- A Redis container (or RabbitMQ if configured).
- A Celery worker container that processes tasks.

### B. Running the Orchestrator

The `main.py` file triggers the tasks. For a simple demo:

```bash
python -m my_email_system.main
```

This schedules tasks in the Celery queue:

- Read & reply to unread emails in your inbox.
- Send a specific templated email (e.g., `offer_template.txt`).
- Pull emails from Spam if they match a certain keyword.

### C. Monitoring Logs

- **Console output**: The Celery worker logs each task’s status (success/failure).
- **File logs**: The rotating file handler writes to `app.log` (up to 5 MB, with 2 backups).
- **Celery Monitoring**: Optionally, install Flower or another Celery monitoring dashboard.

---

## 7. How It Works (Under the Hood)

### Celery + Redis

- Each “email operation” is defined as a Celery task (in `tasks.py`).
- When `main.py` calls `task.delay(...)`, it queues the job in Redis (or RabbitMQ).
- The Celery worker listens for tasks and executes them asynchronously.

### Reading Emails (IMAP)

- **`services/imap_service.py`** connects to your mail provider’s IMAP server (e.g., `imap.gmail.com`) using credentials from `config.py`.
- It fetches unread messages from a specified folder (e.g., INBOX or Spam).
- If we want to move a message from Spam, we “copy” it to INBOX and mark the original as deleted, then expunge.

### Sending Emails (SMTP)

- **`services/smtp_service.py`** uses SMTP with TLS (port 587) on either Gmail (`smtp.gmail.com`) or Outlook (`smtp-mail.outlook.com`).
- A templated message can be rendered with Jinja2 (e.g., `offer_template.txt`) before sending.

### Pulling from Spam

- For Gmail, we select `[Gmail]/Spam` and look for messages that match a certain subject or keyword.
- Then we move them to “INBOX” (via IMAP copy + delete).
- For “Promotions” specifically, use the Gmail API to remove the `CATEGORY_PROMOTIONS` label (not shown by default, but it’s easy to extend).

### Scalability

- Handling 100k+ emails is possible because Celery can spawn multiple workers (via `--concurrency` or multiple servers).
- Each worker processes IMAP/SMTP tasks in parallel, subject to provider rate limits.

### Maintaining IP/Domain Reputation

- The code includes concurrency controls (e.g., `--concurrency=4`) so you don’t send thousands of emails simultaneously from one account.
- For truly large volumes, warm up multiple sender accounts or use dedicated email services.
- Use DNS records like SPF, DKIM, and DMARC to avoid spam classification.

---

## 8. What to Change Before Running

### Credentials

In `config.py` or your environment, set:

- `GMAIL_USERNAME`
- `GMAIL_PASSWORD`
- `OUTLOOK_USERNAME`
- `OUTLOOK_PASSWORD` (Or whichever accounts you want to use.)

### Broker URL

If using Redis on a different host, update `CELERY_BROKER_URL` in `.env` or `config.py`.

### SMTP/IMAP Servers

By default, Gmail is used (`imap.gmail.com`, `smtp.gmail.com`). For Outlook, change the servers (e.g., `imap-mail.outlook.com`, `smtp-mail.outlook.com`).

### Templates

Customize your `.txt` templates in the `templates/` folder to include the content you want.

### Subject/Keywords

In the Spam-pulling tasks, modify the subject filter to suit your needs.

---

## 9. Maintaining a Good IP Reputation

- **Rate Limits**: Gmail typically allows ~2k emails/day per account for free accounts. Over that, you risk bans.
- **DKIM/SPF/DMARC**: Configure your DNS records to prove authenticity.
- **Content**: Avoid spammy keywords and follow best practices to prevent being flagged.
- **Gradual Increase**: If you have a new sending domain or IP, slowly ramp up sending volume so ISPs learn your domain isn’t spamming.

---

## 10. Future Enhancements

- OAuth 2.0 for Gmail and Microsoft 365, removing reliance on “app passwords.”
- Database Integration to store message IDs, track states, and avoid processing duplicates.
- Scheduling: Use Celery Beat or a CRON job to read & send at specific intervals.
- Advanced Classification with the Gmail API to specifically remove `CATEGORY_PROMOTIONS` labels.
- Delivery/Read Tracking with webhooks or return receipts.

---

## Conclusion

This **my_email_system** application showcases a modular, scalable design for reading, replying, sending templated emails, and moving spam. By leveraging Celery for concurrency, IMAP/SMTP for email operations, and best practices for IP reputation, you can manage 100k+ emails across multiple providers.