from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Chat(models.Model):
    """Model to store chat sessions with AI"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_chats'
    )
    title = models.CharField(_("Title"), max_length=255, blank=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title or 'Untitled'} - {self.user.username}"


class Message(models.Model):
    """Model to store individual messages in a chat"""
    ROLE_CHOICES = (
        ('user', _('User')),
        ('assistant', _('Assistant')),
        ('system', _('System')),
    )
    
    chat = models.ForeignKey(
        Chat, 
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(_("Role"), max_length=10, choices=ROLE_CHOICES)
    content = models.TextField(_("Content"))
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    
    # Store embedding vector for the message content (for recommendation purposes)
    embedding = models.JSONField(_("Embedding"), null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:30]}..."
