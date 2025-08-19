from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.views import ProductViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="products")

schema_view = get_schema_view(
    openapi.Info(title="Marketplace API", default_version="v1"),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"),
]
