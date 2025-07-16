from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from .models import AdminLogin

User = get_user_model()

class CombinedJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        # Check for admin token
        if 'admin_id' in validated_token:
            try:
                admin = AdminLogin.objects.get(id=validated_token['admin_id'])
                admin.is_admin = True
                return admin
            except AdminLogin.DoesNotExist:
                raise AuthenticationFailed('Admin not found')

        # Check for regular user token
        if 'user_id' in validated_token:
            try:
                user = User.objects.get(id=validated_token['user_id'])
                user.is_admin = False
                return user
            except User.DoesNotExist:
                raise AuthenticationFailed('User not found')

        raise AuthenticationFailed("Token contained no recognizable user identification")
