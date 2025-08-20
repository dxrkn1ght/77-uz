from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from apps.catalog.views import ProductViewSet
from apps.orders.views import OrderViewSet
from apps.accounts.views import AuthViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("orders", OrderViewSet, basename="order")
router.register("auth", AuthViewSet, basename="auth")

schema_view = get_schema_view(
    openapi.Info(
        title="Mercato API",
        default_version="v1",
        description="Swagger docs for online marketplace",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
]
