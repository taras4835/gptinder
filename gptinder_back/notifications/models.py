from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class NotificationType(models.TextChoices):
    INACTIVITY = 'inactivity', _('Inactivity')
    NEW_MATCH = 'new_match', _('New Match')
    NEW_MESSAGE = 'new_message', _('New Message')
    SYSTEM = 'system', _('System')


class Notification(models.Model):
    """
    Model for storing user notifications
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('User')
    )
    type = models.CharField(
        _('Notification Type'),
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    title = models.CharField(_('Title'), max_length=255)
    message = models.TextField(_('Message'))
    is_read = models.BooleanField(_('Is Read'), default=False)
    created_at = models.DateTimeField(_('Created At'), default=timezone.now)
    
    # For notifications related to other models
    content_type = models.CharField(_('Content Type'), max_length=50, blank=True, null=True)
    object_id = models.PositiveIntegerField(_('Object ID'), blank=True, null=True)
    
    # For email notification tracking
    email_sent = models.BooleanField(_('Email Sent'), default=False)
    email_sent_at = models.DateTimeField(_('Email Sent At'), blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.created_at.date()})"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])
    
    def mark_email_sent(self):
        """Mark notification as emailed"""
        self.email_sent = True
        self.email_sent_at = timezone.now()
        self.save(update_fields=['email_sent', 'email_sent_at'])
