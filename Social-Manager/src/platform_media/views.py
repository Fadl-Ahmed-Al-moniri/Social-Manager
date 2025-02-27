from django.shortcuts import render
from rest_framework import viewsets
from core.permission.permissions import ISManager
from rest_framework import viewsets, status,generics ,decorators
from .serializers import FacebookUserModelSerializer
from core.services.create_response import create_response
from core.services.get_user_from_token import get_user_from_token 
from django.shortcuts import get_object_or_404
from accounts_connection.models import SocialMediaAccount


# Create your views here.


class FacebookUserModelView(viewsets.ViewSet):
    
    serializer_class = FacebookUserModelSerializer
    permission_classes_by_action = {
        'create_facebook_user_account': [ISManager],
    }



    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    @decorators.action(detail=False, methods=["post"], url_path="create_facebook_user_account")
    def create_facebook_user_account(self,request):
        userinfo = get_user_from_token(request)
        try:
            pass
        except Exception as e:
            create_response(errors="errors", message=e, status_code= status.HTTP_400_BAD_REQUEST)



    
