"""Модель пользователя с ролями администратора и обычного участника."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользователь системы бронирования мастер-классов."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Администратор"
        USER = "user", "Пользователь"

    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        default=Role.USER,
        help_text="Роль определяет права: CRUD мастер-классов доступен только admin.",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def is_admin_role(self) -> bool:
        """Возвращает True, если пользователь имеет роль администратора."""
        return self.role == self.Role.ADMIN

    def save(self, *args, **kwargs):
        """Синхронизирует роль с флагами Django Admin."""
        if self.is_admin_role():
            self.is_staff = True
        super().save(*args, **kwargs)
