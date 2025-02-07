from django.shortcuts import get_object_or_404
from user.models import UserModel
from rest_framework.authtoken.models import Token


def get_user_from_token(request):
        """ Auxiliary function to retrieve the user from the token """

        token_key = request.headers.get('Authorization')
        if token_key and token_key.startswith("Token "):
            token_key = token_key.split("Token ")[1]
            token = get_object_or_404(Token, key=token_key)
            userinfo = get_object_or_404(UserModel, id=token.user.id)
            return userinfo
        else:
            None
        
