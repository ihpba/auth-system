"""
Кастомный класс аутентификации DRF на основе JWT.

Не использует встроенные TokenAuthentication или SessionAuthentication
Django/DRF — полностью собственная реализация.
"""

import logging

import jwt as pyjwt

from rest_framework import authentication, exceptions

from accounts.jwt_utils import decode_token
from accounts.models import CustomUser

logger = logging.getLogger(__name__)


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Аутентификация по JWT-токену, переданному в заголовке
    Authorization: Bearer <token>.

    Возвращает кортеж (user, token_payload) при успехе
    или None, если заголовок отсутствует (чтобы дать шанс
    другим authentication-классам).
    """

    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != self.keyword.lower():
            return None

        token = parts[1]
        return self._authenticate_token(token)

    def _authenticate_token(self, token: str):
        """
        Декодирует токен, проверяет тип и состояние пользователя.
        """
        try:
            payload = decode_token(token)
        except pyjwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Срок действия токена истёк.")
        except pyjwt.InvalidTokenError as exc:
            raise exceptions.AuthenticationFailed(f"Недействительный токен: {exc}")

        # Проверяем, что это access-токен (не refresh)
        if payload.get("type") != "access":
            raise exceptions.AuthenticationFailed(
                "Для аутентификации необходим access-токен."
            )

        user_id = payload.get("sub")
        if not user_id:
            raise exceptions.AuthenticationFailed("В токене отсутствует идентификатор пользователя.")

        try:
            user = CustomUser.objects.get(id=user_id, is_active=True)
        except CustomUser.DoesNotExist:
            raise exceptions.AuthenticationFailed("Пользователь не найден или деактивирован.")

        return (user, payload)

    def authenticate_header(self, request):
        """Заголовок WWW-Authenticate для ответа 401."""
        return self.keyword
