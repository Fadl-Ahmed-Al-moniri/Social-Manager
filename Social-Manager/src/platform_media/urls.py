from django.urls import path,include
from platform_media.views import FacebookUserModelView , FacebookpageModelView
from platform_media.view.instgram_view import InstagramView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'facebook', FacebookUserModelView, basename='facebook')
router.register(r'facebook-page', FacebookpageModelView, basename='facebook-page')
router.register(r'instgram', InstagramView, basename='instgram')

urlpatterns = [
    path('', include(router.urls)),
]
