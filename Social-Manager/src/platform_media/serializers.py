from rest_framework import serializers 
from core.services.facebook_services import FacebookService
from accounts_connection.models import SocialMediaAccount
from .models import FacebookUserModel , FacebookPageModel


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
        view_action = self.context.get('view_action')
        if view_action  == "get_info" :
            facebook_user_access_token  = attrs.get("facebook_user_access_token")
            facebook_user_id  = attrs.get("facebook_user_id")
            allowed_fields = { "facebook_user_access_token", "facebook_user_id"}
            for field in allowed_fields:
                if attrs[field] is None:
                    print(attrs[field])
                    raise serializers.ValidationError({field:f"This field {field} is required."})

        if view_action  == "post":
            facebook_user_access_token  = attrs.get("facebook_user_access_token")
            facebook_user_id  = attrs.get("facebook_user_id")
            allowed_fields = { "facebook_user_access_token", "facebook_user_id"}

            for field in allowed_fields:
                if attrs[field] is None:
                    print(attrs[field])
                    raise serializers.ValidationError({field:f"This field {field} is required."})

            FacebookService.validate_facebook_account(
                user_access_token=facebook_user_access_token
                ,facebook_user_id=facebook_user_id)
        if view_action  == "logout_from_account" :
            facebook_user_id = attrs.get("facebook_user_id")
            if not facebook_user_id:
                raise serializers.ValidationError({facebook_user_id:f"This field {facebook_user_id} is required."})

        
        if view_action  == "get_info_accounte":
            facebook_user_id = attrs.get("facebook_user_id")
            if not facebook_user_id:
                raise serializers.ValidationError({facebook_user_id:f"This field {facebook_user_id} is required."})


        
        return super().validate(attrs)

    def create(self, validated_data):
        print("4") 
        
        social_account_id = (validated_data.get("social_media_account").id)
        print(social_account_id)
        facebook_user_access_token = validated_data.get("facebook_user_access_token")
        try:
            user_data = FacebookService.fetch_facebook_user_data(user_access_token= facebook_user_access_token)
            validated_data["facebook_user_id"] = user_data.get("id")
            validated_data["facebook_user_name"] = user_data.get("name")
            validated_data["profile_picture_url"] =  user_data["picture"]["data"]["url"]
            validated_data["facebook_user_email"] = user_data.get("email")
            social_account= SocialMediaAccount.objects.get(id= social_account_id)
            print(social_account)
            social_account.external_account_id = user_data.get("id")
            social_account.save()
        except Exception as e :
            raise serializers.ValidationError(f"Error: {e}")
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




class FacebookPageModelSerializer(serializers.ModelSerializer):

    class Meta :
        model = FacebookPageModel
        fields = [
            "social_media_account",
            "facebook_user",
            "facebook_page_id",
            "facebook_page_name",
            "global_name_brand",
            "facebook_page_access_token",
            "facebook_page_picture_url",
            "followers_count",
            "following_count",
            "tasks",
            "category",
        ]

    def validate(self, attrs):
        facebook_page_id= attrs.get("facebook_page_id")
        facebook_page_access_token = attrs.get("facebook_page_access_token")

        return super().validate(attrs)