from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'message', 'is_read', 
            'content_type', 'object_id', 'created_at'
        ]
        read_only_fields = ['id', 'type', 'title', 'message', 'content_type', 'object_id', 'created_at'] 