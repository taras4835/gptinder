from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer
from .services import NotificationService


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Notification model
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only user's notifications
        """
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark a notification as read
        """
        result = NotificationService.mark_as_read(pk, request.user.id)
        if result:
            return Response({'status': 'notification marked as read'})
        return Response(
            {'error': 'notification not found or already read'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Mark all user's notifications as read
        """
        result = NotificationService.mark_all_as_read(request.user.id)
        if result:
            return Response({'status': 'all notifications marked as read'})
        return Response(
            {'error': 'error marking notifications as read'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
