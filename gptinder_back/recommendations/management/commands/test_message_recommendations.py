from django.core.management.base import BaseCommand
from django.utils import timezone

from recommendations.tasks import analyze_messages_for_recommendations


class Command(BaseCommand):
    help = 'Test the message analysis recommendation task'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting message analysis for recommendations...'))
        start_time = timezone.now()
        
        # Run the task synchronously (not as Celery task)
        result = analyze_messages_for_recommendations()
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write(self.style.SUCCESS(
            f'Completed in {duration:.2f} seconds. {result}'
        )) 