"""API-тесты аутентификации, мастер-классов и бронирований."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from workshops.models import Workshop

User = get_user_model()


class WorkshopBookingAPITests(APITestCase):
    """Проверяет минимальную функциональность системы бронирования."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            password="AdminPass123",
            role=User.Role.ADMIN,
        )
        self.member = User.objects.create_user(
            username="user",
            password="UserPass123",
            role=User.Role.USER,
        )
        self.other = User.objects.create_user(
            username="other",
            password="OtherPass123",
            role=User.Role.USER,
        )
        self.future = Workshop.objects.create(
            title="Гончарное дело",
            description="Лепка",
            starts_at=timezone.now() + timedelta(days=5),
            duration_minutes=90,
            capacity=1,
            location="Студия",
            created_by=self.admin,
        )
        self.past = Workshop.objects.create(
            title="Прошедший",
            description="Архив",
            starts_at=timezone.now() - timedelta(days=1),
            duration_minutes=60,
            capacity=5,
            location="Архив",
            created_by=self.admin,
        )

    def _login(self, username: str, password: str) -> str:
        response = self.client.post(
            reverse("login"),
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["token"]

    def test_register_returns_token_without_password(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newbie",
                "email": "newbie@example.com",
                "password": "NewbiePass123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertNotIn("password", response.data["user"])

    def test_public_workshop_list_and_detail(self):
        list_response = self.client.get("/api/workshops/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(list_response.data["count"], 2)

        detail = self.client.get(f"/api/workshops/{self.future.id}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["title"], "Гончарное дело")
        self.assertIn("remaining_seats", detail.data)

    def test_user_cannot_create_workshop(self):
        token = self._login("user", "UserPass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.post(
            "/api/workshops/",
            {
                "title": "Запрещено",
                "description": "Нет",
                "starts_at": (timezone.now() + timedelta(days=10)).isoformat(),
                "duration_minutes": 60,
                "capacity": 4,
                "location": "Зал",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_workshop_crud(self):
        token = self._login("admin", "AdminPass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        created = self.client.post(
            "/api/workshops/",
            {
                "title": "Каллиграфия",
                "description": "Буквы",
                "starts_at": (timezone.now() + timedelta(days=20)).isoformat(),
                "duration_minutes": 90,
                "capacity": 6,
                "location": "Зал",
            },
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        workshop_id = created.data["id"]

        updated = self.client.put(
            f"/api/workshops/{workshop_id}/",
            {
                "title": "Каллиграфия",
                "description": "Буквы",
                "starts_at": created.data["starts_at"],
                "duration_minutes": 90,
                "capacity": 8,
                "location": "Зал",
            },
            format="json",
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data["capacity"], 8)

        deleted = self.client.delete(f"/api/workshops/{workshop_id}/")
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)

    def test_booking_requires_auth(self):
        response = self.client.post(
            "/api/bookings/",
            {"workshop_id": self.future.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_list_and_cancel_own_booking(self):
        token = self._login("user", "UserPass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        created = self.client.post(
            "/api/bookings/",
            {"workshop_id": self.future.id},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data["workshop"]["title"], "Гончарное дело")
        booking_id = created.data["id"]

        listed = self.client.get("/api/bookings/")
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(listed.data["count"], 1)

        duplicate = self.client.post(
            "/api/bookings/",
            {"workshop_id": self.future.id},
            format="json",
        )
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)

        cancelled = self.client.delete(f"/api/bookings/{booking_id}/")
        self.assertEqual(cancelled.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_book_past_workshop(self):
        token = self._login("user", "UserPass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.post(
            "/api/bookings/",
            {"workshop_id": self.past.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_capacity_limit_and_foreign_bookings_hidden(self):
        first_token = self._login("user", "UserPass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {first_token}")
        first = self.client.post(
            "/api/bookings/",
            {"workshop_id": self.future.id},
            format="json",
        )
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second_token = self._login("other", "OtherPass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {second_token}")
        overflow = self.client.post(
            "/api/bookings/",
            {"workshop_id": self.future.id},
            format="json",
        )
        self.assertEqual(overflow.status_code, status.HTTP_400_BAD_REQUEST)

        hidden = self.client.get(f"/api/bookings/{first.data['id']}/")
        self.assertEqual(hidden.status_code, status.HTTP_404_NOT_FOUND)
