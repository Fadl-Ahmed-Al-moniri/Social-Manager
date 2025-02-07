from rest_framework import serializers 
from .models import Platform
class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ['id','base_url', 'picture_url']
        extra_kwargs = {
            'id': {'read_only': True},
            'base_url': {'read_only': True},
            'picture_url': {'read_only': True},
        }
