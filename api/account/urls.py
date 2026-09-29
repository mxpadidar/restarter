from django.urls import path

from api.account import views

urlpatterns = [
    path("users/", views.UserListView.as_view(), name="user-list"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("me/", views.MeView.as_view(), name="me"),
    path("token/rotate/", views.TokenRotationView.as_view(), name="token-rotate"),
]
