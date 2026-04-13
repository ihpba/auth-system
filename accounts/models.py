"""
Кастомная модель пользователя.

Не наследуется от AbstractBaseUser / AbstractUser — реализация полностью
собственная, без привязки к встроенной системе аутентификации Django.
Хеширование паролей выполняется утилитами Django (make_password / check_password).
"""

import uuid

from django.db import models
from django.db.models.manager import Manager
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password


class CustomUserManager(Manager):
    """
    Кастомный менеджер для CustomUser.
    Предоставляет метод create_user для удобного создания
    пользователей с автоматическим хешированием пароля.
    """

    def create_user(self, email: str, password: str, **extra_fields):
        """Создаёт пользователя с хешированным паролем."""
        if not email:
            raise ValueError("Email обязателен.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def normalize_email(self, email: str) -> str:
        """Нормализация email (приведение домена к нижнему регистру)."""
        return email.lower()


class CustomUser(models.Model):
    """
    Основная модель пользователя.

    Поля:
        id          — UUID для исключения перебора идентификаторов.
        email       — уникальный логин.
        password     — хеш пароля (никогда не хранится в открытом виде).
        first_name  — имя.
        last_name   — фамилия.
        patronymic  — отчество (необязательно).
        is_active   — флаг «мягкого удаления»; False = аккаунт деактивирован.
        created_at  — дата-время создания записи.
        updated_at  — дата-время последнего обновления.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Уникальный идентификатор",
    )
    email = models.EmailField(
        unique=True,
        db_index=True,
        verbose_name="Электронная почта",
    )
    password = models.CharField(
        max_length=128,
        verbose_name="Хеш пароля",
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия",
    )
    patronymic = models.CharField(
        max_length=150,
        blank=True,
        default="",
        verbose_name="Отчество",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Аккаунт активен",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления",
    )

    objects = CustomUserManager()

    class Meta:
        db_table = "accounts_user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    @property
    def is_authenticated(self) -> bool:
        """DRF и Django проверяют это свойство для идентификации пользователя."""
        return True

    @property
    def is_anonymous(self) -> bool:
        """Аналог Django-интерфейса аутентификации."""
        return False

    def __str__(self) -> str:
        return f"{self.email} ({'активен' if self.is_active else 'деактивирован'})"

    def set_password(self, raw_password: str) -> None:
        """Хеширует и сохраняет пароль."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Проверяет соответствие пароля хешу."""
        return check_password(raw_password, self.password)


class RefreshToken(models.Model):
    """
    Хранилище refresh-токенов для возможности их отзыва (logout).

    При logout токен помечается is_revoked=True, что делает
    невозможным получение нового access-токена по данному refresh.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="refresh_tokens",
        verbose_name="Пользователь",
    )
    token = models.CharField(
        max_length=512,
        unique=True,
        db_index=True,
        verbose_name="Значение refresh-токена",
    )
    expires_at = models.DateTimeField(
        verbose_name="Срок действия",
    )
    is_revoked = models.BooleanField(
        default=False,
        verbose_name="Токен отозван",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        db_table = "accounts_refresh_token"
        verbose_name = "Refresh-токен"
        verbose_name_plural = "Refresh-токены"
        indexes = [
            models.Index(fields=["user", "is_revoked"], name="idx_rt_user_revoked"),
        ]

    def __str__(self) -> str:
        status = "отозван" if self.is_revoked else "действителен"
        return f"RefreshToken({self.user.email}, {status})"

    @property
    def is_expired(self) -> bool:
        """Возвращает True, если срок действия токена истёк."""
        return timezone.now() >= self.expires_at
