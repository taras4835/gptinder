from django.apps import AppConfig


class RecommendationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommendations'
    
    def ready(self):
        """Register periodic tasks when the app is ready"""
        # Import is here to avoid AppRegistryNotReady exception
        from django_celery_beat.models import PeriodicTask, IntervalSchedule
        import json
        
        # Create interval schedule if it doesn't exist
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=6,
            period=IntervalSchedule.HOURS,
        )
        
        # Create the periodic task if it doesn't exist
        PeriodicTask.objects.get_or_create(
            name='Analyze user messages for recommendations',
            task='recommendations.tasks.analyze_messages_for_recommendations',
            interval=schedule,
            kwargs=json.dumps({}),
            defaults={
                'enabled': True,
                'description': 'Periodically analyzes message similarities between users with similar embeddings and creates recommendations if they might be useful to each other',
            },
        )
