"""Сериализация броней: вложенные данные мастер-класса, без паролей."""

from rest_framework import serializers

from bookings.models import Booking
from users.serializers import UserSerializer
from workshops.serializers import WorkshopSerializer


class BookingSerializer(serializers.ModelSerializer):
    """Ответ API: бронь + данные мастер-класса и участника."""

    workshop = WorkshopSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    workshop_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Booking
        fields = ("id", "user", "workshop", "workshop_id", "created_at")
        read_only_fields = ("id", "user", "workshop", "created_at")
