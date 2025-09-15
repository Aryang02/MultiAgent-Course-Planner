from smtplib import SMTP
from src.settings import settings
import traceback

def email_helper(to_list, message, subject):
    try:
        with SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            msg = f'Subject: {subject}\n\n{message}'
            smtp.sendmail(settings.EMAIL_HOST_USER, to_list, msg)
    except Exception as e:
        traceback.print_exc()
        print(f"Failed to send email: {str(e)}")