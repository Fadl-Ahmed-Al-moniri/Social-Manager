from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode
from django.utils.encoding import force_bytes , force_str
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.authtoken.models import Token 
from .model_role import Role , RolePermission ,Permission as PermissionModle
from core.services.send_email_message import  send_email_message
from rest_framework.exceptions import ValidationError
from django.urls import reverse
from .models import UserModel
from django.shortcuts import get_object_or_404




class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserModel
        fields = ['username', 'email','password','role','manager','created_at' ,'updated_at', ]
        extra_kwargs = {
            'email': {'read_only': True}, 
            'role': {'read_only': True}, 
            'manager': {'read_only': True}, 
            'password': {'write_only': True},
            'created_at': {'read_only': True}, 
            'updated_at': {'read_only': True},
                        }
        
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate_create(self, attrs):
        """
        this validate serializers for check the input if the user already exists
        """
        email = attrs.get("email")
        if UserModel.objects.filter(email=email).exists():
            raise ValidationError({"email": "the email already exists please try another email"})
        return attrs and UserSerializer.is_valid(self,raise_exception=True)


    def validate(self, attrs):
        """
        this validate serializers for check the input if the user already exists
        """
        view_action = self.context.get('view_action')
        if view_action == "update":
            return attrs
        email = attrs.get("email")
        if UserModel.objects.filter(email=email).exists():
            raise ValidationError({"email": "the email already exists please try another email"})
        return super().validate(attrs)
    
    def create(self, validated_data):
        user = UserModel(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


    def update(self, instance, validated_data):
        instance.username  =validated_data.get("username",instance.username)
        password = validated_data.get('password', None)
        if password :
            instance.set_password(password)
        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            try:
                user = UserModel.objects.get(email=email)
                if not user.check_password(password):
                    raise ValidationError({"message":"the password is Wrong Please try again!"})
                if not user.is_active:
                    message = {"message":"User account is disabled."}
                    raise ValidationError(message)
                if not user.email_verified:  
                    message = {"message":"This account must be authenticated in order for us to verify please the email Check your email."}
                    raise ValidationError(message)
            except UserModel.DoesNotExist:
                raise ValidationError({"message":"This user account isn't found."})
        else:
            raise ValidationError({"message": "Must include email and password"})
        attrs['user'] = user
        print(attrs)
        return attrs

class EmpManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id','username', 'email', 'password', 'role', 'manager', 'is_active','created_at', 'updated_at']
        extra_kwargs = {
            'id': {'read_only': True},
            'email': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'role': {'read_only': True},
            'manager': {'read_only': True},
            'password': {'write_only': True},
        }

    username = serializers.CharField()
    email = serializers.EmailField(required =True)
    password = serializers.CharField(write_only=True)
    role = serializers.CharField()
    manager = serializers.CharField()
    
    # def validate_create(self, attrs):
    #     allowed_fields = {'email', 'username', 'password', 'role','manager'}
    #     for field in attrs:
    #         if field not in allowed_fields:
    #             raise ValidationError({field: f"Updating {field} is not allowed."})
    #     email = attrs.get("email")
    #     if not email :
    #         raise ValidationError({"message": "The email field is required."})

    #     if UserModel.objects.filter(email=email).exists():
    #         raise ValidationError({"message": "The email already exists, please try another email."})

    #     role = attrs.get("role")
    #     manager = attrs.get("manager")

    #     if (not role ) and (not manager) :
    #         raise ValidationError({"message": "The role and manager fields are required."})
        
        
    #     if manager:
    #         manager_instance = UserModel.objects.get(email=manager)
    #         if not manager_instance:
    #             raise ValidationError({"manager": "The specified manager does not exist."})
    #         print(manager_instance.role)
    #         manager_role = manager_instance.role
    #         if not manager_role:
    #             raise ValidationError({"manager": "The manager does not have a valid role."})

    #         permissions = str(RolePermission.objects.filter(role=manager_role).values_list('permission__name', flat=True).get())
    #         print("All the permission related to his account"  in permissions )
    #         if not ("All permissions related to employee operations"  in permissions) and not ("All the permission related to his account"  in permissions):
    #             raise ValidationError({"manager": "The manager does not have permission to create employees."})
                
    #         print("All permissions related to e")

    #     return attrs and  EmpManagerSerializer.is_valid(self,raise_exception=True)


    def validate(self, attrs):
        view_action = self.context.get('view_action')

        if view_action =="create":
            email = attrs.get("email")
            if  UserModel.objects.filter(email=email).exists() :
                raise ValidationError({"message": "The email already exists, please try another email."})
            manager = attrs.get("manager")
            if manager:
                manager_instance = UserModel.objects.get(pk=manager)
                if not manager_instance:
                    raise ValidationError({"manager": "The specified manager does not exist."})
                print(rf"manager_instance:{manager_instance.role}")
                manager_role = manager_instance.role
                if not manager_role:
                    raise ValidationError({"manager": "The manager does not have a valid role."})
                permissions = str(RolePermission.objects.filter(role=manager_role.pk).values_list('permission__name', flat=True).get())
                print("All the permission related to his account"  in permissions )
                if not ("All permissions related to employee operations"  in permissions) and not ("All the permission related to his account"  in permissions):
                    raise ValidationError({"manager": "The manager does not have permission to create employees."})
        

        if view_action == "update" :
            allowed_fields = {'username', 'password'}
            for field in attrs:
                if field not in allowed_fields:
                    raise ValidationError({field: f"Updating {field} is not allowed."})

        if view_action =="update-advance" :
            email = attrs.get("email")
            username = attrs.get("username")
            password = attrs.get("password")
            role = attrs.get("role")
            print(email)
            if not  email : 
                raise ValidationError({"message": "The email field is required."})
            if (not username ) and (not password) and (not role)  :
                raise ValidationError({"message": "Those fields are required."})
        
        print("Aadada")
        return attrs
    

    def create(self, validated_data):
        """
        إنشاء مستخدم جديد
        """
        password = validated_data.pop('password')
        roleinstance = Role.objects.get(pk= validated_data["role"])
        managerinstance = UserModel.objects.get(pk=validated_data["manager"])
        validated_data["role"] = roleinstance
        validated_data["manager"]  = managerinstance
        user = UserModel(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """
        تحديث بيانات الموظف
        """
        instance.username = validated_data.get("username", instance.username)
        password = validated_data.get('password', None)
        roleID =validated_data.get("role", None)
        if roleID :
            print(roleID)
            roleinstance = Role.objects.get(pk= roleID)
            instance.role = roleinstance
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class UpdateEmpData(serializers.ModelSerializer):
    
    class Meta:
        model = UserModel
        fields = ['id','username', 'email', 'password', 'role', 'manager', 'is_active','created_at', 'updated_at']
        extra_kwargs = {
            'id': {'read_only': True},
            'email': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'manager': {'read_only': True},
            'password': {'write_only': True},
        }
    def validate(self, attrs):
        view_action = self.context.get('view_action')
        if view_action == "update" :
            username = attrs.get("username")
            password = attrs.get("password")

            if (not username ) and (not password) :
                raise ValidationError({"message": "The username or password fields are required."})
        if view_action =="update-advance" : 
            email = attrs.get("email")
            username = attrs.get("username")
            password = attrs.get("password")
            role = attrs.get("role")
            print(email)
            if  email : 
                raise ValidationError({"message": "The email field is required."})
            if (not username ) and (not password) and (not role)  :
                raise ValidationError({"message": "Those fields are required."})
            
        print("Aadada")
        return attrs 

    def update(self, instance, validated_data):
        """
        تحديث بيانات الموظف
        """
        instance.username = validated_data.get("username", instance.username)
        password = validated_data.get('password', None)
        rolename =validated_data.get("role", None)

        if rolename :
            print(rolename)
            roleinstance = Role.objects.get(name= rolename)
            instance.role = roleinstance
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate(self, attrs):
        email = attrs.get("email")
        if not email:
            raise ValidationError({"message":"The email field is required."})
        if not UserModel.objects.filter(email=email).exists():
            raise ValidationError({"message":"User with this email does not exist,please review your email and try agine."})
        return attrs
    
    def validate_email(self, value):
        try:
            user = UserModel.objects.get(email=value)
        except UserModel.DoesNotExist:
            raise ValidationError({"message":"User with this email does not exist,please review your email and try agine."})
        return value

    def save(self):
        try:
            email = self.validated_data['email']
            user = UserModel.objects.get(email=email)
            send_email_message(user=user,reverse_viewname="password_reset_confirm",title='Reset your password',content="Click the link to reset your password:")
            print(f"user:{user}")
        except (TypeError) as e:
            raise  "from userserlaizer have erorr ditels: {e}"

class PasswordResetConfirmSerializer(serializers.Serializer):

    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        uidb64 = self.context.get("uidb64")
        token = self.context.get("token")

        if not uidb64 or not token:
            raise ValidationError({"message":"Missing UID or Token in request."})

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(UserModel, pk=user_id)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            raise ValidationError({"message":"Invalid token or user ID."})
        if not default_token_generator.check_token(user, token):
            raise ValidationError({"message":"Token is invalid or expired."})
        data['user'] = user
        return data

    def save(self):


        # تحديث كلمة المرور للمستخدم
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return user

class Roleserializers(serializers.ModelSerializer): 

    class Meta:
        model = Role
        fields = ['id','name', 'description',]
        extra_kwargs = {
            'id': {'read_only': True}, 
            'name': {'read_only': True}, 
            'description': {'read_only': True},
                        }

    def validate(self, attrs):
        return super().validate(attrs)

    def is_valid(self, *, raise_exception=False):
        return super().is_valid(raise_exception=True)    