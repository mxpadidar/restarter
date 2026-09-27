from django.urls import path

from api import views

urlpatterns = [
    path("iam/signup/", views.SignupView.as_view(), name="signup"),
]
