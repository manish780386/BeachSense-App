from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.beaches.views import BeachViewSet

router = DefaultRouter()
router.register(r"beaches", BeachViewSet, basename="beach")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/token/", include("rest_framework_simplejwt.urls")) if False else path(
        "api/token/", __import__(
            "rest_framework_simplejwt.views", fromlist=["TokenObtainPairView"]
        ).TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]