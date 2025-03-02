from django.db import models
from user.models import UserModel



class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)
    base_url = models.URLField()  
    picture_url = models.URLField() 

    class Meta:
        verbose_name = "Platform"
        verbose_name_plural = "Platforms"
    
    def __str__(self):
        return self.name 



class SocialMediaAccount(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    external_account_id = models.CharField(max_length=255, blank=True, null=True,)
    
    class Meta:
        unique_together = ('platform', 'external_account_id')  
        
    def __str__(self):
        return f"{self.pk}"



