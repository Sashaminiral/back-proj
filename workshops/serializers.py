"""Сериализация мастер-классов. Пароли и служебные поля пользователя не отдаются."""

from rest_framework import serializers

from users.serializers import UserSerializer
from workshops.models import Workshop


class WorkshopSerializer(serializers.ModelSerializer):
    """Публичное представление мастер-класса со статистикой мест."""

    created_by = UserSerializer(read_only=True)
    booked_count = serializers.IntegerField(read_only=True)
    remaining_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = Workshop
        fields = (
            "id",
            "title",
            "description",
            "starts_at",
            "duration_minutes",
            "capacity",
            "location",
            "created_by",
            "booked_count",
            "remaining_seats",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_by",
            "booked_count",
            "remaining_seats",
            "created_at",
            "updated_at",
        )

    def to_representation(self, instance):
        """Добавляет вычисляемые поля вместимости в JSON-ответ."""
        data = super().to_representation(instance)
        data["booked_count"] = instance.booked_count()
        data["remaining_seats"] = instance.remaining_seats()
        return data
