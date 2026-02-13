from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
import secrets
from .mailjet import send_otp_email


class AdminUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone_number):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self,first_name, last_name, email,password=None):
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user.is_superuser = True
        user.is_staff = True
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomAdmin(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r"^\+?\d{9,15}$")],
        unique=True
    )

    otp_hash = models.CharField(max_length=128, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_attempts = models.PositiveSmallIntegerField(default=0)
    otp_locked_until = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = AdminUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def generate_otp(self):
        self.clear_otp()
        otp = f"{secrets.randbelow(1000000):06d}"
        self.otp_hash = make_password(otp)
        self.otp_created_at = timezone.now()
        self.otp_attempts = 0
        self.otp_locked_until = None
        self.save(update_fields=["otp_hash", "otp_created_at", "otp_attempts", "otp_locked_until"])
        # Send OTP via email
        send_otp_email(self.email, otp, self.first_name)
        return otp  # return plain OTP 

    def verify_otp(self, otp):
        now = timezone.now()

        if self.otp_locked_until and now < self.otp_locked_until:
            raise ValueError("Max OTP attempts reached. Try later.")

        if self.otp_hash is None or self.otp_created_at is None:
            return False

        if now > self.otp_created_at + timedelta(minutes=5):
            self.clear_otp()
            return False

        if check_password(otp, self.otp_hash):
            self.clear_otp()
            return True
        else:
            self.otp_attempts += 1
            if self.otp_attempts >= 3:
                self.otp_locked_until = now + timedelta(minutes=5)
            self.save(update_fields=["otp_attempts", "otp_locked_until"])
            return False

    def clear_otp(self):
        self.otp_hash = None
        self.otp_created_at = None
        self.otp_attempts = 0
        self.otp_locked_until = None
        self.save(update_fields=["otp_hash", "otp_created_at", "otp_attempts", "otp_locked_until"])

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r"^\+?\d{9,15}$")],
        blank=True,
        null=True
    )
    address = models.TextField(blank=True, null=True)
    additional_info = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"

class Client(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    additional_info = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"