# from django.db import models

# class Role(models.Model):
#     """
#     Represents a role in the system.

#     Attributes:
#         name (str): The name of the role (e.g., 'Admin', 'Editor').
#         description (str): A brief description of the role.
#     """
#     name = models.CharField(max_length=50, unique=True)
#     description = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return fr"id:{self.pk},name:{self.name}"


# class Permission(models.Model):
#     """
#     Represents a permission that can be assigned to roles.

#     Attributes:
#         name (str): The name of the permission (e.g., 'Edit Posts', 'Delete Comments').
#         description (str): A brief description of what the permission allows.
#     """
#     name = models.CharField(max_length=255, unique=True)
#     description = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.name


# class RolePermission(models.Model):
#     """
#     Represents the many-to-many relationship between roles and permissions.

#     Attributes:
#         role (ForeignKey): The role associated with the permission.
#         permission (ForeignKey): The permission assigned to the role.

#     Meta:
#         unique_together: Ensures that each role-permission pair is unique.
#     """
#     role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
#     permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='roles')

#     class Meta:
#         unique_together = ('role', 'permission')

#     def __str__(self):
#         return f"{self.role.name} - {self.permission.name}"
