from rest_framework import permissions
from core.services.get_user_from_token import get_user_from_token
from django.shortcuts import get_object_or_404
from user.models import UserModel 
from user.model_role import Role 
from rest_framework.exceptions import PermissionDenied




class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print(obj)
        if obj.owner != request.user:
            raise PermissionDenied("You are not the owner of this post.")
        return True
    

class IsOwnerOrManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # التحقق من أن المستخدم الحالي هو المالك أو المدير
        return obj.owner == request.user or obj.owner.manager == request.user

class EmailVerifiedPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.email_verified:
            print("has_permission")
            return  True 
        return False

class ISManager(permissions.BasePermission):
    message = "You do not have permission to access this page."

    def has_permission(self, request,view):

        print(fr"requestrequest: ${request}")
        user_info = get_user_from_token(request)
        print(fr"{request}")
        if user_info is None: 
            print("user_info is None")
            return False
        try:
            if user_info.manager is None : 
                print("Permission Granted")
                return True
            else:
                print("Permission Denied: Is'nt Manager")
                return False
        except AttributeError:  
            print("AttributeError: user_info might not have role attribute")
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
            role = str(user_info.role.name)
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


class HasPermissionEmployeeToAccess(permissions.BasePermission):


    message = "You don't have the permission to access to this employee."

    def has_permission(self, request, view):

        print("has_permission")
        manager = get_user_from_token(request)
        if manager is None: 
            print("manager is None")
            return False
        try:
            email = request.data.get("email")
            empinfo = get_object_or_404(UserModel,email = email)

            print(f"User hr: {manager.manager}") 
            print(f"User Info: {empinfo}") 
            if  (str(manager) in str(empinfo.manager)) : #For the Social Medai Owner
                print("Permission Granted")
                return True
            if (str(manager.manager) in str(empinfo.manager) ) : #For the Hr
                print("Permission Granted")
                return True
            else:
                print("Permission Denied: Role mismatch")
                return False
        except AttributeError as e:  

            print(fr"AttributeError: manager might not have role attribute {e}")
            return False

 