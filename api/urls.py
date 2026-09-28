from django.urls import path

from api import views

urlpatterns = [
    path("iam/signup/", views.SignupView.as_view(), name="signup"),
    path("iam/login/", views.LoginView.as_view(), name="login"),
    path("iam/logout/", views.LogoutView.as_view(), name="logout"),
    path("iam/me/", views.MeView.as_view(), name="me"),
    path(
        "iam/rotate-refresh-token/",
        views.RotateRefreshTokenView.as_view(),
        name="rotate-refresh-token",
    ),
]
