from django.test import TestCase

from users.models import User


class UserRoleTests(TestCase):
    """Проверяет роли и отсутствие пароля в строковом представлении."""

    def test_admin_role_flag(self):
        user = User.objects.create_user(
            username="chief",
            password="ChiefPass123",
            role=User.Role.ADMIN,
        )
        self.assertTrue(user.is_admin_role())
        self.assertTrue(user.is_staff)
