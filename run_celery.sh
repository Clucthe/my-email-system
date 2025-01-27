#!/bin/bash
# Simple script to run Celery worker with concurrency

celery -A my_email_system.tasks worker --loglevel=INFO --concurrency=4
