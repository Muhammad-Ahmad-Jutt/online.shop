from django.urls import path, include
from users.views import Sign_Up_API, Sign_In_API,Log_Out_API,Password_Reset_Api_Authenticated,Password_Reset_Email_Send,Password_Reset_Api_code,RefreshAccessToken,UserProfile,GoogleLogin,VerifyUserMailSend,VerifyUser

urlpatterns = [
path('signup/', Sign_Up_API.as_view(), name='signup_api'),  # POST - Register new user
path('login/', Sign_In_API.as_view(), name='login_api'),  # POST - User login
path('logout/', Log_Out_API.as_view(), name='logout_api'),  # POST - User logout
path('password_reset_auth/', Password_Reset_Api_Authenticated.as_view(), name='password_reset_auth'),  # POST - Reset password (Authenticated user)
path("password_reset_email/", Password_Reset_Email_Send.as_view(), name='password_reset_email'),  # POST - Send password reset email
path("password_reset_code_confirm/", Password_Reset_Api_code.as_view(), name='password_reset_code_confirm'),  # POST - Confirm reset code
path("refresh_access_token/", RefreshAccessToken.as_view(), name="refresh_access_token"),  # POST - Refresh JWT access token
path("user_profile/", UserProfile.as_view(), name='user_profile'),  # GET - Fetch profile, PUT - Update profile
path("google_login/", GoogleLogin.as_view(), name='Google Login'), # POST
path("verify_account/", VerifyUserMailSend.as_view(), name='Verify Account'),# POST
path("verify_code/", VerifyUser.as_view(), name='Verify Account')# POST
    # Django's built-in authentication URLs (includes login, logout, password reset, etc.)
    # path('auth/', include('django.contrib.auth.urls')),
]
