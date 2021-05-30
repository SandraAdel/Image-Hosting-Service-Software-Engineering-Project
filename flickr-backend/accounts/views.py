from profiles.models import *
from django.http import request
from rest_framework import generics, status, views
from django.shortcuts import render, redirect
from .serializers import *
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import Account
from project.utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from project.utils import Util
from rest_framework import permissions,viewsets
from project.permissions import IsOwner
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

#Functionality
def verifying_user(user):
    if not user.is_verified:
        # Creating user profile
        Profile.objects.create(owner=user)
        user.is_verified = True
        user.save()
    
def prepare_verify_email(current_site,user,token):
    relative_link = reverse('accounts:email-verify')
    absurl = 'http://'+current_site+relative_link+"?token="+str(token)
    email_body = 'Hi ' + user.username + ' Use link to verify \n' + absurl
    data = {'email_body': email_body,
            'to_email': user.email,
            'email_subject': 'Verify Your Email'}
    return data

def prepare_reset_password_email(current_site,user,token,uidb64):
    relative_link = reverse('accounts:password-reset-confirm',
                            kwargs={'uidb64': uidb64, 'token': token})
    absurl = 'http://'+current_site+relative_link
    email_body = 'Hello,\n Use link below to reset your password  \n' + absurl
    data = {'email_body': email_body, 'to_email': user.email,
            'email_subject': 'Reset you password'}
    return data

def check_account_exist_email(email):
    bool = Account.objects.filter(email=email).exists()
    if bool:
        error=''
    else:
        error= 'Email doesnt exist. Kindly recheck entered email'
    return bool,error

def change_to_pro(user):
    user.is_pro =True
    user.save()

def change_to_normal(user):
    user.is_pro =False
    user.save()
    
def check_pro(user):
    return user.is_pro

def delete_user(user):
    user.delete()

def change_user_password(serializer,user):
    # Check the old password
        if not user.check_password(serializer.data.get('old_password')):
            response = {"old_password": ["Wrong password."]}
            statuss = status.HTTP_400_BAD_REQUEST
            return response, statuss
        
        # Change to the new password
        if serializer.data.get('old_password') == serializer.data.get('new_password'):
            raise serializers.ValidationError('New password cannot be same as old one!')
        
        #validate new password
        password,error=validate_password(serializer.data.get('new_password'),user.username)
        if len(password)==0:
            raise serializers.ValidationError(error)
        user.set_password(serializer.data.get('new_password'))
        user.save()
        response = {
            'status': 'success',
            'message': 'Password updated successfully',
        }
        statuss = status.HTTP_200_OK
        return response,statuss

def change_user_name(serializer,user):
    username,error = validate_username(serializer.data['username'])
    if len(username)==0:
        raise serializers.ValidationError(error)
    user.username = username
    try:
        user.save()
    except:
        response = {'Success': 'Username taken!'}
        return response
        
    response = {'Success': 'Username changed'}
    return response
#sign up user
class SignUpView(generics.GenericAPIView):
    serializer_class = SignUpSerializer
    
    #POST for user signing up
    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        
        #Setting email message
        user = Account.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token
        print(request.data)
        current_site = get_current_site(request).domain

        email = prepare_verify_email(current_site,user,token)
        
        #sending mail
        Util.send_email(email)
        
        

        return Response(user_data, status=status.HTTP_201_CREATED)


#Verify email
class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description',
        type=openapi.TYPE_STRING)


    #GET 
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            #decode token to check for the user
            payload = jwt.decode(token, settings.SECRET_KEY,
                                 algorithms=["HS256"])
            
            #extracting user id from token
            user = Account.objects.get(id=payload['user_id'])
            verifying_user(user)
            return Response({'email': 'Succesfully activated'},
                    status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'},
                            status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid Token'},
                            status=status.HTTP_400_BAD_REQUEST)


