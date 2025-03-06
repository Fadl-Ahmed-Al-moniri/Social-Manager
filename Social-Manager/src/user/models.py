from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,Group,Permission



class Role(models.Model):
    """
    Represents a role in the system.

    Attributes:
        name (str): The name of the role (e.g., 'Admin', 'Editor').
        description (str): A brief description of the role.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return fr"id:{self.pk},name:{self.name}"


class Permission(models.Model):
    """
    Represents a permission that can be assigned to roles.

    Attributes:
        name (str): The name of the permission (e.g., 'Edit Posts', 'Delete Comments').
        description (str): A brief description of what the permission allows.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name



class RolePermission(models.Model):
    """
    Represents the many-to-many relationship between roles and permissions.

    Attributes:
        role (ForeignKey): The role associated with the permission.
        permission (ForeignKey): The permission assigned to the role.

    Meta:
        unique_together: Ensures that each role-permission pair is unique.
    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='roles')

    class Meta:
        unique_together = ('role', 'permission')

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"



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
        def _get_default_role():
            role, created = Role.objects.get_or_create(name="Social Media Owner")
            return role.pk
        return _get_default_role

    username = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # role = models.ForeignKey(Role, on_delete=models.SET_NULL, related_name='users', default= Role.objects.get_or_create(name="Social Media Owner")[0].pk, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, related_name='users', default= Role.objects.get(name="Social Media Owner").pk, null=True, blank=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


