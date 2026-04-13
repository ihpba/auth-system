"""
Класс разрешения (permission) DRF на основе RBAC.

Проверяет, имеет ли аутентифицированный пользователь разрешение
на запрошенный ресурс и действие. Используется в views через
параметр permission_classes.

Пример использования во ViewSet:
    permission_classes = [IsAuthenticated, RBACPermission]
    rbac_resource = "documents"
    rbac_action_map = {
        "list":   "read",
        "create": "create",
        "update": "update",
        "destroy":"delete",
    }
"""

from rest_framework import permissions

from rbac.models import UserRole, Permission


class RBACPermission(permissions.BasePermission):
    """
    Разрешение на основе RBAC.

    Алгоритм:
        1. Пользователь должен быть аутентифицирован (иначе 401 — обработает
           DRF на уровне IsAuthenticated).
        2. Из view извлекаются параметры rbac_resource и rbac_action_map.
        3. Определяется действие для текущего HTTP-метода.
        4. Проверяется наличие записи Permission,
           связывающей одну из ролей пользователя с (ресурс, действие).
        5. Если не найдено — 403 Forbidden.
    """

    message = "У вас нет прав на выполнение данного действия."

    def has_permission(self, request, view):
        if not request.user or not getattr(request.user, "is_authenticated", False):
            return False

        resource_codename = getattr(view, "rbac_resource", None)
        if resource_codename is None:
            return True

        action_map = getattr(view, "rbac_action_map", {})
        action_codename = action_map.get(request.method.lower())

        if action_codename is None:
            return False

        return _user_has_permission(request.user, resource_codename, action_codename)


def _user_has_permission(user, resource_codename: str, action_codename: str) -> bool:
    """
    Проверяет наличие разрешения у пользователя
    на (ресурс, действие) через его роли.
    """
    user_role_ids = UserRole.objects.filter(user=user).values_list("role_id", flat=True)

    return Permission.objects.filter(
        role_id__in=user_role_ids,
        resource__codename=resource_codename,
        action__codename=action_codename,
    ).exists()


def user_has_permission(user, resource_codename: str, action_codename: str) -> bool:
    """Публичный интерфейс для проверки прав (используется в business-views)."""
    return _user_has_permission(user, resource_codename, action_codename)
