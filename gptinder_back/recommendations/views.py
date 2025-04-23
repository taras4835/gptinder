from django.shortcuts import render
import numpy as np
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import UserRecommendation, UserChat, UserMessage
from .serializers import (
    UserRecommendationSerializer, UserChatSerializer, 
    UserMessageSerializer, MessageRequestSerializer
)
from .embeddings import EmbeddingService

User = get_user_model()


class UserRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for UserRecommendation model that provides list and retrieve operations.
    Also provides an action to regenerate recommendations.
    """
    serializer_class = UserRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return only the recommendations for the current user"""
        return UserRecommendation.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate or regenerate user recommendations based on user embeddings
        """
        try:
            # Initialize the embedding service
            embedding_service = EmbeddingService()
            
            # Generate or update embedding for current user
            user_embedding = embedding_service.generate_user_embedding(request.user)
            
            if not user_embedding:
                return Response(
                    {"detail": "Couldn't generate embeddings for your profile. Please add more information to your interests and bio."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate recommendations
            num_recommendations = embedding_service.generate_recommendations(request.user.id)
            
            if num_recommendations == 0:
                return Response(
                    {"detail": "No recommendations found. Try adding more to your interests and bio."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get and return the recommendations
            recommendations = UserRecommendation.objects.filter(user=request.user)
            serializer = self.get_serializer(recommendations, many=True)
            
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error generating recommendations: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        """Mark a recommendation as viewed"""
        recommendation = self.get_object()
        recommendation.is_viewed = True
        recommendation.save()
        return Response({"detail": "Recommendation marked as viewed."})


class UserChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserChat model that provides CRUD operations.
    """
    serializer_class = UserChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return only the chats the current user is participating in"""
        return UserChat.objects.filter(participants=self.request.user)
    
    @action(detail=True, methods=['post'])
    def message(self, request, pk=None):
        """Send a message in the chat"""
        chat = self.get_object()
        serializer = MessageRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create user message
            message = UserMessage.objects.create(
                chat=chat,
                sender=request.user,
                content=serializer.validated_data['content']
            )
            
            # Update chat timestamp
            chat.save()  # This updates the updated_at field
            
            return Response(UserMessageSerializer(message).data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark all messages in the chat as read for the current user"""
        chat = self.get_object()
        UserMessage.objects.filter(
            chat=chat,
            is_read=False
        ).exclude(
            sender=request.user
        ).update(is_read=True)
        
        return Response({"detail": "Messages marked as read."})


class UserMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserMessage model that provides CRUD operations.
    """
    serializer_class = UserMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return only the messages in chats the current user is participating in"""
        return UserMessage.objects.filter(chat__participants=self.request.user)
    
    def perform_create(self, serializer):
        """Set the sender to the current user when creating a message"""
        serializer.save(sender=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a message as read"""
        message = self.get_object()
        
        # Only mark as read if the current user is not the sender
        if message.sender != request.user:
            message.is_read = True
            message.save()
            
        return Response(UserMessageSerializer(message).data)
