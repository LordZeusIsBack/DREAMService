import logging
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import ClientError
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def upload_to_s3(self):
    log_root = settings.LOG_BASE_DIR
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        uploaded_files = []
        failed_uploads = []
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")
        for folder in log_root.glob('*_logs'):
            if not folder.is_dir():
                continue
            app_name = folder.name.replace('_logs', '')
            for file_path in folder.glob(f'{date_str}*.log'):
                if not file_path.name.endswith('.log'):
                    continue
                s3_key = f'logs/{app_name}/{date_str}/{file_path.name}'
                try:
                    s3.upload_file(str(file_path), bucket_name, s3_key)
                    uploaded_files.append(s3_key)
                    logger.info(f'Successfully uploaded {file_path} to {s3_key}!')
                    file_path.unlink()
                    logger.info(f'Deleted local file: {file_path}!')
                except ClientError as e:
                    error_msg = f'AWS error uploading {file_path}: {e}'
                    logger.error(error_msg)
                    failed_uploads.append(str(file_path))
                except Exception as e:
                    error_msg = f'Unexpected error uploading {file_path}: {e}'
                    logger.error(error_msg)
                    failed_uploads.append(str(file_path))
        cleanup_old_files(log_root)
        result = {
            'uploaded_files': uploaded_files,
            'failed_uploads': failed_uploads,
            'total_uploaded': len(uploaded_files),
            'total_failed': len(failed_uploads)
        }
        logger.info(f'Log upload completed: {result}')
        return result
    except Exception as e:
        logger.error(f'Failed to upload logs: {e}')
        raise

def cleanup_old_files(log_root, days_to_keep=7):
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    for folder in log_root.glob('*_logs'):
        if not folder.is_dir():
            continue
        for file_path in folder.glob('*.log*'):
            try:
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_mtime < cutoff_date:
                    file_path.unlink()
                    logger.info(f'Deleted old log file: {file_path}')
            except Exception as e:
                logger.error(f'Error deleting old log file {file_path}: {e}')

@shared_task
def manual_log_upload():
    logger.info('Manual log upload triggered.')
    return upload_to_s3.apply_async()
