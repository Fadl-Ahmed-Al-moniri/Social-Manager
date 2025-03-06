from django.db import models
from accounts_connection.models import SocialMediaAccount  




class FacebookUserModel(models.Model):
    id = models.BigAutoField(primary_key=True,verbose_name='ID',serialize=False,)
    social_media_account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE)
    facebook_user_id = models.CharField(max_length=255, )  # بدون unique=True
    facebook_user_name = models.CharField(max_length=255, blank=True, null=True)
    profile_picture_url = models.URLField(blank=True, null=True)
    facebook_user_email = models.CharField(max_length=255, blank=True, null=True)
    facebook_user_access_token = models.CharField(max_length=255,)

    def __str__(self):
        return self.facebook_user_name or f"User ID :{self.facebook_user_id}"

class FacebookPageModel(models.Model):
    social_media_account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, )
    facebook_user = models.ForeignKey(FacebookUserModel, on_delete=models.SET_NULL, blank=True, null=True)
    facebook_page_id= models.CharField(max_length=255, )
    facebook_page_name = models.CharField(max_length=255, blank=True, null=True)
    global_name_brand = models.CharField(max_length=255, blank=True, null=True)
    facebook_page_access_token = models.CharField(max_length=255)
    facebook_page_picture_url = models.TextField(blank=True, null=True)
    followers_count = models.BigIntegerField(blank=True, null=True)
    following_count = models.BigIntegerField(blank=True, null=True)
    tasks = models.JSONField(blank=True, null=True)
    category = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.facebook_page_name or f"Page ID :{self.facebook_page_id}"



class InstagramModel(models.Model):
    social_media_account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, )
    facebook_page = models.ForeignKey(FacebookPageModel, on_delete=models.SET_NULL, blank=True, null=True)
    instagram_id = models.CharField(max_length=255,)
    instagram_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    instagram_access_token = models.CharField(max_length=255,blank=True, null=True)
    profile_picture_url = models.URLField(max_length=1000,blank=True, null=True)
    followers_count = models.BigIntegerField(blank=True, null=True)
    following_count = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return self.instagram_name or "No Name"
