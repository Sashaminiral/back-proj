"""Сериализаторы регистрации, входа и профиля. Пароли и хеши не отдаются в API."""

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Публичное представление пользователя без секретных полей."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role")
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    """Валидация данных при регистрации нового пользователя."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name")

    def create(self, validated_data):
        """Создаёт пользователя с хешированным паролем и ролью user."""
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.role = User.Role.USER
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Проверка учётных данных при входе."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Аутентифицирует пользователя или возвращает ошибку."""
        user = authenticate(
            username=attrs.get("username"),
            password=attrs.get("password"),
        )
        if user is None:
            raise serializers.ValidationError("Неверный логин или пароль.")
        if not user.is_active:
            raise serializers.ValidationError("Учётная запись отключена.")
        attrs["user"] = user
        return attrs
