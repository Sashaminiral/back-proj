"""Сервисный слой мастер-классов: CRUD и подготовка queryset."""

from django.db.models import Count, QuerySet

from workshops.models import Workshop


def get_workshop_queryset() -> QuerySet[Workshop]:
    """
    Возвращает queryset с подсчётом броней одним запросом.

    Count через annotate убирает N+1 при выводе списка и деталей.
    """
    return (
        Workshop.objects.select_related("created_by")
        .annotate(bookings_count=Count("bookings"))
        .order_by("starts_at")
    )


def create_workshop(*, data: dict, creator) -> Workshop:
    """Создаёт мастер-класс от имени администратора."""
    return Workshop.objects.create(**data, created_by=creator)


def update_workshop(*, workshop: Workshop, data: dict) -> Workshop:
    """Обновляет поля мастер-класса и сохраняет объект."""
    for field, value in data.items():
        setattr(workshop, field, value)
    workshop.save()
    return workshop


def delete_workshop(*, workshop: Workshop) -> None:
    """Удаляет мастер-класс вместе со связанными бронями (CASCADE)."""
    workshop.delete()
