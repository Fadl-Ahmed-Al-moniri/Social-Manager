from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import UserModel
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators  import api_view
from rest_framework.authtoken.models import Token



def send_massage_email(user, reverse_viewname,title,content, ):
    try:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.id))
        verification_url = settings.FRONTEND_URL + reverse(reverse_viewname, args=[uid, token])
        subject = title
        message = f'{content}: {verification_url}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list, fail_silently =True)
    except (TypeError, ValueError, OverflowError,UserModel.DoesNotExist) as m:
        raise f"send_massage_email_erorr: {m}"



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
        