#User login
class LoginView(generics.GenericAPIView):
    serializer_class = LogInSerializer

    #POST
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#Reset password mail
class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = RequestPasswordResetEmailSerializer
    
    #POST
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.data.get('email', '')
        bool,error = check_account_exist_email(email)        
        if bool:
            user = Account.objects.get(email=email)
            
            #encode user id
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            
            #create token
            token = PasswordResetTokenGenerator().make_token(user)
            
            #preparing mail
            current_site = get_current_site(request=request).domain

            email = prepare_reset_password_email(current_site,user,token,uidb64)
            
            #sending mail
            Util.send_email(email)
            
            return Response({'Success':
                            'We have sent you a link to reset password'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)


#Reset password mail
class PasswordTokenCheck(generics.GenericAPIView):
    serializer_class = PasswordTokenCheckSerializer

    def get(self, request, uidb64, token):
        try:
            #decoding token            
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(id=id)

            #validate token
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Invalid Token, Request a new one'},
                                status=status.HTTP_401_UNAUTHORIZED)

            return Response({'success': True, 'message': 'Credential Valid',
                             'uidb64': uidb64, 'token': token},
                            status=status.HTTP_200_OK)
            # check that the user havent used token twice
        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'Invalid Token, Request a new one'},
                            status=status.HTTP_401_UNAUTHORIZED)

#Setting password (from reset mail)
class SetNewPassword(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    #PUT
    def put(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'Success': True, 'message': 'Password Reset Success'},
                        status=status.HTTP_200_OK)

#change account password
class ChangePassword(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    
    #PUT
    def put(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            response,statuss = change_user_password(serializer,user)
            return Response(response, status=statuss)
            
            

#change user type
class ChangeToPro(generics.GenericAPIView):
    serializer_class = ChangeToPro
    permission_classes = (permissions.IsAuthenticated,)
    
    #PUT
    def put(self, request):
        user = self.request.user
        serializer = self.serializer_class(data=request.data)
    
        if serializer.is_valid(raise_exception=True):
            
            #Validate user input
            if check_pro(user) and serializer.data['is_pro'] == True:
                return Response({'status': 'failed',
                                'message': 'User already a pro!'}, status = status.HTTP_400_BAD_REQUEST)    
            elif check_pro(user) and serializer.data['is_pro'] == False:
                change_to_normal(user)
                response = {
                    'status': 'success',
                    'message': 'Returned back to normal!',
                }
                return Response(response, status = status.HTTP_200_OK)
            elif not check_pro(user) and serializer.data['is_pro'] == True:
                change_to_pro(user)
                response = {
                    'status': 'success',
                    'message': 'Changed to Pro!',
                }
                return Response(response, status = status.HTTP_200_OK)
            elif not check_pro(user) and serializer.data['is_pro'] == False:
                response = {
                    'status': 'failed',
                    'message': 'User already normal!',
                }
                return Response(response, status = status.HTTP_200_OK)

#change user username
class ChangeUsername(generics.GenericAPIView):
    serializer_class = ChangeUsernameSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    #PUT
    def put(self, request):
        user = self.request.user
        serializer = self.serializer_class(data=request.data)
    
        if serializer.is_valid(raise_exception=True):
            response = change_user_name(serializer,user)
            return Response(response)
#get user info
class UserInfo(generics.RetrieveAPIView):
    
    serializer_class = OwnerSerializer       
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Account.objects.all()
    
    #override get object to get logged in user
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(id=self.request.user.id)
        return obj

#Delete users account
@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def DeleteAccount(request):
    user = request.user
    try:
        userpassword=request.data['password']
    except:
        return Response({'stat': 'Failed', "message":'Please enter your password'}, status=status.HTTP_200_OK)
    user=auth.authenticate(email=user.email, password=userpassword)
    if not user:
        return Response(
            {'stat': 'incorrect password'},status=status.HTTP_400_BAD_REQUEST)
    user.delete()
    return Response({'stat': 'ok'}, status=status.HTTP_200_OK)

    
