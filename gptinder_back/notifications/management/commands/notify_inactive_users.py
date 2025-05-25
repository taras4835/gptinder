import logging
from django.core.management.base import BaseCommand
from notifications.services import NotificationService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Notify users who have been inactive for a specified number of days'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=14,
            help='Days of inactivity before sending notification'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        self.stdout.write(f"Finding users inactive for {days} days...")
        
        try:
            # Find inactive users
            inactive_users = NotificationService.find_inactive_users(days)
            count = inactive_users.count()
            
            if count == 0:
                self.stdout.write(self.style.SUCCESS(
                    "No inactive users found requiring notification."
                ))
                return
                
            self.stdout.write(f"Found {count} inactive users.")
            
            # Send notifications
            notification_count = NotificationService.notify_inactive_users(days)
            
            self.stdout.write(self.style.SUCCESS(
                f"Successfully sent {notification_count} notifications to inactive users"
            ))
            
        except Exception as e:
            logger.error(f"Error notifying inactive users: {str(e)}")
            self.stdout.write(self.style.ERROR(
                f"Error notifying inactive users: {str(e)}"
            )) 