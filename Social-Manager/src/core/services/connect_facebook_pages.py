from platform_media.models import FacebookPageModel
from platform_media.serializers import FacebookPageModelSerializer
from rest_framework import serializers
from core.services.facebook_services import FacebookService
from core.services.create_response import create_response

def connect_facebook_pages(user_access_token, facebook_user_model, page_ids):
    try:
        if not page_ids:
            raise serializers.ValidationError("It's required to have pages in this account.")

        data = FacebookService.fetch_facebook_user_pages(user_access_token)
        print("FacebookService.fetch_facebook_user_pages(user_access_token)")
        pages_data = data.get("accounts", {}).get("data", [])
        print(f"page_ids  {page_ids}")
        print(f"pages_data  {pages_data}")
        saved_pages = []

        for page in pages_data:
            if page["id"] in page_ids:
                print("if page[id] in page_ids:")

                if FacebookPageModel.objects.filter(facebook_page_id=page["id"]).exists():
                    raise serializers.ValidationError(f"This page {page['name']} has already been connected.")
                print(facebook_user_model.social_media_account)
                page_data = {
                    "social_media_account": facebook_user_model.social_media_account.id,
                    "facebook_user": facebook_user_model.pk,
                    "facebook_page_id": page["id"],
                    "facebook_page_name": page["name"],
                    "global_name_brand": page.get("global_brand_page_name", ""),
                    "facebook_page_access_token": page["access_token"],
                    "facebook_page_picture_url": page["picture"]["data"]["url"],
                    "followers_count": page.get("followers_count", 0),
                    "following_count": page.get("fan_count", 0),
                    "tasks": page.get("tasks", []),
                    "category": page.get("category", ""),
                }

                print(f"page_data  {page_data}")

                serializer = FacebookPageModelSerializer(data=page_data, context={"view_action": "create_page", "facebook_user_model": facebook_user_model})
                if serializer.is_valid():
                    serializer.save()
                    saved_pages.append(serializer.data)
                else:
                    raise serializers.ValidationError(serializer.errors)
                print(f"saved_pages  {saved_pages}")
        return saved_pages
    except Exception as e:
        raise serializers.ValidationError(str(e))