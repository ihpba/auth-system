"""
Тесты модуля RBAC: проверка прав доступа, 401/403, admin API.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import CustomUser
from accounts.jwt_utils import generate_access_token, generate_refresh_token
from rbac.models import Resource, Action, Role, Permission, UserRole


class RBACPermissionTest(TestCase):
    """
    Проверка системы разграничения прав:
        - 401 при отсутствии аутентификации
        - 403 при отсутствии прав
        - 200 при наличии прав
    """

    @classmethod
    def setUpTestData(cls):
        # Создаём ресурсы
        cls.res_docs = Resource.objects.create(codename="documents", name="Документы")
        cls.res_reports = Resource.objects.create(codename="reports", name="Отчёты")

        # Создаём действия
        cls.act_read = Action.objects.create(codename="read", name="Чтение")
        cls.act_create = Action.objects.create(codename="create", name="Создание")

        # Создаём роли
        cls.role_admin = Role.objects.create(codename="admin", name="Администратор")
        cls.role_viewer = Role.objects.create(codename="viewer", name="Читатель")

        # Назначаем разрешения
        Permission.objects.create(role=cls.role_admin, resource=cls.res_docs, action=cls.act_read)
        Permission.objects.create(role=cls.role_admin, resource=cls.res_docs, action=cls.act_create)
        Permission.objects.create(role=cls.role_admin, resource=cls.res_reports, action=cls.act_read)
        Permission.objects.create(role=cls.role_viewer, resource=cls.res_docs, action=cls.act_read)

        # Создаём пользователей
        cls.admin_user = CustomUser.objects.create_user(
            email="admin@test.com", password="TestPass123!",
        )
        cls.viewer_user = CustomUser.objects.create_user(
            email="viewer@test.com", password="TestPass123!",
        )
        cls.guest_user = CustomUser.objects.create_user(
            email="guest@test.com", password="TestPass123!",
        )

        # Назначаем роли
        UserRole.objects.create(user=cls.admin_user, role=cls.role_admin)
        UserRole.objects.create(user=cls.viewer_user, role=cls.role_viewer)

    def test_unauthenticated_gets_401(self):
        """Неаутентифицированный запрос — 401."""
        client = APIClient()
        response = client.get("/api/business/documents/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_read_documents(self):
        """Админ может читать документы — 200."""
        client = APIClient()
        access = generate_access_token(self.admin_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = client.get("/api/business/documents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_create_documents(self):
        """Админ может создавать документы — 201."""
        client = APIClient()
        access = generate_access_token(self.admin_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = client.post("/api/business/documents/", {"title": "New"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_viewer_can_read_documents(self):
        """Читатель может читать документы — 200."""
        client = APIClient()
        access = generate_access_token(self.viewer_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = client.get("/api/business/documents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_viewer_cannot_create_documents(self):
        """Читатель НЕ может создавать документы — 403."""
        client = APIClient()
        access = generate_access_token(self.viewer_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = client.post("/api/business/documents/", {"title": "Hack"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_guest_cannot_read_documents(self):
        """Гость без ролей не может читать документы — 403."""
        client = APIClient()
        access = generate_access_token(self.guest_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = client.get("/api/business/documents/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_read_reports_without_permission(self):
        """Читатель не имеет прав на reports:read — 403."""
        client = APIClient()
        access = generate_access_token(self.viewer_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = client.get("/api/business/reports/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminRBACAPITest(TestCase):
    """Тесты admin-API для управления правилами RBAC."""

    @classmethod
    def setUpTestData(cls):
        cls.role_admin = Role.objects.create(codename="admin", name="Администратор")
        cls.admin_user = CustomUser.objects.create_user(
            email="adm@api.com", password="TestPass123!"
        )
        UserRole.objects.create(user=cls.admin_user, role=cls.role_admin)

    def setUp(self):
        self.client = APIClient()
        self.access = generate_access_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_admin_can_list_roles(self):
        """Админ может просматривать список ролей."""
        response = self.client.get("/api/rbac/roles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_create_role(self):
        """Админ может создавать новую роль."""
        response = self.client.post("/api/rbac/roles/", {
            "codename": "moderator",
            "name": "Модератор",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_create_resource(self):
        """Админ может создавать ресурс."""
        response = self.client.post("/api/rbac/resources/", {
            "codename": "analytics",
            "name": "Аналитика",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_create_permission(self):
        """Админ может создавать разрешение."""
        res = Resource.objects.create(codename="test_res", name="Тест")
        act = Action.objects.create(codename="test_act", name="ТестДействие")
        response = self.client.post("/api/rbac/permissions/", {
            "role_codename": "admin",
            "resource_codename": "test_res",
            "action_codename": "test_act",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_assign_role(self):
        """Админ может назначить роль пользователю."""
        new_user = CustomUser.objects.create_user(
            email="new@api.com", password="TestPass123!"
        )
        response = self.client.post("/api/rbac/user-roles/", {
            "user_email": "new@api.com",
            "role_codename": "admin",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_admin_cannot_access_rbac_api(self):
        """Не-админ получает 403 на RBAC API."""
        viewer = CustomUser.objects.create_user(
            email="notadmin@api.com", password="TestPass123!"
        )
        role_viewer = Role.objects.create(codename="viewer2", name="Читатель2")
        UserRole.objects.create(user=viewer, role=role_viewer)
        access = generate_access_token(viewer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.get("/api/rbac/roles/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_rbac_api(self):
        """Неаутентифицированный получает 401 на RBAC API."""
        self.client.credentials()
        response = self.client.get("/api/rbac/roles/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_view_user_permissions(self):
        """Админ может просмотреть сводку разрешений пользователя."""
        response = self.client.get(f"/api/rbac/users/{self.admin_user.id}/permissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("admin", response.data["roles"])
