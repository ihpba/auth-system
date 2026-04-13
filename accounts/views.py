"""
Представления (views) модуля accounts.

Реализуют полный жизненный цикл пользователя:
    - регистрация;
    - вход (login) с выдачей JWT;
    - обновление access-токена через refresh;
    - выход (logout) с отзывом refresh-токена;
    - просмотр/обновление профиля;
    - мягкое удаление аккаунта.
"""

import jwt as pyjwt

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.jwt_utils import (
    generate_access_token,
    generate_refresh_token,
    revoke_refresh_token,
    decode_token,
)
from accounts.models import CustomUser, RefreshToken
from accounts.serializers import (
    RegisterSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    UserSerializer,
    TokenResponseSerializer,
    RefreshTokenSerializer,
)


class RegisterView(APIView):
    """
    POST /api/auth/register/

    Регистрация нового пользователя.
    Доступно без аутентификации.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"detail": "Регистрация прошла успешно.", "user_id": str(user.id)},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/auth/login/

    Вход в систему по email и паролю.
    Возвращает пару access + refresh токенов.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower()
        password = serializer.validated_data["password"]

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "Неверный email или пароль.", "code": "unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "Аккаунт деактивирован.", "code": "unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password):
            return Response(
                {"detail": "Неверный email или пароль.", "code": "unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = generate_access_token(user)
        refresh_token, _ = generate_refresh_token(user)

        return Response(
            TokenResponseSerializer({"access": access_token, "refresh": refresh_token}).data,
            status=status.HTTP_200_OK,
        )


class RefreshTokenView(APIView):
    """
    POST /api/auth/token/refresh/

    Обновление access-токена с помощью refresh-токена.
    Если refresh-токен отозван или истёк — ошибка 401.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_str = serializer.validated_data["refresh"]

        try:
            payload = decode_token(refresh_str)
        except pyjwt.ExpiredSignatureError:
            return Response(
                {"detail": "Refresh-токен истёк.", "code": "unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except pyjwt.InvalidTokenError:
            return Response(
                {"detail": "Недействительный refresh-токен.", "code": "unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if payload.get("type") != "refresh":
            return Response(
                {"detail": "Ожидается refresh-токен.", "code": "unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            rt = RefreshToken.objects.get(token=refresh_str)
        except RefreshToken.DoesNotExist:
            return Response(
                {"detail": "Refresh-токен не найден.", "code": "unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if rt.is_revoked:
            return Response(
                {"detail": "Refresh-токен отозван.", "code": "unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            user = CustomUser.objects.get(id=payload["sub"], is_active=True)
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден или деактивирован.", "code": "unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Отзываем старый refresh (rotation)
        rt.is_revoked = True
        rt.save(update_fields=["is_revoked"])

        new_access = generate_access_token(user)
        new_refresh, _ = generate_refresh_token(user)

        return Response(
            TokenResponseSerializer({"access": new_access, "refresh": new_refresh}).data,
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    POST /api/auth/logout/

    Выход из системы: отзыв refresh-токена.
    Access-токен остаётся действительным до истечения своего срока
    (это стандартное поведение JWT — stateless-подход).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_str = request.data.get("refresh")
        if refresh_str:
            revoke_refresh_token(refresh_str)
        return Response(
            {"detail": "Вы успешно вышли из системы."},
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    """
    GET  /api/auth/profile/        — просмотр профиля.
    PATCH /api/auth/profile/       — обновление профиля.
    POST /api/auth/profile/delete/ — мягкое удаление аккаунта.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DeleteAccountView(APIView):
    """
    POST /api/auth/profile/delete/

    Мягкое удаление аккаунта:
        - is_active = False
        - отзыв всех refresh-токенов
        - пользователь больше не может залогиниться
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.is_active = False
        user.save(update_fields=["is_active"])

        RefreshToken.objects.filter(user=user, is_revoked=False).update(is_revoked=True)

        return Response(
            {"detail": "Аккаунт деактивирован (мягкое удаление)."},
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    """
    POST /api/auth/profile/change-password/

    Смена пароля текущего пользователя.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"detail": "Неверный текущий пароль."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"detail": "Пароль успешно изменён."})
