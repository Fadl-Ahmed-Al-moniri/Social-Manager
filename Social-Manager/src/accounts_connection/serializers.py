from rest_framework import serializers 
from .models import Platform , SocialMediaAccount
from user.models import UserModel
from core.services.get_user_from_token import get_user_from_token
from rest_framework.serializers import ValidationError



class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ['id','name','base_url', 'picture_url']
        extra_kwargs = {
            'id': {'read_only': True},
            'base_url': {'read_only': True},
            'picture_url': {'read_only': True},
        }


class SocialMediaAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaAccount
        fields = ['id', 'user', 'platform', 'external_account_id']
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'external_account_id': {'required': False},
        }

    def validate(self, attrs):
        view_action = self.context.get('view_action')
        request = self.context.get('request')
        userinfo = get_user_from_token(request)

        if view_action == "create_account":
            platform = attrs.get("platform")
            if not platform :
                raise serializers.ValidationError({"message": "The platform field is required."})
            attrs["user"] = userinfo.pk
        if view_action == "update_account":
            allowed_fields = {'external_account_id'}
            for field in attrs:
                if field not in allowed_fields:
                    raise serializers.ValidationError({field: f"Updating {field} is not allowed."})
        return attrs

    def create(self, validated_data):
        try:
            platform_instance = Platform.objects.get(name=validated_data["platform"])
            validated_data["platform"] = platform_instance
        except Platform.DoesNotExist:
            raise serializers.ValidationError({"platform": "Platform not found."})
        try:
            user_instance = UserModel.objects.get(pk=validated_data["user"])
            validated_data["user"] = user_instance
        except UserModel.DoesNotExist:
            raise serializers.ValidationError({"user": "User not found."})

        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.exterbnal_account_id = validated_data.get("external_account_id", instance.external_account_id)
        return super().update(instance, validated_data)
