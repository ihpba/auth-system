"""
Кастомный обработчик исключений DRF.

Формирует единообразный JSON-ответ при ошибках аутентификации
и авторизации:
    - 401 Unauthorized — пользователь не определён.
    - 403 Forbidden     — пользователь определён, но доступ запрещён.
    - 400 Bad Request   — ошибка валидации (сохраняет структуру полей).
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Обработчик, который приводит ответы к формату:

    Для 401/403/404/405:
        {"detail": "<сообщение>", "code": "<код>"}

    Для 400 (ValidationError):
        сохраняет оригинальную структуру ошибок по полям:
        {"field_name": ["ошибка1", ...], ...}
    """
    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            if isinstance(response.data, dict):
                result = {}
                for key, value in response.data.items():
                    if isinstance(value, list):
                        result[key] = [str(v) for v in value]
                    else:
                        result[key] = str(value)
                response.data = result
            elif isinstance(response.data, list):
                response.data = {"detail": [str(v) for v in response.data]}
        elif isinstance(response.data, dict) and "detail" in response.data:
            detail = response.data["detail"]
            response.data = {
                "detail": str(detail),
                "code": _status_to_code(response.status_code),
            }
        elif isinstance(response.data, dict):
            pass  # оставляем как есть (например, ошибки по полям)
        else:
            response.data = {
                "detail": str(exc),
                "code": _status_to_code(response.status_code),
            }
    else:
        response = Response(
            {"detail": "Внутренняя ошибка сервера.", "code": "server_error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def _status_to_code(status_code: int) -> str:
    mapping = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        422: "validation_error",
    }
    return mapping.get(status_code, f"error_{status_code}")
