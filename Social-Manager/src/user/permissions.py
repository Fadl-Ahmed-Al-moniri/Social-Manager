from rest_framework import permissions
from .services import get_user_from_token

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user  



class EmailVerifiedPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.email_verified:
            return  True 
        return False


class HasPermissionEmployee(permissions.BasePermission):
    message = "You don't have the permission to perform this operation."

    def has_permission(self, request, view):
        print("has_permission")
        user_info = get_user_from_token(request)
        if user_info is None: 
            print("user_info is None")
            return False
        try:
            role = str(user_info.role)
            print(f"User Role: {role}") 
            if role in "Social Media Owner" or role in "HR": 
                print("Permission Granted")
                return True
            else:
                print("Permission Denied: Role mismatch")
                return False
        except AttributeError:  
            print("AttributeError: user_info might not have role attribute")
            return False