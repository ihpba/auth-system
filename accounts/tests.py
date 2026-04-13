"""
Тесты модуля accounts: регистрация, логин, логаут, профиль,
мягкое удаление, смена пароля, обновление токенов.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import CustomUser, RefreshToken


class RegisterViewTest(TestCase):
    """Тесты эндпоинта POST /api/auth/register/."""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/auth/register/"

    def test_register_success(self):
        """Успешная регистрация нового пользователя."""
        data = {
            "email": "new@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "first_name": "Иван",
            "last_name": "Иванов",
            "patronymic": "Иванович",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user_id", response.data)
        user = CustomUser.objects.get(email="new@example.com")
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password("StrongPass123!"))

    def test_register_password_mismatch(self):
        """Пароли не совпадают — ошибка валидации."""
        data = {
            "email": "mismatch@example.com",
            "password": "Pass1234!",
            "password_confirm": "Different!",
            "first_name": "Тест",
            "last_name": "Тестов",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        """Повторная регистрация с тем же email."""
        CustomUser.objects.create_user(email="dup@example.com", password="Pass1234!")
        data = {
            "email": "dup@example.com",
            "password": "Pass1234!",
            "password_confirm": "Pass1234!",
            "first_name": "Дубль",
            "last_name": "Дублёв",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_short_password(self):
        """Пароль короче 8 символов — ошибка."""
        data = {
            "email": "short@example.com",
            "password": "Ab1!",
            "password_confirm": "Ab1!",
            "first_name": "Короткий",
            "last_name": "Пароль",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginViewTest(TestCase):
    """Тесты эндпоинта POST /api/auth/login/."""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/auth/login/"
        self.user = CustomUser.objects.create_user(
            email="login@example.com", password="TestPass123!"
        )

    def test_login_success(self):
        """Успешный вход — получены access и refresh токены."""
        response = self.client.post(self.url, {
            "email": "login@example.com",
            "password": "TestPass123!",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        """Неверный пароль — 401."""
        response = self.client.post(self.url, {
            "email": "login@example.com",
            "password": "WrongPass!",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Несуществующий email — 401."""
        response = self.client.post(self.url, {
            "email": "nobody@example.com",
            "password": "Whatever123!",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_deactivated_user(self):
        """Деактивированный аккаунт — 401."""
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.url, {
            "email": "login@example.com",
            "password": "TestPass123!",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutViewTest(TestCase):
    """Тесты эндпоинта POST /api/auth/logout/."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="logout@example.com", password="TestPass123!"
        )
        from accounts.jwt_utils import generate_access_token, generate_refresh_token
        self.access = generate_access_token(self.user)
        self.refresh, _ = generate_refresh_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_logout_success(self):
        """Успешный выход — refresh-токен отозван."""
        response = self.client.post("/api/auth/logout/", {"refresh": self.refresh})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rt = RefreshToken.objects.get(token=self.refresh)
        self.assertTrue(rt.is_revoked)

    def test_logout_unauthenticated(self):
        """Выход без токена — 401."""
        self.client.credentials()
        response = self.client.post("/api/auth/logout/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileViewTest(TestCase):
    """Тесты профиля: просмотр, обновление, мягкое удаление."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="profile@example.com", password="TestPass123!",
            first_name="Старое", last_name="Имя",
        )
        from accounts.jwt_utils import generate_access_token
        self.access = generate_access_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_get_profile(self):
        """Просмотр профиля аутентифицированного пользователя."""
        response = self.client.get("/api/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "profile@example.com")

    def test_update_profile(self):
        """Обновление имени в профиле."""
        response = self.client.patch("/api/auth/profile/", {"first_name": "Новое"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Новое")

    def test_profile_unauthenticated(self):
        """Доступ к профилю без токена — 401."""
        self.client.credentials()
        response = self.client.get("/api/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DeleteAccountViewTest(TestCase):
    """Тест мягкого удаления аккаунта."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="delete@example.com", password="TestPass123!",
        )
        from accounts.jwt_utils import generate_access_token, generate_refresh_token
        self.access = generate_access_token(self.user)
        generate_refresh_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_soft_delete(self):
        """Мягкое удаление: is_active=False, refresh-токены отозваны."""
        response = self.client.post("/api/auth/profile/delete/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertEqual(
            RefreshToken.objects.filter(user=self.user, is_revoked=False).count(), 0
        )

    def test_cannot_login_after_deletion(self):
        """После мягкого удаления вход невозможен."""
        self.client.post("/api/auth/profile/delete/")
        response = self.client.post("/api/auth/login/", {
            "email": "delete@example.com",
            "password": "TestPass123!",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RefreshTokenViewTest(TestCase):
    """Тест обновления access-токена через refresh."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="refresh@example.com", password="TestPass123!"
        )
        from accounts.jwt_utils import generate_access_token, generate_refresh_token
        self.access = generate_access_token(self.user)
        self.refresh, _ = generate_refresh_token(self.user)

    def test_refresh_success(self):
        """Успешное обновление — получена новая пара токенов."""
        response = self.client.post("/api/auth/token/refresh/", {"refresh": self.refresh})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_revoked_token(self):
        """Отозванный refresh-токен — 401."""
        from accounts.jwt_utils import revoke_refresh_token
        revoke_refresh_token(self.refresh)
        response = self.client.post("/api/auth/token/refresh/", {"refresh": self.refresh})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangePasswordViewTest(TestCase):
    """Тест смены пароля."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="chpwd@example.com", password="OldPass123!"
        )
        from accounts.jwt_utils import generate_access_token
        self.access = generate_access_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_change_password_success(self):
        """Успешная смена пароля."""
        response = self.client.post("/api/auth/profile/change-password/", {
            "old_password": "OldPass123!",
            "new_password": "NewPass456!",
            "new_password_confirm": "NewPass456!",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass456!"))

    def test_change_password_wrong_old(self):
        """Неверный старый пароль — 400."""
        response = self.client.post("/api/auth/profile/change-password/", {
            "old_password": "WrongOld!",
            "new_password": "NewPass456!",
            "new_password_confirm": "NewPass456!",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_mismatch(self):
        """Новые пароли не совпадают — 400."""
        response = self.client.post("/api/auth/profile/change-password/", {
            "old_password": "OldPass123!",
            "new_password": "NewPass456!",
            "new_password_confirm": "Different!",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CustomUserModelTest(TestCase):
    """Тесты модели CustomUser."""

    def test_is_authenticated_property(self):
        """Аутентифицированный пользователь возвращает is_authenticated=True."""
        user = CustomUser.objects.create_user(email="auth@example.com", password="Pass1234!")
        self.assertTrue(user.is_authenticated)
        self.assertFalse(user.is_anonymous)

    def test_password_hashing(self):
        """Пароль хранится в виде хеша, не в открытом виде."""
        user = CustomUser.objects.create_user(email="hash@example.com", password="MySecret123!")
        self.assertNotEqual(user.password, "MySecret123!")
        self.assertTrue(user.check_password("MySecret123!"))
        self.assertFalse(user.check_password("WrongPassword!"))
