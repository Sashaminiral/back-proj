"""Модель бронирования: связь пользователя и мастер-класса без повторов."""

from django.conf import settings
from django.db import models


class Booking(models.Model):
    """Запись пользователя на конкретный мастер-класс."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Участник",
    )
    workshop = models.ForeignKey(
        "workshops.Workshop",
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Мастер-класс",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "workshop"],
                name="unique_user_workshop_booking",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} → {self.workshop}"
