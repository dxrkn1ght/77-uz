from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from config.settings import (
    base as settings,
    django_settings_module,
)


class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http"] if django_settings_module == "development" else ["https"]
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title="dxrkn1ght's Project API",
        default_version="v1",
        description="API for online store website",
        terms_of_service="https://webresumekomron/terms/",
        contact=openapi.Contact(email="info@kevin.uz"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=BothHttpAndHttpsSchemaGenerator,
)

urlpatterns = [
    path("default-admin-panel/", admin.site.urls),
]

urlpatterns += [
    path("api/v1/common/", include("common.urls"), name="common"),
    path("api/v1/accounts/", include("accounts.urls"), name="accounts"),
    path("api/v1/store/", include("store.urls"), name="store"),
]

if django_settings_module == "development":
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path(
            "swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            "redoc/",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
        re_path(
            r"^swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        path("chaining/", include("smart_selects.urls")),
    ]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)