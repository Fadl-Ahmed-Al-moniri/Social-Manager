from .models import Platform
from rest_framework.authentication import TokenAuthentication 
from rest_framework import viewsets , decorators , status 
from rest_framework.response import Response 
from .serializers import PlatformSerializer
from core.services.get_user_from_token import get_user_from_token
from core.services.create_response import  create_response
# Create your viewsets here.

class PlatformView(viewsets.ViewSet):
    serializer_class = PlatformSerializer
    @decorators.action(detail=False, methods=["get"], url_path="get")
    def getplatform(self, request):
            user  = get_user_from_token(request)
            if user:
                req = Platform.objects.all()
                serializer = self.serializer_class(req, many = True)
                return create_response(data=serializer.data, status_code=status.HTTP_200_OK,)
            return create_response(errors="Token", message="Invalid authorization header", status_code=status.HTTP_400_BAD_REQUEST,)
