import logging
from smtplib import SMTPException, SMTPRecipientsRefused

from celery import shared_task

from common.utils.otp_handler import send_otp
from common.utils.upload_logs import upload_logs_now


logger = logging.getLogger('common')

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def upload_to_s3(self):
    """
    Triggers an immediate upload of logs to Amazon S3.
    
    Returns:
        The result of the log upload operation as provided by `upload_logs_now()`.
    """
    return upload_logs_now()

@shared_task(bind=True, autoretry_for=(SMTPException, SMTPRecipientsRefused, TimeoutError), retry_kwargs={'max_retries': 3, 'countdown': 20})
def send_mail_containing_otp(self, email):
    logger.info(f'Sending OTP to email: {email}')
    try:
        send_otp(email, is_resend=False)
    except (SMTPException, SMTPRecipientsRefused, TimeoutError) as e:
        logger.warning(f"Retrying sending OTP to {email} due to {e}")
        raise self.retry(exc=e, countdown=20) from e
    except Exception as e:
        logger.error(f"Failed to send OTP to {email}: {e}")
        raise
