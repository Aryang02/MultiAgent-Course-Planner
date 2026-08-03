import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP, SMTP_SSL

from src.settings import settings

logger = logging.getLogger(__name__)


def _build_message(to_list: list[str], subject: str, plain_text: str, html: str | None) -> str:
    if html:
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))
    else:
        msg = MIMEText(plain_text, "plain", "utf-8")

    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_HOST_USER
    msg["To"] = ", ".join(to_list)
    return msg.as_string()


def build_welcome_email(login_url: str) -> tuple[str, str, str]:
    subject = "Welcome to MCP"
    plain_text = (
        "Welcome to MCP! Your account has been successfully created.\n\n"
        f"Please sign in at: {login_url}"
    )
    html = f"""\
<!DOCTYPE html>
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.5; color: #222;">
    <h2>Welcome to MCP</h2>
    <p>Your account has been successfully created.</p>
    <p>
      <a href="{login_url}" style="display:inline-block;padding:10px 16px;background:#2563eb;color:#fff;text-decoration:none;border-radius:6px;">
        Sign in
      </a>
    </p>
    <p>If the button does not work, copy and paste this link into your browser:<br>{login_url}</p>
  </body>
</html>
"""
    return subject, plain_text, html


def email_helper(
    to_list: list[str],
    message: str,
    subject: str,
    *,
    html: str | None = None,
) -> None:
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        logger.warning("Email credentials not configured; skipping send to %s", to_list)
        return

    payload = _build_message(to_list, subject, message, html)

    try:
        if settings.EMAIL_PORT == 465:
            with SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp:
                smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                smtp.sendmail(settings.EMAIL_HOST_USER, to_list, payload)
        else:
            with SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                smtp.sendmail(settings.EMAIL_HOST_USER, to_list, payload)
    except Exception:
        logger.exception("Failed to send email to %s", to_list)
        raise
