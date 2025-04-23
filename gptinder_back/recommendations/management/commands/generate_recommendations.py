from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recommendations.embeddings import EmbeddingService

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates recommendations for all users based on their embeddings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Generate recommendations only for the specified username',
        )
        parser.add_argument(
            '--explain',
            action='store_true',
            help='Show explanations for recommendations',
        )

    def handle(self, *args, **options):
        embedding_service = EmbeddingService()
        username = options.get('user')
        show_explanations = options.get('explain', False)
        
        if username:
            try:
                user = User.objects.get(username=username)
                self.generate_for_user(user, embedding_service, show_explanations)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User {username} not found')
                )
        else:
            users = User.objects.all()
            for user in users:
                self.generate_for_user(user, embedding_service, show_explanations)
    
    def generate_for_user(self, user, embedding_service, show_explanations):
        self.stdout.write(f'Generating recommendations for {user.username}...')
        
        try:
            # Generate recommendations
            recommendations_count = embedding_service.generate_recommendations(user.id)
            
            if recommendations_count == 0:
                self.stdout.write(
                    self.style.WARNING(f'No recommendations were generated for {user.username}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Generated {recommendations_count} recommendations for {user.username}')
                )
                
                # Show recommendations with explanations if requested
                if show_explanations:
                    from recommendations.models import UserRecommendation
                    recommendations = UserRecommendation.objects.filter(user=user)
                    
                    for rec in recommendations:
                        self.stdout.write(
                            f'- {rec.recommended_user.username} (score: {rec.similarity_score:.2f})'
                        )
                        if rec.explanation:
                            self.stdout.write(f'  Explanation: {rec.explanation}')
                        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating recommendations for {user.username}: {str(e)}')
            ) 