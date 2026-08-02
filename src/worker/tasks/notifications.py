import logging

from src.utils.email_helper import email_helper
from src.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="src.worker.tasks.notifications.send_welcome_email")
def send_welcome_email(to_email: str, message: str, subject: str) -> dict:
    logger.info("Sending welcome email to %s", to_email)
    email_helper([to_email], message, subject)
    return {"sent": True, "to": to_email}
