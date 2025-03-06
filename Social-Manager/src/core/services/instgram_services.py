from typing import Any, Dict, Optional
from rest_framework.exceptions import ValidationError
from pyfacebook.api import GraphAPI


class InstgramService:
    """
    A service to deal with Instgram, including verification and fetching data.
    """


    @staticmethod
    def fetch_instagram_business_user_info(user_access_token, instagram_id):
        """
        Fetch Instagram business account details using the Instagram ID.
        """
        try:
            api = GraphAPI(access_token=user_access_token)
            instagram_data = api.get_object(
                object_id=instagram_id,
                fields="id,name,username,profile_picture_url,followers_count,follows_count"
            )
            return instagram_data
        except Exception as e:
            raise ValueError(f"Error fetching Instagram business account data: {e}")

    @staticmethod
    def validate_instgram_business_account(user_access_token, instagram_id):
            """
            Check the authenticity of the token and user ID on Instgram.
            """
            try:
                api = GraphAPI(access_token=user_access_token)
                user_data = api.get_object(object_id=instagram_id, fields="id")
                
                if user_data : 
                    return True
                if str(user_data["id"]) != instagram_id:
                    raise ValidationError("instagram_id does not match the token's user.")
            except Exception as e:
                raise ValidationError(f"Error validating Facebook account: {e}")

    @staticmethod
    def fetch_instagram_user_info(user_access_token):
        """
        Fetch data for the user account linked to your Instagram account via Facebook authentication.
        """
        try:
            api = GraphAPI(access_token=user_access_token)
            data = api.get_object(
                object_id="me",
                fields=r"id,name,picture{url},accounts{id,name,global_brand_page_name,picture{url},access_token,category,followers_count,fan_count,instagram_business_account}"
            )

            pages_data = data.get("accounts", {}).get("data", [])
            saved_pages = []

            for page in pages_data:
                # التحقق من وجود instagram_business_account
                instagram_account = page.get("instagram_business_account")
                if instagram_account and instagram_account.get("id"):
                    instagram_id = instagram_account["id"]
                    instagram_data =InstgramService.fetch_instagram_business_user_info(user_access_token, instagram_id)

                    # تجميع البيانات
                    page_data = {
                        "user": {
                            "name": data.get("name"),
                            "picture": data.get("picture", {}).get("data", {}).get("url", "")
                        },
                        "page": {
                            "facebook_page_id": page.get("id"),
                            "facebook_page_name": page.get("name"),
                            "global_name_brand": page.get("global_brand_page_name", ""),
                            "facebook_page_access_token": page.get("access_token"),
                            "facebook_page_picture_url": page.get("picture", {}).get("data", {}).get("url", ""),
                            "followers_count": page.get("followers_count", 0),
                            "following_count": page.get("fan_count", 0),
                            "category": page.get("category", "")
                        },
                        "instagram_business_account": {
                            "id": instagram_data.get("id"),
                            "name": instagram_data.get("name"),
                            "username": instagram_data.get("username"),
                            "profile_picture_url": instagram_data.get("profile_picture_url"),
                            "followers_count": instagram_data.get("followers_count", 0),
                            "follows_count": instagram_data.get("follows_count", 0)
                        }
                    }
                    saved_pages.append(page_data)

            return saved_pages

        except Exception as e:
            raise ValueError(f"Error fetching pages data: {e}")

