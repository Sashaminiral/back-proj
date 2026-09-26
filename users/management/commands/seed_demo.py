"""Команда заполнения демо-данными для проверки API."""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import User
from workshops.models import Workshop


class Command(BaseCommand):
    help = "Создаёт администратора, участника и несколько мастер-классов."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Не спрашивать подтверждение (для Docker entrypoint).",
        )

    def handle(self, *args, **options):
        admin, created_admin = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created_admin:
            admin.set_password("AdminPass123")
            admin.save()

        user, created_user = User.objects.get_or_create(
            username="user",
            defaults={
                "email": "user@example.com",
                "role": User.Role.USER,
            },
        )
        if created_user:
            user.set_password("UserPass123")
            user.save()

        now = timezone.now()
        demos = [
            {
                "title": "Гончарное дело для начинающих",
                "description": "Лепка простой чашки и обжиг.",
                "starts_at": now + timedelta(days=7),
                "duration_minutes": 120,
                "capacity": 8,
                "location": "Студия на Невском, 12",
            },
            {
                "title": "Акварельный скетчинг",
                "description": "Городской пейзаж за два часа.",
                "starts_at": now + timedelta(days=14),
                "duration_minutes": 90,
                "capacity": 12,
                "location": "Мастерская «Свет»",
            },
            {
                "title": "Прошедший мастер-класс",
                "description": "Нужен для проверки валидации даты.",
                "starts_at": now - timedelta(days=2),
                "duration_minutes": 60,
                "capacity": 5,
                "location": "Архив",
            },
        ]

        for item in demos:
            Workshop.objects.get_or_create(
                title=item["title"],
                defaults={**item, "created_by": admin},
            )

        self.stdout.write(self.style.SUCCESS("Демо-данные готовы."))
        self.stdout.write("Админ: admin / AdminPass123")
        self.stdout.write("Пользователь: user / UserPass123")
