from django.shortcuts import render
from rest_framework import viewsets, status, decorators
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from core.services.facebook_services import FacebookService
from django.shortcuts import get_object_or_404
from django.db.models import Q
from core.permission.permissions import ISManager
from core.services.create_response import create_response
from core.services.get_user_from_token import get_user_from_token
from accounts_connection.models import SocialMediaAccount, Platform
from .models import FacebookUserModel
from .serializers import FacebookUserModelSerializer

class FacebookUserModelView(viewsets.ViewSet):
    serializer_class = FacebookUserModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes_by_action = {
        'connect_to_account': [ISManager],
        'get_accountes': [ISManager],
        'get_info_accounte': [ISManager],
        'logout_from_account': [ISManager],
    }

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    @decorators.action(detail=False, methods=["post"], url_path="get_info")
    def get_info(self, request):
        userinfo = get_user_from_token(request)
        try:
            facebook_user_access_token  = request.data.get("facebook_user_access_token")
            facebook_user_id  = request.data.get("facebook_user_id")
            data = FacebookService.fetch_facebook_user_info(
                user_access_token=facebook_user_access_token
                ,facebook_user_id=facebook_user_id)
            return create_response(data= data, message="Connected successfully", status_code=status.HTTP_200_OK)
        except Exception as e:
            return create_response(errors="errors", message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
    
    
    @decorators.action(detail=False, methods=["post"], url_path="connect_to_account")
    def connect_to_account(self, request):
        userinfo = get_user_from_token(request)
        try:
            data = request.data.copy()
            platform_facebook = get_object_or_404(Platform, name="Facebook")
            social_account = SocialMediaAccount.objects.create(user=userinfo, platform=platform_facebook)
            data["social_media_account"] = social_account.pk
            serializer = FacebookUserModelSerializer(data=data, context={'request': request, "view_action": "post"})
            if serializer.is_valid():
                serializer.save()
                return create_response(data=serializer.data, message="Connected successfully", status_code=status.HTTP_201_CREATED)
            return create_response(errors="errors", message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return create_response(errors="errors", message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=["get"], url_path="get_accountes")
    def get_accountes(self, request):
        userinfo = get_user_from_token(request)
        try:
            platform_facebook = get_object_or_404(Platform, name="Facebook")
            social_accounts = SocialMediaAccount.objects.filter(
                Q(user=userinfo) & Q(external_account_id__isnull=False) & Q(platform=platform_facebook)
            )
            if not social_accounts.exists():
                raise SocialMediaAccount.DoesNotExist("User does not have a linked social media account.")
            data = FacebookUserModel.objects.filter(social_media_account__in=social_accounts)
            serializer = FacebookUserModelSerializer(data, many=True, context={'request': request, "view_action": "getinfo"})
            return create_response(data=serializer.data, message="success", status_code=status.HTTP_200_OK)
        except SocialMediaAccount.DoesNotExist:
            return create_response(errors="errors", message="User does not have a linked social media account", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return create_response(errors="errors", message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=["get"], url_path="get_info_accounte")
    def get_info_accounte(self, request):
        userinfo = get_user_from_token(request)
        try:
            user_id = request.data.get("facebook_user_id")
            if not user_id:
                return create_response(errors="errors", message="facebook_user_id is required", status_code=status.HTTP_400_BAD_REQUEST)
            data = FacebookUserModel.objects.filter(facebook_user_id=user_id)
            serializer = FacebookUserModelSerializer(data, many=True, context={'request': request, "view_action": "get_info_accounte"})
            return create_response(data=serializer.data, message="success", status_code=status.HTTP_200_OK)
        except Exception as e:
            return create_response(errors="errors", message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=["post"], url_path="logout_from_account")
    def logout_from_account(self, request):
        try:
            account_id = request.data.get("facebook_user_id")
            if not account_id:
                return create_response(errors="errors", message="facebook_user_id is required", status_code=status.HTTP_400_BAD_REQUEST)
            facebook_user = get_object_or_404(FacebookUserModel, facebook_user_id=account_id)
            facebook_user.delete()
            social_account = get_object_or_404(SocialMediaAccount, external_account_id=account_id)
            social_account.delete()
            return create_response(data={}, message="Logged out successfully", status_code=status.HTTP_200_OK)
        except Exception as e:
            return create_response(errors="errors", message=str(e), status_code=status.HTTP_400_BAD_REQUEST)