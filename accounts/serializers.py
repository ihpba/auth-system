"""
Сериализаторы для модуля accounts.

Отвечают за валидацию входных данных и форматирование ответов.
"""

from rest_framework import serializers

from accounts.models import CustomUser


class RegisterSerializer(serializers.Serializer):
    """
    Валидация данных при регистрации нового пользователя.

    Проверяет:
        - совпадение паролей;
        - уникальность email;
        - минимальную длину пароля.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    password_confirm = serializers.CharField(write_only=True, min_length=8, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    patronymic = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value.lower()

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают."})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        raw_password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(raw_password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Валидация данных при входе в систему."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class ChangePasswordSerializer(serializers.Serializer):
    """Валидация смены пароля."""

    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, min_length=8, required=True)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8, required=True)

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "Пароли не совпадают."})
        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения/обновления профиля пользователя."""

    class Meta:
        model = CustomUser
        fields = ("id", "email", "first_name", "last_name", "patronymic", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "email", "is_active", "created_at", "updated_at")


class TokenResponseSerializer(serializers.Serializer):
    """Формат ответа с парой токенов."""

    access = serializers.CharField()
    refresh = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    """Валидация refresh-токена."""

    refresh = serializers.CharField(required=True)
