from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 
            'profile_picture', 'bio', 'interests', 'date_joined'
        )
        read_only_fields = ('id', 'date_joined')


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user (registration)"""
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 
            'profile_picture', 'bio', 'interests', 'password', 
            'password_confirm'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def validate(self, data):
        """Ensure passwords match"""
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError(
                {"password_confirm": _("Passwords must match.")}
            )
        return data
    
    def create(self, validated_data):
        """Create a new user with encrypted password"""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            profile_picture=validated_data.get('profile_picture', None),
            bio=validated_data.get('bio', ''),
            interests=validated_data.get('interests', '')
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user authentication"""
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    
    def validate(self, data):
        """Validate and authenticate the user"""
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authentication')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')
        
        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    current_password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    
    def validate_new_password(self, value):
        """Ensure password is strong enough"""
        if len(value) < 8:
            raise serializers.ValidationError(
                _("Password must be at least 8 characters long.")
            )
        return value 