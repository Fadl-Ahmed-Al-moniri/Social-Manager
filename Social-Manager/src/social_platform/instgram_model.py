from django.db import models
from accounts_connection.models import SocialMediaAccount  


class InstagramModel(models.Model):
    social_media_account = models.OneToOneField(SocialMediaAccount, on_delete=models.CASCADE, primary_key=True)
    instagram_id = models.CharField(max_length=255,)
    instagram_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    instagram_access_token = models.CharField(max_length=255,)
    profile_picture_url = models.URLField(blank=True, null=True)
    followers_count = models.BigIntegerField(blank=True, null=True)
    following_count = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return self.instagram_name or "No Name"
