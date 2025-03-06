from rest_framework import serializers
from platform_media.models import InstagramModel , FacebookPageModel
from core.services.facebook_services import FacebookService
from accounts_connection.models import SocialMediaAccount
from core.services.instgram_services import InstgramService

class InstagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramModel
        fields = [
            "id",
            "social_media_account",
            "facebook_page",
            "instagram_id",
            "instagram_name",
            "username",
            "instagram_access_token",
            "profile_picture_url",
            "followers_count",
            "following_count",
        ]

    def validate(self, attrs):
        view_action = self.context.get('view_action')

        if view_action == "connect_to_instgram_account":
            instagram_id = attrs.get("instagram_id")
            user_access_token =self.context.get('data')["user_access_token"]
            # user_access_token = attrs.get("user_access_token")
            allowed_fields = { "instagram_id"}
            print(f"3 data:{ self.context.get('data')["user_access_token"]}")
            print(f"4 instagram_id:{ instagram_id}")

            for field in allowed_fields:
                if attrs[field] is None:
                    print(attrs[field])
                    raise serializers.ValidationError({field:f"This field {field} is required."})
                
            InstgramService.validate_instgram_business_account(user_access_token=user_access_token, instagram_id=instagram_id)
        return super().validate(attrs)

    def create(self, validated_data):
        social_account = validated_data.get("social_media_account")
        print(f"46 instagram_data:{ social_account}")
        social_account_model = SocialMediaAccount.objects.get(id = social_account.id)
        print(f"48 instagram_id ):{ validated_data.get("instagram_id")}")
        print(f"49 instagram_data:{ social_account_model}")
        social_account_model.external_account_id = validated_data.get("instagram_id")
        social_account_model.save()

        return super().create(validated_data)