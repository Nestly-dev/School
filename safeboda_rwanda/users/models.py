from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username=None, email=None, phone=None, password=None, **extra_fields):
        if not username:
            if email:
                username = email.split("@")[0]
            elif phone:
                digits = "".join(ch for ch in str(phone) if ch.isdigit())
                username = digits[-9:] if len(digits) >= 9 else digits
            else:
                raise ValueError("The username, email or phone must be set.")
        email = self.normalize_email(email) if email else None

        user = self.model(username=username, email=email, phone=phone, **extra_fields)
        if not password:
            raise ValueError("The password must be set.")
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if not password:
            raise ValueError("Superuser must have a password.")
        if not username:
            username = (email or "admin").split("@")[0]
        return self.create_user(username=username, email=email, password=password, **extra_fields)


class User(AbstractUser):
    phone = models.CharField(max_length=13, unique=True, null=True, blank=True)   # +2507XXXXXXXX
    national_id = models.CharField(max_length=16, unique=True, null=True, blank=True)
    district = models.CharField(max_length=50, null=True, blank=True)
    language = models.CharField(max_length=2, default="en")  # rw, fr, en

    objects = UserManager()

    def __str__(self):
        return self.username or self.email or (self.phone or "")
