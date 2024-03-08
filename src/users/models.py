"""
This file contains all the models for users module
"""

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from utils.files import FILE_STORAGE, RenameFile, ValidateFileSize
from utils.models import BaseModel


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, password, **kwargs):
        email = self.normalize_email(email=email)
        user = self.model(email=email, first_name=first_name, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_active", True)
        return self.create_user(email=email, first_name=first_name, **kwargs)


class User(AbstractUser):
    """
    This model is used to store user details.
    """

    username = None
    email = models.EmailField(max_length=256, unique=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return (self.first_name.strip() + " " + (self.last_name or "").strip()).rstrip()


class Profile(BaseModel):
    """
    This model is used to store user profile information
    """

    MAX_FILE_SIZE_ALLOWED = 5  # MB
    EXTENSIONS_ALLOWED = ("jpeg", "png", "jpg")

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(
        storage=FILE_STORAGE,
        upload_to=RenameFile("files/profiles/{instance.user_id}/photo.{extension}"),
        validators=[
            ValidateFileSize(max_file_size=MAX_FILE_SIZE_ALLOWED),
            FileExtensionValidator(allowed_extensions=EXTENSIONS_ALLOWED),
        ],
        null=True,
        blank=True,
    )
    phone_number = PhoneNumberField()

    def __str__(self):
        return f"{self.user.email}'s Profile"

    def clean(self) -> None:
        return super().clean()

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"


class UserRole(BaseModel):
    """
    This model is used to store roles against a user
    """

    class Role(models.IntegerChoices):
        MANAGER = 1
        STAFF_MEMBER = 2

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    role = models.PositiveSmallIntegerField(choices=Role.choices)

    class Meta:
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "role"], name="user_role_unique_constraint"
            )
        ]
