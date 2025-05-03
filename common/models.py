from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email: raise ValueError('Email is required!')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']


class UserExtensionMixin(models.Model):
    is_deleted = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='pictures/seller', null=True, blank=True)
    phone_number = models.CharField(max_length=10, unique=True, null=True, blank=True, editable=False)
    is_verified = models.BooleanField(default=False, editable=False)

    class Meta:
        abstract = True


class VerificationMixin(models.Model):
    aadhaar_card = models.ImageField(upload_to='pictures/seller/verification/aadhaar')
    aadhaar_number = models.BigIntegerField(
        validators=[MinValueValidator(10 ** 12), MaxValueValidator(10 ** 13 - 1)],
        unique=True,
        editable=False
    )
    pan_card = models.ImageField(upload_to='pictures/seller/verification/pan')
    pan_number = models.CharField(max_length=10, unique=True, editable=False)

    class Meta:
        abstract = True
