"""Модель мастер-класса и ограничения вместимости."""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Workshop(models.Model):
    """Мастер-класс, на который можно записаться."""

    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    starts_at = models.DateTimeField(verbose_name="Дата и время начала")
    duration_minutes = models.PositiveIntegerField(
        default=90,
        validators=[MinValueValidator(1)],
        verbose_name="Длительность (мин)",
    )
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Вместимость",
        help_text="Максимальное число участников.",
    )
    location = models.CharField(max_length=255, verbose_name="Место проведения")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_workshops",
        verbose_name="Создатель",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["starts_at"]
        verbose_name = "Мастер-класс"
        verbose_name_plural = "Мастер-классы"

    def __str__(self) -> str:
        return self.title

    def booked_count(self) -> int:
        """Количество активных броней (используется, если нет аннотации)."""
        if hasattr(self, "bookings_count"):
            return self.bookings_count
        return self.bookings.count()

    def remaining_seats(self) -> int:
        """Свободные места с учётом уже созданных броней."""
        return max(self.capacity - self.booked_count(), 0)
