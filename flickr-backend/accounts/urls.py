from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView


app_name = 'accounts'

urlpatterns = [
#sign user up
path('sign-up/', SignUpView.as_view(), name="signup"),

#change user's password
path('change-password/', ChangePassword.as_view(), name='change-password'),

#change user's username
path('change-username/', ChangeUsername.as_view(), name='change-username'),

#resend's verify mail 
path('resend-verify-mail/', ResendMailView.as_view(), name='resend-verify'),

#verify user's mail
path('email-verify/', VerifyEmail.as_view(), name="email-verify"),

#reset users password
path('password-reset-email', RequestPasswordResetEmail.as_view(),
     name="reset=pass"),

#log user in
path('login/', LoginView.as_view(), name="login"),

#reset user's password
path('password-reset/<uidb64>/<token>/', PasswordTokenCheck.as_view(),
     name="password-reset-confirm"),

#setting new password after reset
path('password-reset-complete/', SetNewPassword.as_view(),
     name="password-reset-complete"),

#refresh token api
path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

#delete user's account
path('delete-account/', DeleteAccount, name='delete-account'),

#change account type
path('change-to-pro/', ChangeToPro.as_view(), name="change-to-pro"),

#get account info
path('user-info/', UserInfo.as_view(), name="user-info"),

#get,put profile details of a specific user 
path('<int:id>', UserDetailList.as_view(), name='Userdetail'),

path('profile-pic', upload_profile, name='upload_profile'),

path('cover-photo', upload_cover, name='upload_cover'),

# Contacts
path('follow/<int:userpk>', follow_unfollow, name='follow_unfollow'),
# get the favourites photos list API
path('followers', followers_list, name='followers_list'),
path('following', following_list, name='following_list'),
path('following/<int:userpk>', user_following, name='user_following'),

]
