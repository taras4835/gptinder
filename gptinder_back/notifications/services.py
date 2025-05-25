import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from users.models import User
from .models import Notification, NotificationType

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing user notifications"""
    
    @staticmethod
    def create_notification(user, type, title, message, content_type=None, object_id=None):
        """Create a new notification for a user"""
        try:
            notification = Notification.objects.create(
                user=user,
                type=type,
                title=title,
                message=message,
                content_type=content_type,
                object_id=object_id
            )
            return notification
        except Exception as e:
            logger.error(f"Error creating notification for user {user.id}: {str(e)}")
            return None
    
    @staticmethod
    def mark_as_read(notification_id, user_id):
        """Mark notification as read"""
        try:
            notification = Notification.objects.get(id=notification_id, user_id=user_id)
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            logger.warning(f"Notification {notification_id} not found for user {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error marking notification {notification_id} as read: {str(e)}")
            return False
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all user notifications as read"""
        try:
            Notification.objects.filter(user_id=user_id, is_read=False).update(is_read=True)
            return True
        except Exception as e:
            logger.error(f"Error marking all notifications as read for user {user_id}: {str(e)}")
            return False
    
    @staticmethod
    def send_notification_email(notification):
        """Send email for a notification"""
        if not notification.user.email:
            logger.warning(f"Cannot send email to user {notification.user.id} - no email address")
            return False
            
        try:
            subject = notification.title
            
            # Render HTML message
            html_message = render_to_string('notifications/email_notification.html', {
                'notification': notification,
                'user': notification.user,
                'site_name': settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'GPTinder',
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else '',
            })
            
            # Plain text version
            plain_message = strip_tags(html_message)
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            # Mark as sent
            notification.mark_email_sent()
            return True
        except Exception as e:
            logger.error(f"Error sending notification email to {notification.user.email}: {str(e)}")
            return False
    
    @classmethod
    def find_inactive_users(cls, days=14):
        """Find users who haven't been active for a specified number of days"""
        inactivity_threshold = timezone.now() - timedelta(days=days)
        
        # Find users who haven't been active since the threshold
        # and haven't received an inactivity notification in the last week
        
        # First, get user IDs who received inactivity notifications in the last week
        week_ago = timezone.now() - timedelta(days=7)
        recently_notified_user_ids = Notification.objects.filter(
            type=NotificationType.INACTIVITY,
            created_at__gte=week_ago
        ).values_list('user_id', flat=True)
        
        # Then get inactive users excluding those recently notified
        inactive_users = User.objects.filter(
            last_activity__lt=inactivity_threshold,
            is_active=True
        ).exclude(
            id__in=recently_notified_user_ids
        )
        
        return inactive_users
    
    @classmethod
    def notify_inactive_users(cls, days=14):
        """Create notifications for inactive users"""
        inactive_users = cls.find_inactive_users(days)
        notification_count = 0
        
        for user in inactive_users:
            title = "Мы скучаем по вам!"
            message = f"Вы не заходили в GPTinder уже {days} дней. У нас появились новые интересные пользователи - возвращайтесь!"
            
            notification = cls.create_notification(
                user=user,
                type=NotificationType.INACTIVITY,
                title=title,
                message=message
            )
            
            if notification:
                cls.send_notification_email(notification)
                notification_count += 1
        
        return notification_count 