from rest_framework import serializers
from accounts.models import Account
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from project.utils import *
from django.core.validators import MaxValueValidator, MinValueValidator


#Sign up serializer
class SignUpSerializer(serializers.ModelSerializer):
    '''Serializer for Signing up'''
    password = serializers.CharField(max_length=16, min_length=12,
                                     write_only=True)

    class Meta:
        model = Account
        fields = ['email', 'password','first_name','last_name','age']
        

    def validate(self, attrs):
        
        password = attrs.get('password', '')
        age= attrs.get('age', '')
        email= attrs.get('email','').lower()
        user = Account.objects.filter(email=email)
        #Checking if user is already registered
        if user:
            raise serializers.ValidationError({'error': 'Email already registered!!'})
        
        #Checking if user entered valid age
        if age == 0:
            raise serializers.ValidationError("Enter valid age")
            
        password,error2=validate_password(password)

        if len(password)==0:
            raise serializers.ValidationError(error2)
            
        return attrs

    def create(self, validated_data): 
        return Account.objects.create_user(**validated_data)

#Email verify serializer
class EmailVerificationSerializer(serializers.ModelSerializer):
    '''Serializer for Email Verification'''
    token = serializers.CharField(max_length=555)

    class Meta:
        model = Account
        fields = ['token']

#Reset password token check
class PasswordTokenCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields='__all__'

#Log in serializer
class LogInSerializer(serializers.ModelSerializer):
    '''Serializer for Log in'''
    
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=16, min_length=12,
                                     write_only=True)
    

    class Meta:
        model = Account
        fields = ['email', 'password', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        email=email.lower()
        user = auth.authenticate(email=email, password=password)
        
        if not user:
            raise AuthenticationFailed('Invalid email or password.')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')
        user.login_from = "email"
        user.save()
        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens
        }

            
#Reset password mail serializer
class RequestPasswordResetEmailSerializer(serializers.Serializer):
    '''Serializer for Reset Password'''
    
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']

#Change account password from mail serializer
class SetNewPasswordSerializer(serializers.Serializer):
    '''Serializer for setting new password after password reset'''
    
    password = serializers.CharField(min_length=12, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        password = attrs.get('password')
        token = attrs.get('token')
        uidb64 = attrs.get('uidb64')


        id = force_str(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(id=id)
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise AuthenticationFailed('The reset link is invalid.', 401)
        
        password,error2=validate_password(password,user.username)
        if len(password)==0:
            raise serializers.ValidationError(error2)
        user.set_password(password)
        user.save()
        return (user)

#Change account password serializer
class ChangePasswordSerializer(serializers.Serializer):
    '''Serializer for changing Password'''
    
    old_password = serializers.CharField(max_length=16, min_length=12,required=True)
    new_password = serializers.CharField(max_length=16, min_length=12,required=True)

#change to pro serializer
class ChangeToPro(serializers.Serializer):
    '''Serializer for changing Account type'''
    is_pro = serializers.BooleanField(default=False)

#change user info serializer
class ChangeUsernameSerializer(serializers.Serializer):
    '''Serializer for changing Account username'''
    username = serializers.CharField(max_length=60)

#Account info serializer
class OwnerSerializer(serializers.ModelSerializer):
    '''Serializer to get Account info '''
    class Meta:
        model = Account
        exclude=("password","date_joined", "updated_at",
        "last_login", "login_from", "groups","user_permissions")
        
        