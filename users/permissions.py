"""Права доступа на основе роли пользователя."""

from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Разрешает действие только пользователям с ролью admin."""

    message = "Действие доступно только администратору."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "is_admin_role", lambda: False)()
        )
