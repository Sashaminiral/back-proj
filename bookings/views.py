"""Контроллеры бронирований: создание, просмотр своих записей, отмена."""

from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bookings.serializers import BookingSerializer
from bookings.services import cancel_booking, create_booking, get_user_bookings


class BookingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    POST — создать бронь.
    GET — только свои бронирования.
    DELETE — отменить свою бронь.
    """

    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        """Пользователь видит только свои записи."""
        return get_user_bookings(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = create_booking(
            user=request.user,
            workshop_id=serializer.validated_data["workshop_id"],
        )
        return Response(
            self.get_serializer(booking).data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        cancel_booking(booking=self.get_object(), user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
