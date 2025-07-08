# auth/admin_authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.authentication import get_authorization_header
from jewelleryapp.models import AdminLogin  # ✅ correct


class AdminJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        admin_id = validated_token.get("admin_id")

        if not admin_id:
            raise InvalidToken("Token missing admin_id")

        try:
            return AdminLogin.objects.get(id=admin_id)
        except AdminLogin.DoesNotExist:
            raise InvalidToken("Admin not found")
