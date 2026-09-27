from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from iam.admin_site import admin_site


def health_view(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("api/", include("api.urls")),
    path("admin/", admin_site.urls),
    path("health/", health_view, name="health"),
    # openapi / swagger
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
]
