from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlatformView

router = DefaultRouter()

router.register(r'platform', PlatformView, basename='platform')

urlpatterns = [
    path('', include(router.urls)),
]

