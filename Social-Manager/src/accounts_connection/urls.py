from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlatformView , SocialMediaAccountView

router = DefaultRouter()

router.register(r'platform', PlatformView, basename='platform')
router.register(r'social-manager', SocialMediaAccountView, basename='social-manager')

urlpatterns = [
    path('', include(router.urls)),
]

