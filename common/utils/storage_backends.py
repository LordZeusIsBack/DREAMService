from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    default_acl = None
    file_overwrite = False
    querystring_auth = True
    querystring_expire = 900
    location = 'pictures/'
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
