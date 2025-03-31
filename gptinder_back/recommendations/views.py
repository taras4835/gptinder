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
from ai_chat.models import Message as AIMessage

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
        Generate or regenerate user recommendations based on chat history
        """
        # Delete existing recommendations
        UserRecommendation.objects.filter(user=request.user).delete()
        
        # Get all users who have spoken with the AI
        users_with_chats = User.objects.filter(
            ~Q(id=request.user.id),  # Exclude the current user
            ai_chats__messages__embedding__isnull=False  # Users with message embeddings
        ).distinct()
        
        if not users_with_chats.exists():
            return Response({"detail": "No users with chat history found for recommendations."})
        
        # Get the current user's chat messages with embeddings
        user_messages = AIMessage.objects.filter(
            chat__user=request.user,
            embedding__isnull=False
        )
        
        if not user_messages.exists():
            return Response({"detail": "You don't have enough chat history for recommendations."})
        
        # Calculate average embeddings for the current user
        user_embeddings = [np.array(msg.embedding) for msg in user_messages]
        user_avg_embedding = np.mean(user_embeddings, axis=0)
        
        recommendations = []
        
        for other_user in users_with_chats:
            # Get the other user's messages with embeddings
            other_user_messages = AIMessage.objects.filter(
                chat__user=other_user,
                embedding__isnull=False
            )
            
            if not other_user_messages.exists():
                continue
            
            # Calculate average embeddings for the other user
            other_user_embeddings = [np.array(msg.embedding) for msg in other_user_messages]
            other_user_avg_embedding = np.mean(other_user_embeddings, axis=0)
            
            # Calculate cosine similarity
            similarity = np.dot(user_avg_embedding, other_user_avg_embedding) / (
                np.linalg.norm(user_avg_embedding) * np.linalg.norm(other_user_avg_embedding)
            )
            
            # Determine common interests (topics)
            # This is a simplified approach - in a real app, you might use more sophisticated topic modeling
            user_topics = set([word.lower() for msg in user_messages for word in msg.content.split() if len(word) > 5])
            other_user_topics = set([word.lower() for msg in other_user_messages for word in msg.content.split() if len(word) > 5])
            common_topics = user_topics.intersection(other_user_topics)
            
            # Create the recommendation
            recommendation = UserRecommendation.objects.create(
                user=request.user,
                recommended_user=other_user,
                similarity_score=float(similarity),
                common_interests=list(common_topics)[:10]  # Limit to 10 common topics
            )
            
            recommendations.append(recommendation)
        
        # Sort by similarity score and return
        recommendations.sort(key=lambda x: x.similarity_score, reverse=True)
        serializer = self.get_serializer(recommendations, many=True)
        
        return Response(serializer.data)
    
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
