from rest_framework import viewsets, status, decorators
from rest_framework.authentication import TokenAuthentication
from core.services.connect_instgram import connect_instagram
from platform_media.json.serializers_instgram import InstagramSerializer
from platform_media.models import FacebookPageModel , FacebookUserModel ,InstagramModel
from accounts_connection.models import Platform, SocialMediaAccount
from core.permission.permissions import ISManager 
from core.services.create_response import create_response
from django.shortcuts import get_object_or_404
from core.services.get_user_from_token import get_user_from_token
from core.services.instgram_services import InstgramService
from django.db.models import Q


class InstagramView(viewsets.ModelViewSet):
    serializer_class = InstagramSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes_by_action = {
        'connect_to_instagram': [ISManager],
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
            user_access_token  = request.data.get("user_access_token")
            if not user_access_token : 
                return create_response(errors="errors", message="This field access_token is required.", status_code=status.HTTP_400_BAD_REQUEST)
            data = InstgramService.fetch_instagram_user_info(
                user_access_token=user_access_token
                )
            
            return create_response(data= data, status_code=status.HTTP_200_OK)
        except Exception as e:
            return create_response(errors="errors", message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
    
    
    @decorators.action(detail=False, methods=["post"], url_path="connect_to_instgram_account")
    def connect_to_instgram_account(self, request):
        userinfo = get_user_from_token(request)
        try:
            data = request.data.copy()
            platform_instgram, created = Platform.objects.get_or_create(name="Instagram")
            social_account, created = SocialMediaAccount.objects.get_or_create(user=userinfo, platform=platform_instgram)
            data["social_media_account"] = social_account.pk
            print(f"1 :{ data["social_media_account"]}")
            print(f"5 user_access_token:{ request.data.get("user_access_token")}")
            print(data)

            serializers = InstagramSerializer(data=data, context={'request': request, "view_action": "connect_to_instgram_account", "data":data})
            if serializers.is_valid():
                instagram_id = request.data.get("instagram_id")
                print(f"2 instagram_id:{ instagram_id}")
                if not InstagramModel.objects.filter(social_media_account=social_account, instagram_id=instagram_id).exists():
                    instagram_user_model = connect_instagram(
                        user_access_token=request.data.get("user_access_token"),
                        instagram_id=instagram_id,
                        social_account=social_account.pk,
                        facebook_page=FacebookPageModel.objects.get(facebook_page_id = request.data.get("facebook_page_id")).pk
                    )
                else:
                    instagram_user_model = InstagramModel.objects.get(social_media_account=social_account, instagram_id=instagram_id)

                return create_response(
                    data={
                        "instagram_user": InstagramSerializer(instagram_user_model).data,
                    },
                    message="Connected successfully",
                    status_code=status.HTTP_201_CREATED
                )
            return create_response(errors="errors", message=serializers.errors, status_code=status.HTTP_400_BAD_REQUEST)
        except (Exception, BaseException) as e:
            return create_response(errors="errors", message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        

    @decorators.action(detail=False, methods=["get"], url_path="get_accountes")
    def get_accountes(self, request):
        userinfo = get_user_from_token(request)
        try:
            platform_instgram = get_object_or_404(Platform, name="Instagram")
            social_accounts = SocialMediaAccount.objects.filter(
                Q(user=userinfo) & Q(external_account_id__isnull=False) & Q(platform=platform_instgram)
            )
            if not social_accounts.exists():
                raise SocialMediaAccount.DoesNotExist("User does not have a linked social media account.")
            data = InstagramModel.objects.filter(social_media_account__in=social_accounts)
            serializer = InstagramSerializer(data, many=True, context={'request': request, "view_action": "getinfo"})
            return create_response(data=serializer.data, message="success", status_code=status.HTTP_200_OK)
        except SocialMediaAccount.DoesNotExist:
            return create_response(errors="errors", message="User does not have a linked social media account", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return create_response(errors="errors", message=str(e), status_code=status.HTTP_400_BAD_REQUEST)


    @decorators.action(detail=False, methods=["post"], url_path="get_info_accounte")
    def get_info_accounte(self, request):
        userinfo = get_user_from_token(request)
        try:
            user_id = request.data.get("instagram_id")
            if not user_id:
                return create_response(errors="errors", message="instagram_id is required", status_code=status.HTTP_400_BAD_REQUEST)
            data = InstagramModel.objects.filter(instagram_id=user_id)
            serializer = InstagramSerializer(data, many=True, context={'request': request, "view_action": "get_info_accounte"})
            return create_response(data=serializer.data, message="success", status_code=status.HTTP_200_OK)
        except Exception as e:
            return create_response(errors="errors", message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=["post"], url_path="logout_from_account")
    def logout_from_account(self, request):
        try:
            account_id = request.data.get("instagram_id")
            if not account_id:
                return create_response(errors="errors", message="instagram_id is required", status_code=status.HTTP_400_BAD_REQUEST)
            account_instgram = get_object_or_404(InstagramModel, instagram_id=account_id)
            account_instgram.delete()
            social_account = get_object_or_404(SocialMediaAccount, external_account_id=account_id)
            social_account.delete()
            return create_response(data={}, message="Logged out successfully", status_code=status.HTTP_200_OK)
        except Exception as e:
            return create_response(errors="errors", message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        

