from django.db import models
from .model_role import Role
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,Group,Permission


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    

class UserModel(AbstractBaseUser, PermissionsMixin):

    def get_default_role():
        return Role.objects.get(name= "Social Media Owner").pk


    username = models.CharField(max_length=255,)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) 
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, related_name='users', default=get_default_role,null=True, blank=True,)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    objects = CustomUserManager()




    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username"]
    
    def __str__(self):
        return self.email




