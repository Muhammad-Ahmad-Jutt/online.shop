import logging
from rest_framework import serializers
from users.models import CoreUser,PasswordReset,Verify_Email
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from users.tasks import send_mail_to_user
from rest_framework_simplejwt.views import token_refresh
from datetime import timedelta
from django.utils import timezone
import requests,json
# Configure logging
logger = logging.getLogger(__name__)
class VerifyUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()
    def validate(self,data):
        try:
            email = data['email']
            code = data['code'] 
            user = CoreUser.objects.filter(email = email).first()
            data['user']=user
            if not user:
                raise serializers.ValidationError(f"Email is not registered")
            else:
                code = Verify_Email.objects.filter(user_id=user,code=code,used=False,activate=True).first()
                if code.is_expired():
                    raise serializers.ValidationError("Code is used or expired")
                else:
                    code.used=True
                    code.activate=False
                    code.save()
        except Exception as e:
            logger.error(f'[Verify User Serializer] Throws exception {e}')
            raise serializers.ValidationError(f"Invalid or Expired Code ------->,{e}")
        return data
    def update_user_status(self, validated_data):
        user = validated_data['user']
        user.verified=True
        user.save()
        send_mail_to_user.delay(user.email,'Your email has been verified',"Notification for Verification")
class VerifyUserMailSendSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self,data):
        try:
            email = data["email"]

            if not email:
                raise serializers.ValidationError('No email provided')
            
            user = CoreUser.objects.filter(email=email).first()
            if user.verified==True:
                raise serializers.ValidationError("User is already verified")
            ten_minutes_ago = timezone.now() - timedelta(minutes=10)
            request_count = Verify_Email.objects.filter(user_id=user, created_at__gte=ten_minutes_ago, used=False).count()
            if request_count>=2:
                raise serializers.ValidationError("User already have two pending request wait for 10 minutes")
            else:
                deactivate_previous_code = Verify_Email.objects.filter(user_id=user).all().update(activate=False)
                code = Verify_Email(user_id=user)
                code.generate_code()
                code.save()
                send_mail_to_user.delay(user.email,f'Verify email with this code --->{code.code}', 'Verify Email Address')
        except Exception as e:
            logger.error(f'[VerifyUserMailSendSerializer] throws exception {e}')
            raise serializers.ValidationError(f"Invalid or Expired Code---->,{e}")
        return data
class GoogleLoginSerializer(serializers.Serializer):
    google_token = serializers.CharField()

    def validate(self, data):
        try:
            google_token = data["google_token"]
            payload = {'access_token': google_token}
            google_response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params=payload)
            data = google_response.json()
            if 'error' in data:
                raise serializers.ValidationError("Wrong/Expired Google Token")
            else:
                email = data['email']
                name = data['name']
                first_name = data['given_name']
                last_name = data['family_name']
                profile_link = data['picture']
                verified=True
                user,created = CoreUser.objects.get_or_create(name=name, email=email,first_name=first_name, last_name=last_name, profile_link=profile_link, verified=True,google_token=google_token)
                if created:
                    send_mail_to_user.delay(email, 'To Generate your new password, visit reset password in account settings', 'Password Generate Notification')

        except Exception as e:
            logger.error(f'[Continue with google] throws exception {e}')
            raise serializers.ValidationError(f"Invalid or Expired Code---->,{e}")
        return {"user":user}
class UserProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='phone_number.as_e164', read_only=True)

    class Meta:
        model = CoreUser
        fields = ['name', 'first_name', 'age', 'email', 'phone_number', 'created_at', 'last_login']
        read_only_fields = [ 'email', 'created_at', 'last_login'] 
    def validate(self, data):
        if not data:
            raise serializers.ValidationError("No update data provided.")
        return data
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, data):
        try:
            logger.info("Refresh Token Serializer")
            old_token = data['refresh_token']
            new_token = RefreshToken(old_token)
            data['access_token']=str(new_token.access_token)
        except Exception as e:
            logger.error(f'[Refresh Access Token] throws exception {e}')
            raise serializers.ValidationError(f"Invalid or Expired Code---->,{e}")
        return data
