from django.contrib import admin
from .models import *
from .model_role import *

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'role','manager']
    list_filter = ['manager','role','is_active', 'email_verified']

class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    list_filter = ['id','name', ]
    

class PermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    list_filter = ['id','name', ]
    

class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'role', 'permission']
    list_filter = ['id','role','permission']
    

admin.site.register(UserModel, UserAdmin)
admin.site.register(Role ,RoleAdmin)
admin.site.register(Permission ,PermissionAdmin)
admin.site.register(RolePermission,RolePermissionAdmin)
