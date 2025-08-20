from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import api_info, health_check

app_name = 'common'

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('info/', api_info, name='api_info'),
    path('health/', health_check, name='health_check'),
]
