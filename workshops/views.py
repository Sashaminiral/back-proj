"""Контроллеры REST API мастер-классов."""

from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.permissions import IsAdminRole
from workshops.serializers import WorkshopSerializer
from workshops.services import (
    create_workshop,
    delete_workshop,
    get_workshop_queryset,
    update_workshop,
)


class WorkshopViewSet(viewsets.ModelViewSet):
    """
    GET — публичный просмотр списка и деталей.
    POST/PUT/PATCH/DELETE — только роль администратора.
    """

    serializer_class = WorkshopSerializer
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return get_workshop_queryset()

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminRole()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        workshop = create_workshop(
            data=serializer.validated_data,
            creator=request.user,
        )
        output = self.get_serializer(get_workshop_queryset().get(pk=workshop.pk))
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        workshop = self.get_object()
        serializer = self.get_serializer(workshop, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        update_workshop(workshop=workshop, data=serializer.validated_data)
        output = self.get_serializer(get_workshop_queryset().get(pk=workshop.pk))
        return Response(output.data)

    def destroy(self, request, *args, **kwargs):
        delete_workshop(workshop=self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)
