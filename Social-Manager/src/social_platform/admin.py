from django.contrib import admin
from .facebook_model import FacebookPageModel, FacebookUserModel
from .instgram_model import InstagramModel


admin.site.register(FacebookPageModel)
admin.site.register(FacebookUserModel)
admin.site.register(InstagramModel)