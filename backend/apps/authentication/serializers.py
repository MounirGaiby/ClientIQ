"""
Custom JWT serializers for authentication.
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that uses email instead of username.
    """
    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Replace username field with email field if it exists
        if 'username' in self.fields:
            self.fields[self.username_field] = self.fields.pop('username')
        elif self.username_field not in self.fields:
            # If email field doesn't exist, add it
            from rest_framework import serializers
            self.fields[self.username_field] = serializers.CharField()

    def validate(self, attrs):
        # Use email for authentication instead of username
        email = attrs.get(self.username_field)
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,  # Django's authenticate still expects 'username' parameter
                password=password
            )

            if not user:
                raise serializers.ValidationError(
                    'No active account found with the given credentials'
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.'
                )

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            return data
        else:
            raise serializers.ValidationError(
                'Must include email and password.'
            )

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)
