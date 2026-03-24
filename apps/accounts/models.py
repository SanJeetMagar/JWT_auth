from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password = None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email = self.normalize_email(email) , **extra_fields)
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name =  models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4)
    password_reset_token = models.UUIDField(null=True, blank=True)
    password_reset_expiry = models.DateTimeField(null=True,blank=True)
    objects = CustomUserManager()
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=255,null=True, blank=True)
    phone_number = models.CharField(max_length=255,null=True, blank=True)
    profile_picture = models.ImageField(upload_to="profiles/",null=True, blank=True)
    social_links = models.JSONField(null=True, blank=True)