"""
Mock-Views бизнес-объектов.

Реализуют минимальные вымышленные объекты бизнес-приложения,
к которым применяется созданная система разграничения прав.

Бизнес-объекты (не создают реальных таблиц в БД):
    - Документы   (resource: «documents»)
    - Отчёты      (resource: «reports»)
    - Задачи      (resource: «tasks»)

Каждый ViewSet проверяет права через RBACPermission.
Если пользователь не аутентифицирован — 401.
Если аутентифицирован, но прав нет — 403.
Если права есть — возвращает mock-данные.
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rbac.permissions import RBACPermission


# ── Моковые данные ──────────────────────────────────────────────

MOCK_DOCUMENTS = [
    {"id": 1, "title": "Договор аренды №12", "status": "подписан"},
    {"id": 2, "title": "Приказ о премировании", "status": "черновик"},
    {"id": 3, "title": "Служебная записка IT-01", "status": "на согласовании"},
]

MOCK_REPORTS = [
    {"id": 1, "title": "Финансовый отчёт Q1-2026", "period": "Q1 2026"},
    {"id": 2, "title": "Отчёт по продажам", "period": "Март 2026"},
]

MOCK_TASKS = [
    {"id": 1, "title": "Настроить CI/CD", "assignee": "Иванов И.И.", "status": "в работе"},
    {"id": 2, "title": "Обновить документацию", "assignee": "Петров П.П.", "status": "новая"},
    {"id": 3, "title": "Провести код-ревью", "assignee": "Сидоров С.С.", "status": "выполнена"},
]


# ── ViewSet с поддержкой RBAC ───────────────────────────────────


class BusinessViewSetMixin:
    """
    Общий миксин для бизнес-ViewSet'ов.

    Атрибуты:
        rbac_resource     — кодовое имя ресурса (например, «documents»).
        mock_data         — список моковых данных.
        rbac_action_map   — отображение HTTP-методов в действия RBAC.
    """

    mock_data = []

    rbac_action_map = {
        "get": "read",
        "post": "create",
        "patch": "update",
        "put": "update",
        "delete": "delete",
    }

    def list(self, request):
        return Response(self.mock_data)

    def retrieve(self, request, pk=None):
        item = next((x for x in self.mock_data if x["id"] == pk), None)
        if item is None:
            return Response({"detail": "Объект не найден."}, status=status.HTTP_404_NOT_FOUND)
        return Response(item)

    def create(self, request):
        return Response(
            {"detail": "Объект создан (mock).", "data": request.data},
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, pk=None):
        item = next((x for x in self.mock_data if x["id"] == pk), None)
        if item is None:
            return Response({"detail": "Объект не найден."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "Объект обновлён (mock).", "data": request.data})

    def destroy(self, request, pk=None):
        return Response({"detail": "Объект удалён (mock)."}, status=status.HTTP_204_NO_CONTENT)


class DocumentViewSet(BusinessViewSetMixin, viewsets.ViewSet):
    """
    Документы — бизнес-объект с проверкой прав по ресурсу «documents».
    """

    rbac_resource = "documents"
    mock_data = MOCK_DOCUMENTS
    permission_classes = [IsAuthenticated, RBACPermission]


class ReportViewSet(BusinessViewSetMixin, viewsets.ViewSet):
    """
    Отчёты — бизнес-объект с проверкой прав по ресурсу «reports».
    """

    rbac_resource = "reports"
    mock_data = MOCK_REPORTS
    permission_classes = [IsAuthenticated, RBACPermission]


class TaskViewSet(BusinessViewSetMixin, viewsets.ViewSet):
    """
    Задачи — бизнес-объект с проверкой прав по ресурсу «tasks».
    """

    rbac_resource = "tasks"
    mock_data = MOCK_TASKS
    permission_classes = [IsAuthenticated, RBACPermission]
