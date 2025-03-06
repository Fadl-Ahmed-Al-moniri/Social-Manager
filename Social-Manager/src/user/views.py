from rest_framework import viewsets, status,generics ,decorators
from rest_framework.response import Response
from rest_framework.authtoken.models import Token 
from core.permission.permissions import EmailVerifiedPermission , IsOwner ,ISManager, HasPermissionEmployee ,HasPermissionEmployeeToAccess
from .models import UserModel , Role
from .serializers import EmpManagerSerializer, UserSerializer, LoginSerializer ,Roleserializers  
from rest_framework.authentication import TokenAuthentication
from core.services.get_user_from_token import  get_user_from_token
from core.services.send_email_message import send_email_message
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from .serializers import PasswordResetConfirmSerializer, PasswordResetSerializer


class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet for user authentication related operations. 
    frist login operation ,
    second operation is SingUP .
    """


    @decorators.permission_classes([EmailVerifiedPermission])
    @decorators.action(detail=False, methods=["post"])
    def login(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except   PermissionError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            send_email_message(user=user,reverse_viewname='verify_email',title='Verify your email address',content="Please verify your email by clicking the link")
            response = {
                "message":"Please verify your email by clicking the link below"
            }
            return Response(response, status=status.HTTP_201_CREATED,)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@decorators.api_view(http_method_names=["GET"])
def verify_email(request, uidb64, token):
    """
    This function handles email verification for a user.

    It decodes the provided `uidb64` to retrieve the user's unique ID, verifies the token, 
    and updates the email verification status if the token is valid. 
    If the token is invalid or expired, an appropriate error message is returned.

    Parameters:
    - request (HttpRequest): The HTTP request object.
    - uidb64 (str): Base64 encoded string representing the user ID.
    - token (str): Verification token to validate the email.

    Returns:
    - Response: 
        - On success: {"message": "Email verified successfully"} with status 200.
        - On failure: {"message": "Invalid verification link."} or 
    {"message": "Invalid or expired verification link."} with status 400.
    """
    try:
        
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(UserModel, pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        return Response({"message": "Invalid verification link."}, status=status.HTTP_400_BAD_REQUEST)
    if default_token_generator.check_token(user, token):
        user.email_verified = True
        user.save()
        return Response({"message": f"Email verified successfully"})
    else:
        return Response({"message": "Invalid or expired verification link."}, status=status.HTTP_400_BAD_REQUEST)

class UserAccountViewSet(viewsets.ViewSet):
    """
    ViewSet for user account related operations.
    """
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsOwner , ISManager]

    @decorators.action(detail=False, methods=["get"], url_path="get")
    def getUserData(self, request):
        userinfo =  get_user_from_token(request)
        if userinfo is not None:
            serializer = self.serializer_class(userinfo)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "Invalid authorization header"}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=["post"], url_path="update")
    def updateUserData(self, request):
        userinfo =  get_user_from_token(request)
        if userinfo is not None:
            serializer = self.serializer_class(userinfo,context={'request': request, 'view_action': 'update'}, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Invalid authorization header"}, status=status.HTTP_400_BAD_REQUEST)

class EmpUserViewSet(viewsets.ViewSet):
    """
    ViewSet for Employee account-related operations.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes_by_action = {
        'create_emp_user': [HasPermissionEmployee],
        'update_user_data': [IsOwner],
        'update_user_data_advance': [HasPermissionEmployee,HasPermissionEmployeeToAccess],
        'deactivate_emp_user': [HasPermissionEmployee,HasPermissionEmployeeToAccess],
        'activate_emp_user': [HasPermissionEmployee,HasPermissionEmployeeToAccess],
        'get_info_emp': [HasPermissionEmployee],
    }
    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]


    @decorators.action(detail=False, methods=["post"], url_path="create")
    def create_emp_user(self, request):
        """
        Create a new employee account.
        """
        serializer = EmpManagerSerializer(data=request.data,context={'request': request, 'view_action': 'create'},)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            send_email_message(user=user,reverse_viewname='verify_email',title='Verify your email',content="Please verify your email by clicking the link")
            response = {
                "message":"please verify your email by clicking the link below",
                "data":serializer.data
            }
            return Response( response , status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @decorators.action(detail=False, methods=["put"], url_path="update")
    def update_user_data(self, request):
        """
        Update employee account information.
        """
        user_info = get_user_from_token(request)
        if not user_info:   
            return Response({"message": "Invalid authorization header"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EmpManagerSerializer(user_info, context={'request': request, 'view_action': 'update'},data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @decorators.action(detail=False, methods=["put"], url_path="update-advance")
    def update_user_data_advance(self, request):
        """
        Update employee account information.
        """
        manager_info = get_user_from_token(request)
        if not manager_info:
            return Response({"message": "Invalid authorization header"}, status=status.HTTP_400_BAD_REQUEST)
        userinfo = get_object_or_404(UserModel, email=request.data.get("email"))
        serializer = EmpManagerSerializer(userinfo,data = request.data,context={'request': request, 'view_action': 'update-advance'}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @decorators.action(detail=False, methods=["get"], url_path="info")
    def get_info(self, request):
        userinfo =  get_user_from_token(request)
        if userinfo is not None:
            serializer =EmpManagerSerializer(userinfo)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "Invalid authorization header"}, status=status.HTTP_400_BAD_REQUEST)


    @decorators.action(detail=False, methods=["get"], url_path="get_emps")
    def get_info_emp(self, request):
        userinfo =  get_user_from_token(request)
        if userinfo is not None:
            empdata = UserModel.objects.filter(manager = userinfo.pk)
            serializer =EmpManagerSerializer(empdata , many = True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "Invalid authorization header"}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=["post"], url_path="deactivate")
    def deactivate_emp_user(self, request):
        """
        Deactivate an employee account.
        """
        return self._toggle_user_status(request, False)

    @decorators.action(detail=False, methods=["post"], url_path="activate")
    def activate_emp_user(self, request):
        """
        Activate an employee account.
        """
        return self._toggle_user_status(request, True)
    
    def _toggle_user_status(self, request, is_active):
        """
        Helper method to activate or deactivate an employee account.
        """

        emp_email = request.data.get("email")
        if not emp_email:
            return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        emp_model = get_object_or_404(UserModel, email=emp_email)

        emp_model.is_active = is_active
        emp_model.save()
        status_message = "enabled" if is_active else "disabled"
        return Response({"message": f"Account {status_message} successfully."}, status=status.HTTP_200_OK)

    @decorators.action(detail=False, methods=["get"], url_path="roleList")
    def get_role(self, request):
        user_info = get_user_from_token(request)
        if not user_info:
            return Response({"message": "Invalid authorization header"}, status=status.HTTP_400_BAD_REQUEST)
        roles = Role.objects.exclude(name="System Administrator")
        serializer = Roleserializers(roles, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
        # return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset link sent to your email, please check your Email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uidb64=None, token=None):
        """
            Handles password reset requests for users.

            This method allows users to reset their passwords by providing a unique identifier (uidb64)
            and a token for verification. The values can be passed either as URL parameters or in the
            request headers. If either value is missing, the method returns an appropriate error message.

            The process involves:
            - Checking the presence of `uidb64` and `token`.
            - Passing the received data along with the context to the serializer for validation.
            - If the serializer validates the data, the password is reset, and a success response is returned.
            - If validation fails, appropriate error details are returned.

            Parameters:
            - request (HttpRequest): The HTTP request object containing data and optional headers.
            - uidb64 (str, optional): The base64-encoded user identifier, passed as a URL parameter.
            - token (str, optional): The token for password reset validation, passed as a URL parameter.

            Returns:
            - Response: A JSON response with a success message or error details, depending on the operation result.
        """
    
        uidb64 = uidb64 or request.headers.get('uidb64')
        token = token or request.headers.get('token')

        if not uidb64 or not token:
            return Response(
                {"message": "Missing UID or Token. Please provide the required values."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        
        serializer = self.get_serializer(data=request.data, context={'uidb64': uidb64, 'token': token})
        
        
        if serializer.is_valid():
            user=  serializer.save() 
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            return Response(
                {"message": "Your password has been reset successfully."},
                status=status.HTTP_200_OK
            )
        
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

