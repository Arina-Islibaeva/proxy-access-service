from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Менеджер модели пользователя."""

    def create_user(self, email, password=None, **extra_fields):
        """Создает обычного пользователя с email и паролем."""
        if not email:
            raise ValueError("Email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создает суперпользователя с правами администратора."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)