class PasswordChangeEmailCode(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()
    password = serializers.CharField(write_only=True)
    def validate(self,data):
        try:
            logger.info("Password Change with Email Serializer")
            email = data['email']
            password = data['password']
            code = data['code']
            user = CoreUser.objects.filter(email=email).first()
            password_reset = PasswordReset.objects.filter(user_id=user, code=code, used=False,activate=True).first()
            if not password_reset or password_reset.is_expired():  # Check expiration here
                raise serializers.ValidationError("Invalid or expired code.")
            data['message']='Code Confirmed'
            data['user']=user
            data['new_password']=password
        except Exception as e:
            logger.error(f'[Password code verify] throws exception {e}')
            raise serializers.ValidationError(f"Invalid or Expired Code---->,{e}")

        return data
    def update_password(self):
        """Update the user's password after validation"""
        user = self.validated_data["user"]
        new_password = self.validated_data["new_password"]
        user.verified=True
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Mark password reset code as used
        password_reset = PasswordReset.objects.filter(user_id=user, code=self.validated_data["code"]).first()
        if password_reset:
            password_reset.mark_as_used()
        send_mail_to_user.delay(self.validated_data['email'],'Password Changed Successfull','Password Change Notification')

class EmailPassResetRequest(serializers.Serializer):
    email = serializers.EmailField()
    def validate(self,data):
        try:
            logger.info("Email Password Rest Request Serializer")
            email=data['email']
            
            user = CoreUser.objects.filter(email=email).first()
            request_count = PasswordReset.objects.filter(user_id=user, used=False).all()
            req_count=0
            for request in request_count:
                if request.is_expired():
                    continue
                else:
                    req_count+=1
            if req_count>=2:
                raise serializers.ValidationError("User already have two pending request wait for 10 minutes")
            else:
                deactivate_previous_code=PasswordReset.objects.filter(user_id=user).all().update(activate=False)
                subject = 'Applicaiton Password Reset Code'
                code = PasswordReset(user_id=user)
                code.generate_code()
                code.save()
                message = f"Your Password Reset Code is {code.code} \n Code will be expire after 10 minutes."
                send_mail_to_user.delay(email,message,subject)
                data["status"]=True
        except Exception as e:
            logger.error(f'[send_email_on_account_registration] throws exception {e}')
            raise serializers.ValidationError("Email not found")
        return data


class AuthPassReset(serializers.Serializer):
    access_token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    def validate(self, attrs):
        logger.info("Auth Pass Reset Serializer")

        access_token = attrs.get("access_token")
        password = attrs.get('password')
        if not access_token:
            raise serializers.ValidationError("Access token is required.")

        try:
            token = AccessToken(access_token)
            user_id = token.payload['user_id']
            user = CoreUser.objects.get(id=user_id)
            attrs["user"] = user
            attrs['user_name']=user.email
            attrs['new_password']=password
        except Exception:
            logger.error("Invalid or expired access token.", exc_info=True)
            raise serializers.ValidationError("Invalid or expired access token.")

        return attrs
    def update_password(self):
        """Update the user's password after validation"""
        user = self.validated_data["user"]
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()


class LogOutAPISerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        logger.info("Logout Api Serializer")

        refresh_token = attrs.get("refresh_token")
        if not refresh_token:
            raise serializers.ValidationError("Refresh token is required.")

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the token
        except Exception:
            logger.error("Invalid or expired refresh token.", exc_info=True)
            raise serializers.ValidationError("Invalid or expired refresh token.")

        return attrs



class EmailSignInSerializer(serializers.Serializer):
    """Serializer for User model with password hashing and debugging."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self,data):
        try:
            logger.info("Email Sign In Serializer")

            email = data.get('email')
            password = data.get('password')
            if not email or not password:
                raise serializers.ValidationError('Both email and password required to authenticate')
            user = authenticate(request=self.context.get('request'), email=email, password=password)  # Change `username=email`
            if not user:
                raise serializers.ValidationError("Invalid credentials, please try again.")
            if not user.is_active:
                raise serializers.ValidationError("This account is inactive.")
            data["user"] = user
            return data
        except Exception as e:
            logger.error(f"Error login user: {str(e)}", exc_info=True)
            raise serializers.ValidationError({"error": f"User login Failed: {str(e)}"})

class UserSignUpSerializer(serializers.ModelSerializer):
    """Serializer for User model with password hashing and debugging."""

    class Meta:
        model = CoreUser
        fields = ["name", "first_name", "last_name", "age", "email", "password", "phone_number", "permission"]
        extra_kwargs = {"password": {"write_only": True}}  # Hide password in API response

    def create(self, validated_data):
        """Ensure password is hashed before saving, with debugging enabled."""
        try:
            logger.info("Sign Up Serializer")

            logger.info("Starting user creation process...")
            logger.debug(f"Received validated data: {validated_data}")

            password = validated_data.pop("password", None)  # Extract password
            user = CoreUser(**validated_data)  # Initialize user instance

            if password:
                user.set_password(password)  # Hash password before saving
                logger.debug("Password has been securely hashed.")

            user.save()
            logger.info(f"User {user.email} created successfully!")

            return user

        except Exception as e:
            logger.error(f"Error creating user: {str(e)}", exc_info=True)
            raise serializers.ValidationError({"error": f"User creation failed: {str(e)}"})
