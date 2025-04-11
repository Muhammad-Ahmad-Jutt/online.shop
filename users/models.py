import uuid
import os
import jwt
from datetime import datetime, timedelta, date
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from users.manager import UserManager
from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
import string 
import secrets
class CoreUser(AbstractBaseUser):
    """Custom User Model"""

    id = models.UUIDField(_("ID"), default=uuid.uuid4, primary_key=True, unique=True)
    name = models.CharField(_("Name"), max_length=100, null=False, blank=False)
    first_name = models.CharField(_("First Name"), max_length=50, null=False, blank=False)
    last_name = models.CharField(_("Last Name"), max_length=50, null=True, blank=True)  
    age = models.IntegerField(_("Age"), null=False, blank=True,default=0)
    email = models.EmailField(_("Email"), max_length=254, unique=True, null=False, blank=False)
    permission = models.JSONField(_("Permission"), default=dict)  
    password = models.CharField(max_length=255)
    phone_number = PhoneNumberField(_("Phone Number"), unique=True, blank=True, null=True)
    profile_link = models.TextField(null=True, blank=True, default=None)
    google_token = models.TextField(null=True, blank=True, default=None)
    verified = models.BooleanField(default=False)
    created_at = models.DateField(_("User Since"), auto_now_add=True)
    modified_at = models.DateField(_("Updated At"), auto_now=True)
    last_login = models.DateTimeField(_("Last Login"), auto_now=True)

    # Required for Django Admin & Permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = UserManager()  


    def __str__(self):
        return f"{self.name} ---> {self.email}" if self.name else self.email

    def has_perm(self, perm, obj=None):
        """Check permissions (always True for simplicity)"""
        return True

    def has_module_perms(self, app_label):
        """Check if user has permissions for an app (always True)"""
        return True
    def set_password(self, raw_password):
        """Hash the password properly using Django's method"""
        super().set_password(raw_password)  

    def tokens(self):
        """Generate Refresh and Access JWT tokens"""
        refresh = RefreshToken.for_user(self)
        return {
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
        }
    class Meta:
        db_table = "core_user"
        verbose_name_plural = "Core Users"
class PasswordReset(models.Model):

    id = models.UUIDField(_("ID"), default=uuid.uuid4, primary_key=True, unique=True)
    user_id = models.ForeignKey(CoreUser, verbose_name=_("Of User"), on_delete=models.CASCADE)
    code = models.CharField(_("Verification Code"),null=False, blank=False)
    used = models.BooleanField(_("Used Code"), default=False)
    created_at = models.DateTimeField("created_at", auto_now_add=True)
    activate = models.BooleanField('Activate',default=True)
    def __str__(self):
        return f"{self.user_id}--->{self.code}"

    def generate_code(self, length=6):
        chars = string.ascii_uppercase + string.digits
        self.code = ''.join(secrets.choice(chars) for _ in range(length))

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save( *args, **kwargs)
    def is_expired(self):
        return now() > self.created_at + timedelta(minutes=10)
    def deactivate_previous_code(self):
        self.activate=False
        self.save()

    def mark_as_used(self):
        self.used=True
        self.save()

class Verify_Email(models.Model):

    id = models.UUIDField(_("ID"), default=uuid.uuid4, primary_key=True, unique=True)
    user_id = models.ForeignKey(CoreUser, verbose_name=_("Of User"), on_delete=models.CASCADE)
    code = models.CharField(_("Verification Code"),null=False, blank=False)
    used = models.BooleanField(_("Used Code"), default=False)
    created_at = models.DateTimeField("created_at", auto_now_add=True)
    activate = models.BooleanField('Activate', default=True)
    def __str__(self):
        return f"{self.user_id}--->{self.code}"

    def generate_code(self, length=8):
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save( *args, **kwargs)
    def is_expired(self):
        return now() > self.created_at + timedelta(minutes=10)        
    
    def pending_request_in_last_10_min(self):
        ten_minutes_ago = now() - timedelta(minutes=10)
        request_count = Verify_Email.objects.filter(user_id=self.user_id, created_at__gte=ten_minutes_ago).count()
        return request_count >= 2  
    def deactivate_previus_code(self):
        self.activate=False
        self.save()
    
    def mark_as_used(self):
        self.used=True
        self.save()