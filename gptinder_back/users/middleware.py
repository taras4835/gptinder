from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class LastActivityMiddleware:
    """
    Middleware to track last user activity
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process request
        response = self.get_response(request)
        
        # Update last activity for authenticated users
        if request.user.is_authenticated:
            try:
                # Only update if the last update was more than 5 minutes ago
                # to avoid too many database writes
                now = timezone.now()
                if (not request.user.last_activity or 
                        (now - request.user.last_activity).total_seconds() > 300):
                    request.user.last_activity = now
                    request.user.save(update_fields=['last_activity'])
            except Exception as e:
                logger.error(f"Error updating last_activity for user {request.user.id}: {str(e)}")
        
        return response 