from functools import partial
from django.db import models
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from common.utils.storage_backends import MediaStorage
from uuid import uuid4

def get_user_document_upload_path(instance, filename, subfolder):
    """
    Generate a unique and organized file upload path for a user's document or image.
    
    The path includes the user type ('buyer' or 'seller'), a specified subfolder, and a sanitized filename with a short UUID to prevent collisions.
    
    Parameters:
        instance: The model instance associated with the file upload.
        filename (str): The original name of the uploaded file.
        subfolder (str): The subdirectory under the user type where the file will be stored.
    
    Returns:
        str: The constructed file path for storing the uploaded file.
    """
    user_type = 'buyer' if hasattr(instance.user, 'buyer') else 'seller'
    base, extension = filename.rsplit('.', 1)
    safe_filename = f'{slugify(base)}.{uuid4().hex[:8]}.{extension}'
    return f'{user_type}/{instance.user}/{subfolder}/{safe_filename}'

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

    def save(self, *args, **kwargs):
        """
        Override the save method to prevent changes to the email and username fields after initial creation.
        
        Raises:
            ValidationError: If an attempt is made to modify the email or username of an existing user.
        """
        if self.pk:
            try:
                original = type(self).objects.get(pk=self.pk)
                if original.email != self.email: raise ValidationError('Email address once set cannot be changed!.')
                if original.username != self.username: raise ValidationError('Username once set cannot be changed!.')
            except type(self).DoesNotExist: pass
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Return the string representation of the user as their email address.
        """
        return self.email


class UserExtensionMixin(models.Model):
    profile_picture = models.ImageField(upload_to=profile_picture_path, null=True, blank=True, storage=MediaStorage)
    phone_number = models.IntegerField(validators=[MinValueValidator(10 ** 9), MaxValueValidator(10 ** 10 - 1)], unique=True, editable=False)
    is_verified = models.BooleanField(default=False, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Override the save method to prevent changes to the phone number after initial creation.
        
        Raises:
            ValidationError: If an attempt is made to modify the phone number once it has been set.
        """
        if self.pk:
            try:
                original = type(self).objects.get(pk=self.pk)
                if original.phone_number != self.phone_number: raise ValidationError('Phone number once set cannot be changed!')
            except type(self).DoesNotExist: pass
        super().save(*args, **kwargs)


class VerificationMixin(models.Model):
    aadhaar_card = models.ImageField(upload_to=aadhaar_card_image_path, null=True, blank=True, storage=MediaStorage)
    aadhaar_number = models.BigIntegerField(
        validators=[MinValueValidator(10 ** 12), MaxValueValidator(10 ** 13 - 1)],
        unique=True,
        editable=False
    )
    pan_card = models.ImageField(upload_to=pan_card_image_path, null=True, blank=True, storage=MediaStorage)
    pan_number = models.CharField(max_length=10, unique=True, editable=False)

    def save(self, *args, **kwargs):
        """
        Save the instance while enforcing immutability of Aadhaar and PAN numbers and their associated card images.
        
        Raises a ValidationError if an attempt is made to modify the `aadhaar_number`, `pan_number`, `aadhaar_card`, or `pan_card` fields after they have been set.
        """
        if self.pk:
            try:
                original = type(self).objects.get(pk=self.pk)
                if original.aadhaar_number != self.aadhaar_number: raise ValidationError('Aadhaar Number once set cannot be changed!')
                if original.pan_number != self.pan_number: raise ValidationError('Pan Number once set cannot be changed!')
                if original.aadhaar_card and self.aadhaar_card:
                    if original.aadhaar_card.name != self.aadhaar_card.name:
                        raise ValidationError('Aadhaar Card once set cannot be changed!')
                if original.pan_card and self.pan_card:
                    if original.pan_card.name != self.pan_card.name:
                        raise ValidationError('Pan Card once set cannot be changed!')
            except type(self).DoesNotExist: pass
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
