from django.urls import path,include
from platform_media.views import FacebookUserModelView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'facebook', FacebookUserModelView, basename='facebook')
urlpatterns = [
    path('', include(router.urls)),
]
