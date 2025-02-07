from rest_framework import serializers 
from .models import *
from core.services.facebook_services import FacebookService


class FacebookUserModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = FacebookUserModel
        fields =[
            "social_media_account",
            "facebook_user_id",
            "facebook_user_name",
            "profile_picture_url",
            "facebook_user_email",
            "facebook_user_access_token",
        ]

    def validate(self, attrs): 

        facebook_user_access_token  = attrs.get("user_access_token")
        facebook_user_id  = attrs.get("facebook_user_id")
        FacebookService.validate_facebook_account(
            user_access_token=facebook_user_access_token
            ,facebook_user_id=facebook_user_id)
        
        
        return super().validate(attrs)

