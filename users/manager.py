from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
import re

class UserManager(BaseUserManager):
    """Custom user manager with password hashing and validations."""

    def validate_name(self, value):
        """Ensures the name contains only alphabets."""
        if not re.match(r'^[A-Za-z]+$', value):
            raise ValidationError("Name must contain only letters.")

    def validate_password(self, password):
        """Ensures password follows security rules."""
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one number.")
        if not any(char.isupper() for char in password):
            raise ValidationError("Password must contain at least one uppercase letter.")

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        """Creates and returns a user with a hashed password."""

        if not email:
            raise ValidationError("Email is required.")
        
        email = self.normalize_email(email)

        if not first_name:
            raise ValidationError("First name is required.")
        self.validate_name(first_name)

        if last_name:
            self.validate_name(last_name)



        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)

        # Hash the password before saving
        user.set_password(password)  # This ensures password is hashed
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        """Creates and returns a superuser with a hashed password."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValidationError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValidationError("Superuser must have is_superuser=True.")

        return self.create_user(email, first_name, last_name, password, **extra_fields)
    def get_by_natural_key(self, username):
        """Django Admin uses this method to look up users."""
        return self.model.objects.get(email=username)  # ✅ Correct way to access the model
