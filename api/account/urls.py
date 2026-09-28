from django.urls import path

from api.account import views

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("me/", views.MeView.as_view(), name="me"),
    path(
        "rotate-refresh-token/",
        views.RotateRefreshTokenView.as_view(),
        name="rotate-refresh-token",
    ),
]
