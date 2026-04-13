"""
Представления модуля RBAC — управление ролями, разрешениями и назначениями.

Все эндпоинты доступны только пользователям с ролью «admin».
Для проверки используется специальный класс IsAdmin.
"""

from rest_framework import generics, status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import CustomUser
from rbac.models import Resource, Action, Role, Permission, UserRole
from rbac.serializers import (
    ResourceSerializer,
    ActionSerializer,
    RoleSerializer,
    PermissionSerializer,
    PermissionCreateSerializer,
    UserRoleSerializer,
    UserRoleCreateSerializer,
    UserPermissionsSummarySerializer,
)


class IsAdmin(BasePermission):
    """
    Проверяет, что пользователь имеет роль «admin».
    Используется для ограничения доступа к API управления RBAC.
    """

    def has_permission(self, request, view):
        if not request.user or not getattr(request.user, "is_authenticated", False):
            return False
        return UserRole.objects.filter(
            user=request.user, role__codename="admin"
        ).exists()


# ── Ресурсы ─────────────────────────────────────────────────────


class ResourceListView(generics.ListCreateAPIView):
    """
    GET  /api/rbac/resources/   — список ресурсов.
    POST /api/rbac/resources/   — создание ресурса.
    """

    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAdmin]


class ResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/rbac/resources/<id>/ — детали ресурса.
    PATCH  /api/rbac/resources/<id>/ — обновление.
    DELETE /api/rbac/resources/<id>/ — удаление.
    """

    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAdmin]


# ── Действия ────────────────────────────────────────────────────


class ActionListView(generics.ListCreateAPIView):
    """
    GET  /api/rbac/actions/   — список действий.
    POST /api/rbac/actions/   — создание действия.
    """

    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = [IsAdmin]


class ActionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = [IsAdmin]


# ── Роли ────────────────────────────────────────────────────────


class RoleListView(generics.ListCreateAPIView):
    """
    GET  /api/rbac/roles/   — список ролей.
    POST /api/rbac/roles/   — создание роли.
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin]


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin]


# ── Разрешения ──────────────────────────────────────────────────


class PermissionListView(generics.ListCreateAPIView):
    """
    GET  /api/rbac/permissions/   — список всех разрешений.
    POST /api/rbac/permissions/   — создание разрешения по кодовым именам.
    """

    queryset = Permission.objects.select_related("role", "resource", "action").all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PermissionCreateSerializer
        return PermissionSerializer

    def create(self, request, *args, **kwargs):
        serializer = PermissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        permission = serializer.save()
        return Response(
            PermissionSerializer(permission).data,
            status=status.HTTP_201_CREATED,
        )


class PermissionDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/rbac/permissions/<id>/ — детали разрешения.
    DELETE /api/rbac/permissions/<id>/ — удаление разрешения.
    """

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAdmin]


# ── Назначения ролей ────────────────────────────────────────────


class UserRoleListView(generics.ListCreateAPIView):
    """
    GET  /api/rbac/user-roles/   — список всех назначений.
    POST /api/rbac/user-roles/   — назначить роль пользователю.
    """

    queryset = UserRole.objects.select_related("user", "role").all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserRoleCreateSerializer
        return UserRoleSerializer

    def create(self, request, *args, **kwargs):
        serializer = UserRoleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_role = serializer.save()
        return Response(
            UserRoleSerializer(user_role).data,
            status=status.HTTP_201_CREATED,
        )


class UserRoleDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/rbac/user-roles/<id>/ — детали назначения.
    DELETE /api/rbac/user-roles/<id>/ — снять роль с пользователя.
    """

    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAdmin]


# ── Сводка разрешений пользователя ──────────────────────────────


class UserPermissionsView(APIView):
    """
    GET /api/rbac/users/<user_id>/permissions/ — все разрешения пользователя.

    Возвращает список ролей и полный набор разрешений
    (объединение разрешений всех ролей).
    """

    permission_classes = [IsAdmin]

    def get(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_roles = UserRole.objects.filter(user=user).select_related("role")
        roles = [ur.role.codename for ur in user_roles]
        role_ids = [ur.role_id for ur in user_roles]

        perms = (
            Permission.objects.filter(role_id__in=role_ids)
            .select_related("resource", "action")
            .values_list("resource__codename", "action__codename")
        )
        permissions_list = [f"{res}:{act}" for res, act in perms]

        return Response(
            UserPermissionsSummarySerializer(
                {
                    "user_email": user.email,
                    "roles": roles,
                    "permissions": permissions_list,
                }
            ).data
        )
