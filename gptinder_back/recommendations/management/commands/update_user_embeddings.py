from django.core.management.base import BaseCommand
from django.utils import timezone
from recommendations.embeddings import EmbeddingService


class Command(BaseCommand):
    help = 'Updates embeddings for all users based on their interests and bio'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update embeddings even if they were recently updated',
        )

    def handle(self, *args, **options):
        force_update = options.get('force', False)
        embedding_service = EmbeddingService()

        updated_count = embedding_service.update_all_user_embeddings()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated embeddings for {updated_count} users')
        ) 