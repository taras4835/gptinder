from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom user model that extends the default Django user model.
    Added profile picture field.
    """
    profile_picture = models.ImageField(
        _("Profile Picture"), 
        upload_to="profile_pictures/", 
        null=True, 
        blank=True
    )
    bio = models.TextField(_("Bio"), max_length=500, blank=True)
    interests = models.TextField(_("Interests"), max_length=500, blank=True)
    
    # Embedding vector for user interests
    embedding = models.JSONField(_("Embedding Vector"), null=True, blank=True)
    
    # Last time the embedding was updated
    embedding_updated_at = models.DateTimeField(_("Embedding Updated At"), null=True, blank=True)
    
    def __str__(self):
        return self.username
