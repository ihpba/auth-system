"""
Модели системы разграничения прав доступа (RBAC — Role-Based Access Control).

Архитектура:
    Пользователь ←── UserRole ──→ Роль ←── Permission ──→ (Ресурс + Действие)

    - Resource  (Ресурс)     — объект бизнес-логики (например, «документы», «отчёты»).
    - Action    (Действие)   — тип операции над ресурсом (create, read, update, delete).
    - Role      (Роль)       — именованный набор разрешений (например, «администратор», «редактор»).
    - Permission(Разрешение) — связка «ресурс + действие», назначаемая роли.
    - UserRole   (Связка)    — назначение роли конкретному пользователю.

Правила проверки доступа:
    1. Если пользователь не аутентифицирован — 401 Unauthorized.
    2. Если пользователь аутентифицирован, но у его ролей нет разрешения
       на запрошенный (ресурс, действие) — 403 Forbidden.
    3. Если разрешение найдено — доступ разрешён.
"""

import uuid

from django.db import models

from accounts.models import CustomUser


class Resource(models.Model):
    """
    Ресурс — логический объект бизнес-приложения,
    к которому регулируется доступ.

    Примеры значений: «documents», «reports», «tasks», «users».
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codename = models.SlugField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Кодовое имя ресурса",
        help_text="Уникальный идентификатор ресурса в нижнем регистре (например, «documents»).",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Человекочитаемое название",
        help_text="Например, «Документы».",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Описание ресурса",
    )

    class Meta:
        db_table = "rbac_resource"
        verbose_name = "Ресурс"
        verbose_name_plural = "Ресурсы"
        ordering = ["codename"]

    def __str__(self) -> str:
        return f"{self.codename} ({self.name})"


class Action(models.Model):
    """
    Действие — тип операции, которую можно совершить над ресурсом.

    Стандартные значения: create, read, update, delete.
    Можно расширять пользовательскими действиями (например, «approve», «export»).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codename = models.SlugField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Кодовое имя действия",
        help_text="Уникальный идентификатор (например, «create»).",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Человекочитаемое название",
        help_text="Например, «Создание».",
    )

    class Meta:
        db_table = "rbac_action"
        verbose_name = "Действие"
        verbose_name_plural = "Действия"
        ordering = ["codename"]

    def __str__(self) -> str:
        return f"{self.codename} ({self.name})"


class Role(models.Model):
    """
    Роль — именованный набор разрешений.

    Примеры: «admin», «editor», «viewer».
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codename = models.SlugField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Кодовое имя роли",
        help_text="Уникальный идентификатор роли (например, «admin»).",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Человекочитаемое название",
        help_text="Например, «Администратор».",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Описание роли",
    )

    class Meta:
        db_table = "rbac_role"
        verbose_name = "Роль"
        verbose_name_plural = "Роли"
        ordering = ["codename"]

    def __str__(self) -> str:
        return f"{self.codename} ({self.name})"


class Permission(models.Model):
    """
    Разрешение — связка «роль + ресурс + действие».

    Определяет, что пользователь с данной ролью может совершить
    указанное действие над указанным ресурсом.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="permissions",
        verbose_name="Роль",
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="permissions",
        verbose_name="Ресурс",
    )
    action = models.ForeignKey(
        Action,
        on_delete=models.CASCADE,
        related_name="permissions",
        verbose_name="Действие",
    )

    class Meta:
        db_table = "rbac_permission"
        verbose_name = "Разрешение"
        verbose_name_plural = "Разрешения"
        unique_together = [("role", "resource", "action")]
        ordering = ["role", "resource", "action"]

    def __str__(self) -> str:
        return f"{self.role.codename} → {self.action.codename} → {self.resource.codename}"


class UserRole(models.Model):
    """
    Назначение роли пользователю.

    Пользователь может иметь несколько ролей.
    Итоговый набор разрешений — объединение разрешений всех ролей.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name="Пользователь",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name="Роль",
    )

    class Meta:
        db_table = "rbac_user_role"
        verbose_name = "Назначение роли"
        verbose_name_plural = "Назначения ролей"
        unique_together = [("user", "role")]
        ordering = ["user", "role"]

    def __str__(self) -> str:
        return f"{self.user.email} → {self.role.codename}"
