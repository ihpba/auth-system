"""
Утилиты для генерации и валидации JWT-токенов.

Реализация полностью собственная — используются только библиотека PyJWT
и параметры из settings. Никаких готовых библиотек типа djangorestframework-simplejwt.
"""

import uuid
from datetime import datetime, timedelta, timezone as dt_tz

import jwt

from django.conf import settings


def _now() -> datetime:
    """Текущее время в UTC."""
    return datetime.now(dt_tz.utc)


def generate_access_token(user) -> str:
    """
    Генерирует access-токен (короткоживущий).

    Полезная нагрузка (payload):
        - sub  : str   — идентификатор пользователя (UUID).
        - email: str   — email пользователя.
        - type : str   — «access» (для различения типа токена).
        - iat  : int   — время выдачи (Unix timestamp).
        - exp  : int   — время истечения (Unix timestamp).
    """
    issued_at = _now()
    expires_at = issued_at + settings.JWT_ACCESS_LIFETIME
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "type": "access",
        "iat": issued_at,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def generate_refresh_token(user) -> tuple[str, datetime]:
    """
    Генерирует refresh-токен (долгоживущий) и сохраняет его в БД.

    Возвращает кортеж (token_string, expires_at).
    Токен хранится в таблице RefreshToken и может быть отозван при logout.
    """
    from accounts.models import RefreshToken

    issued_at = _now()
    expires_at = issued_at + settings.JWT_REFRESH_LIFETIME

    # Уникальный идентификатор токена для привязки к записи в БД
    jti = str(uuid.uuid4())

    payload = {
        "sub": str(user.id),
        "jti": jti,
        "type": "refresh",
        "iat": issued_at,
        "exp": expires_at,
    }
    token_str = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    RefreshToken.objects.create(
        user=user,
        token=token_str,
        expires_at=expires_at,
    )

    return token_str, expires_at


def decode_token(token: str) -> dict:
    """
    Декодирует и верифицирует JWT-токен.

    Выбрасывает:
        jwt.ExpiredSignatureError — если срок действия истёк.
        jwt.InvalidTokenError     — при любой другой ошибке валидации.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


def revoke_refresh_token(token_str: str) -> bool:
    """
    Отзывает refresh-токен (помечает is_revoked=True).

    Возвращает True, если токен найден и отозван; False — иначе.
    """
    from accounts.models import RefreshToken

    try:
        rt = RefreshToken.objects.get(token=token_str, is_revoked=False)
        rt.is_revoked = True
        rt.save(update_fields=["is_revoked"])
        return True
    except RefreshToken.DoesNotExist:
        return False
