"""
URL-маршруты модуля accounts.
"""

from django.urls import path

from accounts.views import (
    RegisterView,
    LoginView,
    LogoutView,
    RefreshTokenView,
    ProfileView,
    DeleteAccountView,
    ChangePasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token-refresh"),
    path("profile/", ProfileView.as_view(), name="auth-profile"),
    path("profile/delete/", DeleteAccountView.as_view(), name="auth-delete"),
    path("profile/change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
]
