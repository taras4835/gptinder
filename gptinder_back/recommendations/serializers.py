from rest_framework import serializers
from users.serializers import UserSerializer
from .models import UserRecommendation, UserChat, UserMessage


class UserRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for UserRecommendation model"""
    recommended_user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserRecommendation
        fields = (
            'id', 'recommended_user', 'similarity_score', 
            'common_interests', 'created_at', 'is_viewed',
            'explanation'
        )
        read_only_fields = ('id', 'recommended_user', 'similarity_score', 'common_interests', 'created_at', 'explanation')


class UserMessageSerializer(serializers.ModelSerializer):
    """Serializer for UserMessage model"""
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_profile_picture = serializers.ImageField(source='sender.profile_picture', read_only=True)
    
    class Meta:
        model = UserMessage
        fields = (
            'id', 'sender', 'sender_username', 'sender_profile_picture',
            'content', 'created_at', 'is_read'
        )
        read_only_fields = ('id', 'sender', 'sender_username', 'sender_profile_picture', 'created_at')
    
    def create(self, validated_data):
        """Set the sender to the current user"""
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class UserChatSerializer(serializers.ModelSerializer):
    """Serializer for UserChat model"""
    participants = UserSerializer(many=True, read_only=True)
    messages = UserMessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = UserChat
        fields = ('id', 'participants', 'created_at', 'updated_at', 'messages', 'last_message')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_last_message(self, obj):
        """Get the last message in the chat"""
        message = obj.messages.last()
        if message:
            return UserMessageSerializer(message).data
        return None
    
    def create(self, validated_data):
        """Create a new chat and add the current user as a participant"""
        participant_ids = self.context['request'].data.get('participants', [])
        
        # Create the chat
        chat = UserChat.objects.create()
        
        # Add the current user as a participant
        chat.participants.add(self.context['request'].user)
        
        # Add other participants
        for participant_id in participant_ids:
            chat.participants.add(participant_id)
        
        return chat


class MessageRequestSerializer(serializers.Serializer):
    """Serializer for message requests between users"""
    content = serializers.CharField() 