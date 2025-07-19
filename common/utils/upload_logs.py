import logging
from datetime import timedelta

from django.utils import timezone
import boto3
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger('common')

def upload_logs_now():
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

        # Calculate yesterday's date
        yesterday = timezone.now() - timedelta(days=1)

        for folder in log_root.glob('*_logs'):
            if not folder.is_dir():
                continue

            app_name = folder.name.replace('_logs', '')

            for file_path in folder.glob('*.log*'):  # Matches .log, .log.2024-07-17 etc.
                try:
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

                    if file_mtime.date() == yesterday.date():
                        date_str = yesterday.strftime("%Y-%m-%d")
                        s3_key = f'logs/{app_name}/{date_str}/{file_path.name}'

                        try:
                            s3.upload_file(str(file_path), bucket_name, s3_key)
                            uploaded_files.append(s3_key)
                            logger.info(f'Successfully uploaded {file_path} to {s3_key}!')
                            file_path.unlink()
                            logger.info(f'Deleted local file: {file_path}!')
                        except ClientError as e:
                            logger.error(f'AWS error uploading {file_path}: {e}')
                            failed_uploads.append(str(file_path))
                        except Exception as e:
                            logger.error(f'Unexpected error uploading {file_path}: {e}')
                            failed_uploads.append(str(file_path))

                except Exception as e:
                    logger.error(f'Error checking file timestamp for {file_path}: {e}')

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
