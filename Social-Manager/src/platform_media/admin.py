from django.contrib import admin
from .models import FacebookUserModel ,FacebookPageModel ,InstagramModel

# Register your models here.



class FacebookUserAdmin(admin.ModelAdmin):
    list_display = [ 'social_media_account', 'facebook_user_id', 'facebook_user_name','facebook_user_email','facebook_user_access_token' ]
    list_filter = ['facebook_user_name','facebook_user_email','facebook_user_access_token']

class FacebookPageAdmin(admin.ModelAdmin):
    list_display = [ 'social_media_account', 'facebook_user', 'facebook_page_id','facebook_page_name','facebook_page_access_token' ]
    list_filter = ['facebook_user','facebook_page_name','facebook_page_access_token']

class InstagramAdmin(admin.ModelAdmin):
    list_display = [ 'social_media_account', 'instagram_id', 'instagram_name','username','instagram_access_token' ]
    list_filter = ['instagram_id','username','instagram_access_token']



admin.site.register(FacebookPageModel,FacebookPageAdmin)

admin.site.register(FacebookUserModel,FacebookUserAdmin)

admin.site.register(InstagramModel,InstagramAdmin)

