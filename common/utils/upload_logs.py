import logging
from datetime import timedelta, datetime

import boto3
from botocore.exceptions import ClientError
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger('common')


def upload_logs_now():
    """
    Uploads log files from local application log directories to an AWS S3 bucket if they were last modified on the previous day.
    
    For each log file in directories ending with "_logs", the function uploads files modified yesterday to a structured S3 path, verifies the upload, deletes the local file upon success, and tracks both successful and failed uploads. After processing, it cleans up old log files beyond the retention period.
    
    Returns:
        dict: A summary containing lists of uploaded and failed files, and their respective counts.
    """
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
        yesterday = timezone.localtime() - timedelta(days=1)
        current_tz = timezone.get_current_timezone()
        for folder in log_root.glob('*_logs'):
            if not folder.is_dir():
                continue
            app_name = folder.name.replace('_logs', '')
            for file_path in folder.glob('*.log*'):
                try:
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=current_tz)
                    if file_mtime.date() == yesterday.date():
                        date_str = yesterday.strftime("%Y-%m-%d")
                        s3_key = f'logs/{app_name}/{date_str}/{file_path.name}'
                        try:
                            s3.upload_file(str(file_path), bucket_name, s3_key)
                            s3.head_object(Bucket=bucket_name, Key=s3_key)
                            uploaded_files.append(s3_key)
                            logger.info(f'Successfully uploaded {file_path} to {s3_key}')
                            file_path.unlink()
                            logger.info(f'Deleted local file: {file_path}')
                        except ClientError as e:
                            logger.error(f'AWS error uploading {file_path}: {e}')
                            failed_uploads.append(str(file_path))
                        except Exception as e:
                            logger.error(f'Failed to upload or verify {file_path}: {e}')
                except Exception as e:
                    logger.error(f'Error processing file {file_path}: {e}')
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
        logger.exception(f'Failed to upload logs due to unexpected error: {e}')
        raise

def cleanup_old_files(log_root, days_to_keep=7):
    """
    Delete log files older than a specified number of days from all subdirectories ending with '_logs'.
    
    Parameters:
    	log_root: The root directory containing log subdirectories.
    	days_to_keep (int): The number of days to retain log files. Files older than this will be deleted.
    """
    current_tz = timezone.get_current_timezone()
    cutoff_date = timezone.localtime() - timedelta(days=days_to_keep)
    for folder in log_root.glob('*_logs'):
        if not folder.is_dir():
            continue
        for file_path in folder.glob('*.log*'):
            try:
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=current_tz)
                if file_mtime < cutoff_date:
                    file_path.unlink()
                    logger.info(f'Deleted old log file: {file_path}')
            except Exception as e:
                logger.error(f'Error deleting old log file {file_path}: {e}')
