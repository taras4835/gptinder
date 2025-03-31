from rest_framework import serializers
from .models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    
    class Meta:
        model = Message
        fields = ('id', 'role', 'content', 'created_at')
        read_only_fields = ('id', 'created_at')


class ChatSerializer(serializers.ModelSerializer):
    """Serializer for Chat model"""
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Chat
        fields = ('id', 'user', 'title', 'created_at', 'updated_at', 'messages')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        """Create a new chat with the current user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ChatMessageRequestSerializer(serializers.Serializer):
    """Serializer for chat message requests to the AI"""
    content = serializers.CharField()


class ChatMessageResponseSerializer(serializers.Serializer):
    """Serializer for chat message responses from the AI"""
    message = MessageSerializer() 