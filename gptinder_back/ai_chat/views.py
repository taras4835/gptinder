from django.shortcuts import render
import openai
import json
import numpy as np
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Chat, Message
from .serializers import (
    ChatSerializer, MessageSerializer, 
    ChatMessageRequestSerializer, ChatMessageResponseSerializer
)


class ChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Chat model that provides CRUD operations.
    """
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only the chats belonging to the current user
        """
        return Chat.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def message(self, request, pk=None):
        """
        Send a message to the AI and get a response
        """
        chat = self.get_object()
        serializer = ChatMessageRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create user message
            user_message = Message.objects.create(
                chat=chat,
                role='user',
                content=serializer.validated_data['content']
            )
            
            # Get all previous messages in the chat for context
            messages = []
            
            # Add system message
            messages.append({
                'role': 'system',
                'content': 'You are a helpful AI assistant talking with a human. Be friendly and concise.'
            })
            
            # Add chat history
            for msg in chat.messages.all():
                messages.append({
                    'role': msg.role,
                    'content': msg.content
                })
            
            try:
                # Call OpenAI API
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=1000
                )
                
                # Extract assistant response
                assistant_response = response.choices[0].message.content
                
                # Create assistant message
                assistant_message = Message.objects.create(
                    chat=chat,
                    role='assistant',
                    content=assistant_response
                )
                
                # Update embedding for user message (for recommendations)
                try:
                    embedding_response = openai.embeddings.create(
                        model="text-embedding-ada-002",
                        input=user_message.content
                    )
                    embedding = embedding_response.data[0].embedding
                    user_message.embedding = embedding
                    user_message.save()
                except Exception as e:
                    # Continue even if embedding fails
                    print(f"Embedding failed: {str(e)}")
                
                # Update chat timestamp
                chat.save()  # This updates the updated_at field
                
                return Response({
                    'message': MessageSerializer(assistant_message).data
                })
                
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
