from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from users.models import User
from workshops.models import Workshop
from workshops.services import get_workshop_queryset


class WorkshopQuerysetTests(TestCase):
    """Проверяет аннотацию числа броней без N+1."""

    def test_annotate_bookings_count(self):
        admin = User.objects.create_user(
            username="admin",
            password="AdminPass123",
            role=User.Role.ADMIN,
        )
        Workshop.objects.create(
            title="Скетчинг",
            description="Город",
            starts_at=timezone.now() + timedelta(days=3),
            duration_minutes=90,
            capacity=10,
            location="Зал",
            created_by=admin,
        )
        workshop = get_workshop_queryset().get(title="Скетчинг")
        self.assertEqual(workshop.bookings_count, 0)
        self.assertEqual(workshop.remaining_seats(), 10)
