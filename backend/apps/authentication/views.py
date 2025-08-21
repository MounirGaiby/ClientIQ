from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django_tenants.utils import tenant_context
from apps.tenants.models import Tenant

User = get_user_model()


class CustomLoginView(APIView):
    permission_classes = []
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return Response(
                {'error': 'Tenant context required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Authenticate user within tenant context
        user = None
        try:
            with tenant_context(tenant):
                # Import the tenant user model directly instead of using get_user_model()
                from apps.users.models import CustomUser as TenantUserModel
                
                user = TenantUserModel.objects.get(email=email, is_active=True)
                
                if user.check_password(password):
                    # User authenticated successfully
                    pass
                else:
                    user = None
        except TenantUserModel.DoesNotExist:
            # User doesn't exist in this tenant
            print(f"User {email} not found in tenant {tenant.schema_name}")
            user = None
        except Exception as e:
            # Any other error during authentication
            print(f"Authentication error: {e}")
            user = None
        
        if user:
            if user.is_active:
                # Generate JWT tokens manually to avoid model mismatch
                from rest_framework_simplejwt.tokens import AccessToken
                from django.contrib.auth import get_user_model
                
                # Create tokens without using OutstandingToken (blacklist feature)
                access_token = AccessToken()
                access_token['user_id'] = user.pk
                access_token['email'] = user.email
                
                # For now, we'll skip refresh tokens to avoid the model mismatch
                # This is a temporary solution for the multi-tenant setup
                return Response({
                    'access': str(access_token),
                    'user': {
                        'id': user.pk,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
                })
            else:
                return Response(
                    {'error': 'Account is disabled'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response(
                {'error': 'Invalid email or password'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )


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
                "full_name": user.get_full_name() if hasattr(user, 'get_full_name') else f"{user.first_name} {user.last_name}".strip(),
                "department": getattr(user, 'department', ''),
                "job_title": getattr(user, 'job_title', ''),
                "phone_number": getattr(user, 'phone_number', ''),
                "is_admin": getattr(user, 'is_admin', False),
                "is_active": user.is_active,
                "date_joined": user.date_joined,
            }
        })
