from core.services.instgram_services import InstgramService
from rest_framework import serializers
from platform_media.json.serializers_instgram import InstagramSerializer
from platform_media.models import FacebookPageModel

def connect_instagram(user_access_token, instagram_id, social_account, facebook_page=None):
    """
    Connect an Instagram business account to the system.
    """
    try:
        # جلب بيانات Instagram Business Account
        instagram_data = InstgramService.fetch_instagram_business_user_info(user_access_token, instagram_id)
        print(f"13 instagram_data:{ social_account}")
        # إعداد البيانات للحفظ
        instagram_data = {
            "social_media_account": social_account,
            "instagram_id": instagram_data.get("id"),
            "instagram_name": instagram_data.get("name"),
            "username": instagram_data.get("username"),
            "instagram_access_token": user_access_token,
            "profile_picture_url": instagram_data.get("profile_picture_url"),
            "followers_count": instagram_data.get("followers_count", 0),
            "following_count": instagram_data.get("follows_count", 0),
        }
        print(f"25 instagram_data:{ instagram_data}")

        if facebook_page:
            instagram_data["facebook_page"] =facebook_page

        print(f"30 instagram_data:{ instagram_data}")


        serializer = InstagramSerializer(data=instagram_data)
        if serializer.is_valid():
            instagram_user_model = serializer.save()
            return instagram_user_model
        else:
            raise serializers.ValidationError(serializer.errors)

    except Exception as e:
        raise ValueError(f"Error connecting Instagram account: {e}")