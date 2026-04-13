"""
URL-маршруты модуля RBAC.
"""

from django.urls import path

from rbac.views import (
    ResourceListView,
    ResourceDetailView,
    ActionListView,
    ActionDetailView,
    RoleListView,
    RoleDetailView,
    PermissionListView,
    PermissionDetailView,
    UserRoleListView,
    UserRoleDetailView,
    UserPermissionsView,
)

urlpatterns = [
    # Ресурсы
    path("resources/", ResourceListView.as_view(), name="rbac-resource-list"),
    path("resources/<uuid:pk>/", ResourceDetailView.as_view(), name="rbac-resource-detail"),
    # Действия
    path("actions/", ActionListView.as_view(), name="rbac-action-list"),
    path("actions/<uuid:pk>/", ActionDetailView.as_view(), name="rbac-action-detail"),
    # Роли
    path("roles/", RoleListView.as_view(), name="rbac-role-list"),
    path("roles/<uuid:pk>/", RoleDetailView.as_view(), name="rbac-role-detail"),
    # Разрешения
    path("permissions/", PermissionListView.as_view(), name="rbac-permission-list"),
    path("permissions/<uuid:pk>/", PermissionDetailView.as_view(), name="rbac-permission-detail"),
    # Назначения ролей
    path("user-roles/", UserRoleListView.as_view(), name="rbac-userrole-list"),
    path("user-roles/<uuid:pk>/", UserRoleDetailView.as_view(), name="rbac-userrole-detail"),
    # Сводка разрешений пользователя
    path("users/<uuid:user_id>/permissions/", UserPermissionsView.as_view(), name="rbac-user-permissions"),
]
