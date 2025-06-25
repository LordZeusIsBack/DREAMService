from functools import partial
from django.db import models
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from common.utils.storage_backends import MediaStorage
from uuid import uuid4

def get_user_document_upload_path(instance, filename, subfolder):
    """
    Generate a unique and organized file upload path for user documents based on user type and subfolder.
    
    Parameters:
        instance: The model instance associated with the file upload, used to determine user type.
        filename: The original name of the uploaded file.
        subfolder: The subdirectory under the user type where the file should be stored.
    
    Returns:
        str: A file path in the format '<user_type>/<subfolder>/<slugified-filename>.<short-uuid>.<extension>'.
    """
    user_type = 'buyer' if hasattr(instance, 'buyer') else 'seller'
    base, extension = filename.rsplit('.', 1)
    safe_filename = f'{slugify(base)}.{uuid4().hex[:8]}.{extension}'
    return f'{user_type}/{subfolder}/{safe_filename}'

profile_picture_path = partial(get_user_document_upload_path, subfolder='profile_pictures')
aadhaar_card_image_path = partial(get_user_document_upload_path, subfolder='verification/aadhaar_card')
pan_card_image_path = partial(get_user_document_upload_path, subfolder='verification/pan_card')

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email: raise ValueError('Users must have an email address')
        if not password: raise ValueError('Users must have a password')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True: raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True: raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class UserExtensionMixin(models.Model):
    is_deleted = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to=profile_picture_path, null=True, blank=True, storage=MediaStorage)
    phone_number = models.CharField(max_length=10, unique=True, null=True, blank=True, editable=False)
    is_verified = models.BooleanField(default=False, editable=False)

    class Meta:
        abstract = True


class VerificationMixin(models.Model):
    aadhaar_card = models.ImageField(upload_to=aadhaar_card_image_path, null=True, blank=True, storage=MediaStorage)
    aadhaar_number = models.BigIntegerField(
        validators=[MinValueValidator(10 ** 12), MaxValueValidator(10 ** 13 - 1)],
        unique=True,
        editable=False
    )
    pan_card = models.ImageField(upload_to=pan_card_image_path, null=True, blank=True, storage=MediaStorage)
    pan_number = models.CharField(max_length=10, unique=True, editable=False)

    class Meta:
        abstract = True
