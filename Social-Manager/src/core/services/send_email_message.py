from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from user.models import UserModel


def send_email_message(user, reverse_viewname,title,content, ):
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
        raise f"send_email_message_erorr: {m}"
