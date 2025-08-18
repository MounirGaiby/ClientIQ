"""
Views for authentication app.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


class LogoutView(APIView):
    """
    Logout view that blacklists the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"success": True, "message": "Successfully logged out."}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"success": False, "error": "Invalid token."}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class CurrentUserView(APIView):
    """
    Get current user information.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "success": True,
            "data": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": user.full_name,
                "user_type": user.user_type,
                "department": user.department,
                "job_title": user.job_title,
                "is_tenant_admin": user.is_tenant_admin,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }
        })
