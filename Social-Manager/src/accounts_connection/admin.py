from django.contrib import admin
from .models import  SocialMediaAccount , Platform

class PlatformAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'base_url', 'picture_url']
    list_filter = ['id','name',]
    

class SocialMediaAccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'platform' , 'external_account_id']
    list_filter = ['id','platform','user', 'external_account_id']
    search_fields = ['id',]
    
admin.site.register(Platform, PlatformAdmin)
admin.site.register(SocialMediaAccount ,SocialMediaAccountAdmin)
