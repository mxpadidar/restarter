from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health_view(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_view, name="health"),
    # openapi / swagger
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
]
