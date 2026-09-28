from django.urls import path

from api import views

urlpatterns = [
    path("account/signup/", views.SignupView.as_view(), name="signup"),
    path("account/login/", views.LoginView.as_view(), name="login"),
    path("account/logout/", views.LogoutView.as_view(), name="logout"),
    path("account/me/", views.MeView.as_view(), name="me"),
    path(
        "account/rotate-refresh-token/",
        views.RotateRefreshTokenView.as_view(),
        name="rotate-refresh-token",
    ),
]
