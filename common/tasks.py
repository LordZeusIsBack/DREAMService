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
    """
    Send a one-time password (OTP) email to the specified address.
    
    Attempts to send an OTP using send_otp(email, is_resend=False). On SMTP-related failures
    (SMTPException, SMTPRecipientsRefused, TimeoutError) the exception is re-raised so the
    Celery task's autoretry can retry the send; other exceptions are logged and re-raised.
    Parameters:
        email (str): Recipient email address for the OTP.
    """
    logger.info(f'Sending OTP to email: {email}')
    try:
        send_otp(email, is_resend=False)
    except (SMTPException, SMTPRecipientsRefused, TimeoutError) as e:
        logger.warning(f"SMTP error sending OTP to {email}: {e}")
        raise  # Let autoretry_for handle the retry
    except Exception as e:
        logger.error(f"Failed to send OTP to {email}: {e}")
        raise
