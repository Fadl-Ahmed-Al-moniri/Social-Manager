from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmpUserViewSet, UserAccountViewSet ,AuthViewSet ,PasswordResetRequestView, PasswordResetConfirmView , verify_email

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'info', UserAccountViewSet, basename='info')
router.register(r'emp', EmpUserViewSet, basename='employee')



urlpatterns = [
    path('', include(router.urls)),
    path('verify-email/<uidb64>/<token>/', verify_email, name='verify_email'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
