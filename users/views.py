from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from users.permissions import IsAuthenticatedAndVerified
from rest_framework.response import Response
from rest_framework import status   
<<<<<<< HEAD
from users.serializer import UserSignUpSerializer,EmailSignInSerializer,LogOutAPISerializer,AuthPassReset,EmailPassResetRequest,PasswordChangeEmailCode,RefreshTokenSerializer,UserProfileSerializer,GoogleLoginSerializer,VerifyUserMailSendSerializer
=======
from users.serializer import UserSignUpSerializer,EmailSignInSerializer,LogOutAPISerializer,AuthPassReset,EmailPassResetRequest,PasswordChangeEmailCode,RefreshTokenSerializer,UserProfileSerializer,GoogleLoginSerializer,VerifyUserMailSendSerializer,VerifyUserSerializer
>>>>>>> master
from django.contrib.auth.models import update_last_login
from django.contrib.auth import logout
import datetime
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken,OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
import requests
<<<<<<< HEAD
# class VerifyUser(APIView):
#     permission_classes=[IsAuthenticated]
#     def post(self,request):
#         try:
#             serializer=VerifyUserSerializer(data = request.data)
#             if serializer.is_valid():
#                 serializer.update_verification()
#             else:
#                 return Response({
#                     "success": False,
#                     "errors": serializer.errors
#                     }, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#                 return Response({
#                     "success":False,
#                     "message":f"Unexpected error--> {str(e)}"
#                 }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
=======
class VerifyUser(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            serializer=VerifyUserSerializer(data = request.data)
            if serializer.is_valid():
                serializer.update_user_status(serializer.validated_data)
                return Response({
                    "success":True,
                    "message":"Email Verified Correctly"
                },status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "errors": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                return Response({
                    "success":False,
                    "message":f"Unexpected error--> {str(e)}"
                }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
>>>>>>> master
class VerifyUserMailSend(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            serializer = VerifyUserMailSendSerializer(data=request.data)
            if serializer.is_valid():
                response={
                    "success":True,
                    "message":"Mail Send Successfull"
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response({
                        "success": False,
                        "errors": serializer.errors
                        }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success":False,
                "message":f"Unexpected error--> {str(e)}"
            }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
class GoogleLogin(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        try:
            serializer = GoogleLoginSerializer(data = request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                response={
                    "success": True,
                    "tokens": user.tokens(),
                    "email": user.email
                }
                return Response(response)
            else:
                return Response({
                        "success": False,
                        "errors": serializer.errors
                        }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                return Response({
                    "success":False,
                    "message":f"Unexpected error--> {str(e)}"
                }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
class UserProfile(APIView):
    permission_classes=[IsAuthenticatedAndVerified]
    def get(self, request):
        try:
            user = request.user
            serializer = UserProfileSerializer(user, context={"request":request})
            return Response({"success": True,"user_info":serializer.data})

        except Exception as e:
            return Response({
                "success": False,
                "message": f"Unexpected error --> {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            user = request.user
            serializer = UserProfileSerializer(user,data=request.data, context={"request":request}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success":True,
                    "Changed Values":serializer.validated_data
                })
            else:
                return Response({
                    "success": False,
                    "errors": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success":False,
                "message":f"Unexpected error--> {str(e)}"
            }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
class RefreshAccessToken(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            serializer = RefreshTokenSerializer(data=request.data)
            if serializer.is_valid():
                return Response({"success":True,"message": "Token Refreshed","access_token":serializer.validated_data['access_token'], "refresh_token":serializer.validated_data['refresh_token']}, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "errors": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Unexpected error --> {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Password_Reset_Api_code(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try:
            email = request.data.get('email')
            password= request.data.get('password')
            code = request.data.get('code')
            
            serializer = PasswordChangeEmailCode(data={"email":email, "password":password, "code":code})
            if serializer.is_valid():
                serializer.update_password()
                return Response({"message": "Password Reset successful.","User":email}, status=status.HTTP_200_OK)

            else:
                return Response({
                "success": False,
                "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Unexpected error --> {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Password_Reset_Email_Send(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            if not request.data.get('email'):
                return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
            email = request.data.get("email")

            serializer = EmailPassResetRequest(data={"email":email})
            if serializer.is_valid():
                return Response({"success":serializer.validated_data['status'],"message": "Password Mail is in Queue."}, status=status.HTTP_200_OK)
            else:
                return Response({
                "success": False,
                "errors": serializer.errors,
                "message": "Data is incomplete"
                }, status=status.HTTP_400_BAD_REQUEST) 
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Unexpected error --> {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Password_Reset_Api_Authenticated(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            if not request.data.get('password') or len(str(request.data.get('password')))<8:
                return Response({"error": "Password of 8 Chars is required."}, status=status.HTTP_400_BAD_REQUEST)
            auth_header = request.headers.get("Authorization")
            password = request.data.get('password')
            if not auth_header or not auth_header.startswith("Bearer "):
                return Response({"error": "Access token required."}, status=status.HTTP_400_BAD_REQUEST)

            access_token = auth_header.split(" ")[1]
            serializer = AuthPassReset(data={"access_token": access_token,'password':password})
            if serializer.is_valid():
                serializer.update_password()
                return Response({"message": "Password Reset successful.","User":serializer.validated_data['user_name']}, status=status.HTTP_200_OK)
            else:
                return Response({
                "success": False,
                "errors": serializer.errors,
                "message": "Data is incomplete"
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Unexpected error --> {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Log_Out_API(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"error": "Refresh token required."}, status=status.HTTP_400_BAD_REQUEST)

        refresh_token = auth_header.split(" ")[1]
        serializer = LogOutAPISerializer(data={"refresh_token": refresh_token})
        
        if serializer.is_valid():
            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Sign_In_API(APIView):
    """ API for User SignIn"""
    def post(self,request):
        try:
            serializer = EmailSignInSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                update_last_login(None, user) 
                response = {
                    "success": True,
                    "tokens": user.tokens(),
                    "email": user.email,
                    "login_time":user.last_login
                }
                return Response(response, status=status.HTTP_201_CREATED) 
            else:
                return Response({
                "success": False,
                "errors": serializer.errors,
                "message": "Invalid or Incomplete Credientials"
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Unexpected error --> {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Sign_Up_API(APIView):
    """API for User Signup"""

    def post(self, request):
        try:
            serializer = UserSignUpSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                response = {
                    "success": True,
                    "tokens": user.tokens(),
                    "email": user.email
                }
                return Response(response, status=status.HTTP_201_CREATED) 
            
            return Response({
                "success": False,
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "success": False,
                "message": f"Unexpected error --> {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
