from rest_framework import viewsets, status, decorators
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from core.services.facebook_services import FacebookService
from core.services.connect_facebook_pages import connect_facebook_pages
from django.shortcuts import get_object_or_404
from django.db.models import Q
from core.permission.permissions import ISManager
from core.services.create_response import create_response
from core.services.get_user_from_token import get_user_from_token
from accounts_connection.models import SocialMediaAccount, Platform
from .models import FacebookUserModel , FacebookPageModel
from .serializers import FacebookUserModelSerializer ,FacebookPageModelSerializer
from rest_framework import serializers 


class FacebookUserModelView(viewsets.ViewSet):
    serializer_class = FacebookUserModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes_by_action = {
        'get_info': [ISManager],
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
            return create_response(data= data, status_code=status.HTTP_200_OK)
        except Exception as e:
            return create_response(errors="errors", message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
    
    
    
    @decorators.action(detail=False, methods=["post"], url_path="connect_to_account")
    def connect_to_account(self, request):
        userinfo = get_user_from_token(request)
        try:
            data = request.data.copy()
            platform_facebook ,created= Platform.objects.get_or_create( name="Facebook")
            social_account, created = SocialMediaAccount.objects.get_or_create(user=userinfo, platform=platform_facebook ,external_account_id=request.data.get("facebook_user_id") )
            print(social_account)
            data["social_media_account"] = social_account.pk
            print(f"social_account: {social_account}")
    
            serializers = FacebookUserModelSerializer(data= data,context={'request': request, "view_action": "post"})
            if serializers.is_valid():
                if not FacebookUserModel.objects.filter(social_media_account =social_account ,facebook_user_id =request.data.get("facebook_user_id") ).exists():
                    facebook_user_model= serializers.save()
                facebook_user_model =FacebookUserModel.objects.get(social_media_account =social_account ,facebook_user_id =request.data.get("facebook_user_id") )
                print("6")

                print(fr"facebook_user_model:  {facebook_user_model}")
                page_ids = request.data.get("page_ids", [])  # قائمة بمعرفات الصفحات
                print(rf"print{(page_ids)}")
                saved_pages = connect_facebook_pages(request.data.get("facebook_user_access_token"), facebook_user_model, page_ids)

                return create_response(data={"facebook_user": FacebookUserModelSerializer(facebook_user_model).data, "pages": saved_pages}, message="Connected successfully", status_code=status.HTTP_201_CREATED)
            return create_response(errors="errors", message=serializers.errors, status_code=status.HTTP_400_BAD_REQUEST)        
        except( Exception ,BaseException) as e:
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


    @decorators.action(detail=False, methods=["post"], url_path="get_info_accounte")
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
        



class FacebookpageModelView(viewsets.ViewSet):
    serializer_class = FacebookPageModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes_by_action = {
        'get_pages': [ISManager],
        'info_page': [ISManager],
    }

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]
        


    @decorators.action(detail=False, methods=["post"],url_path="info_page")
    def info_page(self, request):
        userinfo = get_user_from_token(request)
        try:
            page_id = request.data.get("facebook_page_id")
            if not page_id:
                return create_response(errors="errors", message="facebook_page_id is required", status_code=status.HTTP_400_BAD_REQUEST)
            data = FacebookPageModel.objects.filter(facebook_page_id=page_id)
            serializer = FacebookPageModelSerializer(data, many=True, context={'request': request, "view_action": "info_page"})
            return create_response(data=serializer.data, message="success", status_code=status.HTTP_200_OK)
        except Exception as e:
            return create_response(errors="errors", message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=["post"],url_path="get_pages")
    def get_pages(self, request):
        userinfo = get_user_from_token(request)
        try:
            platform_facebook = get_object_or_404(Platform, name="Facebook")
            social_accounts = SocialMediaAccount.objects.filter(
                Q(user=userinfo) & Q(external_account_id__isnull=False) & Q(platform=platform_facebook)
            )
            if not social_accounts.exists():
                raise SocialMediaAccount.DoesNotExist("User does not have a linked social media account.")
            data = FacebookPageModel.objects.filter(social_media_account__in=social_accounts)
            serializer = FacebookPageModelSerializer(data, many=True, context={'request': request, "view_action": "get_pages"})
            return create_response(data=serializer.data, message="success", status_code=status.HTTP_200_OK)
        except Exception as e:
            return create_response(errors="errors", message=str(e), status_code=status.HTTP_400_BAD_REQUEST)


    @decorators.action(detail=False, methods=["post"], url_path="logout_from_page")
    def logout_from_page(self, request):
        try:
            page_id = request.data.get("facebook_page_id")
            if not page_id:
                return create_response(errors="errors", message="facebook_page_id is required", status_code=status.HTTP_400_BAD_REQUEST)
            facebook_user_page = get_object_or_404(FacebookPageModel, facebook_page_id=page_id)
            facebook_user_page.delete()

            return create_response(data={}, message="Logged out successfully", status_code=status.HTTP_200_OK)
        except Exception as e:
            return create_response(errors="errors", message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        
