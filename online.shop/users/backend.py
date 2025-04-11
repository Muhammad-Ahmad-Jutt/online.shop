from django.contrib.auth.backends import BaseBackend
from users.models import CoreUser
class CUSTOMEMAILBACKEND(BaseBackend):

    def authenticate(self, request,email=None, password=None, **kwargs):
        try:
            user = CoreUser.objects.get(email=email)
            if user.check_password(password):
                return user
            else:
                return None
        except CoreUser.DoesNotExist:
            return None

    def get_user(self,id):
        try:
            return CoreUser.objects.get(id=id)
        except CoreUser.DoesNotExist:
            return None

