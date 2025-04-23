from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class UserRecommendation(models.Model):
    """Model to store user recommendations"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendations_received'
    )
    recommended_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendations_as_recommended'
    )
    similarity_score = models.FloatField(_("Similarity Score"))
    common_interests = models.JSONField(_("Common Interests"), null=True, blank=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    is_viewed = models.BooleanField(_("Is Viewed"), default=False)
    
    # Add explanation field
    explanation = models.TextField(_("Explanation"), blank=True, null=True, 
                                  help_text=_("Personalized explanation of why these users might be interested in talking to each other"))
    
    class Meta:
        ordering = ['-similarity_score']
        unique_together = ['user', 'recommended_user']
    
    def __str__(self):
        return f"{self.user.username} - {self.recommended_user.username} ({self.similarity_score})"


class UserChat(models.Model):
    """Model to store chat sessions between users"""
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='user_chats'
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat between {', '.join([p.username for p in self.participants.all()])}"


class UserMessage(models.Model):
    """Model to store messages between users"""
    chat = models.ForeignKey(
        UserChat,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField(_("Content"))
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    is_read = models.BooleanField(_("Is Read"), default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}..."
