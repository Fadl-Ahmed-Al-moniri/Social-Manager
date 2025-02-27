from .models import Platform , SocialMediaAccount
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import TokenAuthentication 
from rest_framework import viewsets , decorators , status  
from rest_framework.authtoken.models import Token 
from rest_framework.response import Response 
from .serializers import PlatformSerializer , SocialMediaAccountSerializer
from core.services.get_user_from_token import get_user_from_token
from core.services.create_response import  create_response 
from django.shortcuts import get_object_or_404
from core.permission.permissions import HasPermissionEmployee , ISManager , EmailVerifiedPermission , IsOwnerOrManager  , IsOwner
# Create your viewsets here.

class PlatformView(viewsets.ViewSet):
    serializer_class = PlatformSerializer
    @decorators.action(detail=False, methods=["get"], url_path="get")
    def getplatform(self, request):
            user = get_user_from_token(request)
            if user:
                req = Platform.objects.all()
                serializer = self.serializer_class(req, many = True)
                return create_response(data=serializer.data, status_code=status.HTTP_200_OK,)
            return create_response(errors="Token", message="Invalid authorization header", status_code=status.HTTP_400_BAD_REQUEST,)


class SocialMediaAccountView(viewsets.ViewSet):
    serializer_class = SocialMediaAccountSerializer
    authentication_classes = [TokenAuthentication]

    permission_classes_by_action = {
        'create_account': [ISManager,IsOwner],
        'get_account': [ISManager],
        'update_account': [ISManager, IsOwner],
        'set_external_id': [ISManager, IsOwnerOrManager ,EmailVerifiedPermission],
    }

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    @decorators.action(detail=False, methods=["post"], url_path="create")
    def create_account(self, request): 
        serializer = SocialMediaAccountSerializer(data= request.data , context={'request': request, 'view_action': 'create_account'}  )
        if serializer.is_valid():
                serializer.save()
                return create_response(data=serializer.data, message="Succefully", status_code=status.HTTP_200_OK,)
        return create_response(errors="errors", message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST,)
        
    @decorators.action(detail=False, methods=["put"], url_path="update")
    def update_account(self, request):
                userinfo =get_user_from_token(request)
                id = request.data.get("id")
                if userinfo :
                    social_account = SocialMediaAccount.objects.get(id = id)
                    print(fr"social_account>>>>>>>>>>> {social_account}")
                    serializer = SocialMediaAccountSerializer(social_account,data= request.data,context={'request': request, 'view_action': 'update_account'},partial=True)
                    if serializer.is_valid():
                            serializer.save()
                            return create_response(data=serializer.data, message="Succefully", status_code=status.HTTP_200_OK,)
                return create_response(errors="errors", message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST,)
    
    
    @decorators.action(detail=False, methods=["post"], url_path="set_external_id")
    def set_external_id(self, request):
        try:
            userinfo = get_user_from_token(request)
            id = request.data.get("id")
            external_account_id = request.data.get("external_account_id")
            if not id or not external_account_id:
                return create_response(errors="errors", message="ID or external_account_id is missing", status_code=status.HTTP_400_BAD_REQUEST)
            if userinfo:
                social_account = get_object_or_404(SocialMediaAccount, id=id, user=userinfo.pk)
                social_account.external_account_id = external_account_id
                social_account.save() 
                serializer = SocialMediaAccountSerializer(
                    social_account,
                    data= request.data,
                    context={'request': request, 'view_action': 'update_account'},
                    partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    return create_response(data=serializer.data, message="Successfully updated", status_code=status.HTTP_200_OK)
                else:
                    return create_response(errors=serializer.errors, message="Validation error", status_code=status.HTTP_400_BAD_REQUEST)
            else:
                return create_response(errors="errors", message="User not found", status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return create_response(errors=str(e), message="An error oc curred", status_code=status.HTTP_400_BAD_REQUEST)
        

    @decorators.action(detail=False, methods=["get"], url_path="get")
    def get_account(self, request): 
                user =get_user_from_token(request)
                if user :
                    social_account =  SocialMediaAccount.objects.filter(user= user.pk)
                    serializer = SocialMediaAccountSerializer(social_account, many = True, context={'request': request, 'view_action': 'get_account'})
                    # return  Response(data= serializer.data, status=status.HTTP_200_OK)
                    return create_response(data=serializer.data, message="successfully requested", status_code=status.HTTP_200_OK,)
                return Response(data= serializer.errors, status=status.HTTP_400_BAD_REQUEST,)
            # return create_response(errors="errors", message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST,)
    

    
    @decorators.action(detail=False, methods=["post"], url_path="logout")
    def logout_account(self, request): 
                id = request.data.get("id")
                if id :
                    social_account =get_object_or_404(SocialMediaAccount , id = id).delete()
                    print(social_account)
                    return create_response( message="logout successfully", status_code=status.HTTP_200_OK,)
                return create_response(errors="errors", message="The logout process failed", status_code=status.HTTP_400_BAD_REQUEST,)

    # @decorators.action(detail=False, methods=["put"], url_path="update")
    # def update_account(self, request):
    #     try:
    #         userinfo = get_user_from_token(request)
    #         if not userinfo:
    #             return create_response(
    #                 errors="Invalid token",
    #                 message="Authentication failed",
    #                 status_code=status.HTTP_401_UNAUTHORIZED,
    #             )

    #         external_id = request.data.get("external_account_id")
    #         if not external_id:
    #             return create_response(
    #                 errors="external_account_id is required",
    #                 message="Validation error",
    #                 status_code=status.HTTP_400_BAD_REQUEST,
    #             )
    #         try:
    #             print(userinfo.pk)
    #             socialaccount = SocialMediaAccount.objects.select_related('user').get(user=userinfo.pk)
                
    #         except ObjectDoesNotExist:
    #             return create_response(
    #                 errors="Account not found",
    #                 message="No social media account found for this user",
    #                 status_code=status.HTTP_404_NOT_FOUND,
    #             )

    #         serializer = SocialMediaAccountSerializer(
    #             socialaccount,
    #             data=request.data,
    #             context={'request': request, 'view_action': 'update_account'},
    #             partial=True
    #         )

    #         if serializer.is_valid():
    #             serializer.save()
    #             return create_response(
    #                 data=serializer.data,
    #                 message="Account updated successfully",
    #                 status_code=status.HTTP_200_OK,
    #             )

    #         return create_response(
    #             errors=serializer.errors,
    #             message="Invalid data provided",
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #         )

    #     except Exception as e:
    #         return create_response(
    #             errors=str(e),
    #             message="An error occurred",
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         )