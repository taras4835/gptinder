from django.shortcuts import render
from rest_framework import viewsets, permissions, status, generics
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import login

from .models import User
from .serializers import UserSerializer, UserCreateSerializer, LoginSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model that provides CRUD operations.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        Custom permissions:
        - Allow creation without authentication
        - Only allow users to view/update/delete their own profile
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """
        Use a different serializer for user creation
        """
        if self.action == 'create':
            return UserCreateSerializer
        return self.serializer_class
    
    def get_queryset(self):
        """
        Only allow users to view/update/delete their own profile
        unless they're staff/superuser
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Return the current user's profile
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class LoginView(generics.GenericAPIView):
    """
    Login API view that returns a token
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Get or create token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        # Login the user
        login(request, user)
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user, context=self.get_serializer_context()).data
        })


class LogoutView(generics.GenericAPIView):
    """
    Logout API view that deletes the token
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        # Delete the user's token
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
