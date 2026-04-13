"""
Middleware для JWT-аутентификации.

Подмена request.user на основе JWT из заголовка Authorization.
Используется дополнительно к DRF-аутентификации, чтобы
request.user был доступен в обычных Django-views и middleware.
"""

import logging

from django.utils.deprecation import MiddlewareMixin

from accounts.authentication import JWTAuthentication
from accounts.models import CustomUser

logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Промежуточный слой, который извлекает пользователя из JWT
    и помещает его в request.user.

    Не выбрасывает исключения — если токен отсутствует или невалиден,
    request.user остаётся AnonymousUser (аналог).
    """

    def process_request(self, request):
        request.user = None

        auth = JWTAuthentication()
        try:
            result = auth.authenticate(request)
            if result is not None:
                request.user, _ = result
        except Exception:
            pass

        if request.user is None:
            request.user = AnonymousUser()


class AnonymousUser:
    """Заглушка неаутентифицированного пользователя."""

    is_active = False
    is_authenticated = False

    def __str__(self):
        return "AnonymousUser"
