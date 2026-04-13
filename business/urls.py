"""
URL-маршруты модуля business — Mock-Views бизнес-объектов.
"""

from django.urls import path, include
from rest_framework.routers import SimpleRouter

from business.views import DocumentViewSet, ReportViewSet, TaskViewSet

router = SimpleRouter()
router.register("documents", DocumentViewSet, basename="business-documents")
router.register("reports", ReportViewSet, basename="business-reports")
router.register("tasks", TaskViewSet, basename="business-tasks")

urlpatterns = [
    path("", include(router.urls)),
]
