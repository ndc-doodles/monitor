# jewelleryapp/auth/combined_auth.py

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from .admin_authentication import AdminJWTAuthentication

class CombinedJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        jwt_auth = JWTAuthentication()
        admin_auth = AdminJWTAuthentication()

        for auth in (admin_auth, jwt_auth):
            try:
                return auth.authenticate(request)
            except Exception:
                continue

        raise AuthenticationFailed("No valid authentication token found")
