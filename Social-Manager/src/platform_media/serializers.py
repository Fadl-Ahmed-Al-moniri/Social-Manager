from rest_framework import serializers 
from ..aaa.models import *
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

        extra_kwargs = {
            'social_media_account': {'read_only': True},  
        }

    def validate(self, attrs):
        facebook_user_access_token  = attrs.get("facebook_user_access_token")
        facebook_user_id  = attrs.get("facebook_user_id")

        if not facebook_user_access_token :
            raise("access_token is requierd")

        if not facebook_user_id :
            raise("id is requierd")
        
        FacebookService.validate_facebook_account(
            user_access_token=facebook_user_access_token
            ,facebook_user_id=facebook_user_id)
        return super().validate(attrs)

    def create(self, validated_data):
        facebook_user_access_token = validated_data.get("facebook_user_access_token")
        if not facebook_user_access_token:
            raise serializers.ValidationError("User access token is required.")
        try:
            user_data = FacebookService.fetch_facebook_user_data(user_access_token= facebook_user_access_token)
            validated_data["facebook_user_id"] = user_data.get("id")
            validated_data["facebook_user_name"] = user_data.get("name")
            validated_data["profile_picture_url"] =  user_data["picture"]["data"]["url"]
            validated_data["facebook_user_email"] = user_data.get("email")
            validated_data["facebook_user_access_token"] = user_data.get("access_token")
        except Exception as e :
            raise serializers.ValidationError(f"Error fetching data from Facebook API: {e}")
        return super().create(validated_data)
    

    def update(self, instance, validated_data):
        facebook_user_access_token = validated_data.get("facebook_user_access_token")
        if not facebook_user_access_token :
            raise serializers.ValidationError("User access token is required.")    
        try:
            user_data = FacebookService.fetch_facebook_user_data(user_access_token= facebook_user_access_token)
            instance.facebook_user_access_token = user_data.get("access_token")
            instance.facebook_user_name = user_data.get("name")
            instance.profile_picture_url = user_data["picture"]["data"]["url"]
            instance.facebook_user_access_token = user_data.get("access_token")
        except Exception as e:
                    raise serializers.ValidationError(f"Error fetching data from Facebook API: {e}") 
        return super().update(instance, validated_data)
    
    

