from django.contrib import admin
from .models import *
from .model_role import *

# Register your models here.


# admin.site.register(AdminModel)
admin.site.register(UserModel)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(RolePermission)


