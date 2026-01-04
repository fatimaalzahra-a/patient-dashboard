from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        # create_user handles password salting and hashing automatically
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # adds data to the encrypted token
        token = super().get_token(user)

        token['username'] = user.username
        token['permissions'] = list(user.get_custom_permissions())
        # Using getattr in case the profile is missing during dev
        token['department'] = getattr(user.profile, 'department', None) if hasattr(user, 'profile') else None

        return token

    def validate(self, attrs):
        # adds data to the JSON response
        data = super().validate(attrs)


        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'department': getattr(self.user.profile, 'department', None) if hasattr(self.user, 'profile') else None,
            'permissions': list(self.user.get_custom_permissions())
        }

        return data
