from celery import shared_task

from common.utils.upload_logs import upload_logs_now


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def upload_to_s3():
    return upload_logs_now()
