"""Бизнес-логика бронирования: вместимость, прошедшие даты, дубликаты."""

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from bookings.models import Booking
from workshops.models import Workshop


def get_user_bookings(user):
    """
    Брони текущего пользователя.

    select_related подгружает мастер-класс одним JOIN и устраняет N+1.
    """
    return (
        Booking.objects.filter(user=user)
        .select_related("workshop", "workshop__created_by", "user")
    )


def create_booking(*, user, workshop_id: int) -> Booking:
    """
    Создаёт бронь, если есть места, дата не прошла и повтор запрещён.

    select_for_update блокирует строку мастер-класса на время транзакции,
    чтобы два параллельных запроса не превысили вместимость.
    """
    with transaction.atomic():
        try:
            workshop = Workshop.objects.select_for_update().get(pk=workshop_id)
        except Workshop.DoesNotExist as exc:
            raise ValidationError({"workshop_id": "Мастер-класс не найден."}) from exc

        if workshop.starts_at <= timezone.now():
            raise ValidationError(
                {"workshop_id": "Нельзя записаться на прошедший мастер-класс."}
            )

        occupied = workshop.bookings.count()
        if occupied >= workshop.capacity:
            raise ValidationError(
                {"workshop_id": "Свободных мест нет, вместимость исчерпана."}
            )

        if Booking.objects.filter(user=user, workshop=workshop).exists():
            raise ValidationError(
                {"workshop_id": "Вы уже записаны на этот мастер-класс."}
            )

        try:
            booking = Booking.objects.create(user=user, workshop=workshop)
        except IntegrityError as exc:
            raise ValidationError(
                {"workshop_id": "Вы уже записаны на этот мастер-класс."}
            ) from exc

    return (
        Booking.objects.select_related("workshop", "workshop__created_by", "user")
        .get(pk=booking.pk)
    )


def cancel_booking(*, booking: Booking, user) -> None:
    """Отменяет бронь, если она принадлежит текущему пользователю."""
    if booking.user_id != user.id and not user.is_admin_role():
        raise ValidationError("Нельзя отменить чужое бронирование.")
    booking.delete()
