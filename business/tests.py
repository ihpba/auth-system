"""
Тесты Mock-Views бизнес-объектов.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import CustomUser
from accounts.jwt_utils import generate_access_token
from rbac.models import Resource, Action, Role, Permission, UserRole


class BusinessMockViewTest(TestCase):
    """
    Проверка, что Mock-Views возвращают правильные данные
    и корректно обрабатывают ошибки 401/403.
    """

    @classmethod
    def setUpTestData(cls):
        # Ресурсы
        res_docs = Resource.objects.create(codename="documents", name="Документы")
        res_tasks = Resource.objects.create(codename="tasks", name="Задачи")

        # Действия
        act_read = Action.objects.create(codename="read", name="Чтение")
        act_create = Action.objects.create(codename="create", name="Создание")

        # Роль editor
        role_editor = Role.objects.create(codename="editor", name="Редактор")
        Permission.objects.create(role=role_editor, resource=res_docs, action=act_read)
        Permission.objects.create(role=role_editor, resource=res_docs, action=act_create)
        Permission.objects.create(role=role_editor, resource=res_tasks, action=act_read)

        # Пользователь-редактор
        cls.editor = CustomUser.objects.create_user(
            email="editor@biz.com", password="TestPass123!"
        )
        UserRole.objects.create(user=cls.editor, role=role_editor)

    def test_documents_list_returns_mock_data(self):
        """GET /api/business/documents/ возвращает моковые данные."""
        client = APIClient()
        access = generate_access_token(self.editor)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = client.get("/api/business/documents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_documents_create_mock(self):
        """POST /api/business/documents/ — моковое создание."""
        client = APIClient()
        access = generate_access_token(self.editor)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = client.post("/api/business/documents/", {"title": "Новый"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_tasks_list_allowed_for_editor(self):
        """Редактор может читать задачи."""
        client = APIClient()
        access = generate_access_token(self.editor)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = client.get("/api/business/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tasks_create_forbidden_for_editor(self):
        """Редактор НЕ может создавать задачи — 403."""
        client = APIClient()
        access = generate_access_token(self.editor)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = client.post("/api/business/tasks/", {"title": "Hack"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
