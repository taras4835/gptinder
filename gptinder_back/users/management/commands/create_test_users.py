import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
import os

User = get_user_model()

INTERESTS_CATEGORIES = {
    'technology': [
        'programming', 'artificial intelligence', 'machine learning', 'web development', 
        'cybersecurity', 'data science', 'blockchain', 'virtual reality', 'gaming',
    ],
    'science': [
        'astronomy', 'physics', 'chemistry', 'biology', 'neuroscience', 
        'mathematics', 'geology', 'quantum mechanics', 'evolutionary biology',
    ],
    'arts': [
        'painting', 'sculpture', 'photography', 'literature', 'poetry', 
        'film', 'theatre', 'music', 'dance', 'architecture',
    ],
    'sports': [
        'football', 'basketball', 'tennis', 'swimming', 'running', 
        'cycling', 'yoga', 'hiking', 'martial arts', 'climbing',
    ],
    'lifestyle': [
        'cooking', 'travel', 'fashion', 'fitness', 'meditation', 
        'reading', 'gardening', 'interior design', 'sustainability', 'minimalism',
    ],
}

TEST_USERS = [
    {
        'username': 'tech_lover',
        'email': 'tech@example.com',
        'password': 'password123',
        'first_name': 'Alex',
        'last_name': 'Smith',
        'bio': 'Software developer passionate about new technologies and coding challenges.',
        'interests_categories': ['technology', 'science'],
    },
    {
        'username': 'art_enthusiast',
        'email': 'artist@example.com',
        'password': 'password123',
        'first_name': 'Emma',
        'last_name': 'Johnson',
        'bio': 'Artist exploring various mediums and always looking for inspiration.',
        'interests_categories': ['arts', 'lifestyle'],
    },
    {
        'username': 'science_geek',
        'email': 'science@example.com',
        'password': 'password123',
        'first_name': 'Michael',
        'last_name': 'Brown',
        'bio': 'PhD student in physics with a passion for explaining complex concepts.',
        'interests_categories': ['science', 'technology'],
    },
    {
        'username': 'fitness_guru',
        'email': 'fitness@example.com',
        'password': 'password123',
        'first_name': 'Sarah',
        'last_name': 'Davis',
        'bio': 'Personal trainer helping people achieve their fitness goals.',
        'interests_categories': ['sports', 'lifestyle'],
    },
    {
        'username': 'travel_addict',
        'email': 'traveler@example.com',
        'password': 'password123',
        'first_name': 'James',
        'last_name': 'Wilson',
        'bio': 'Digital nomad exploring the world one country at a time.',
        'interests_categories': ['lifestyle', 'arts'],
    },
    {
        'username': 'bookworm',
        'email': 'reader@example.com',
        'password': 'password123',
        'first_name': 'Olivia',
        'last_name': 'Taylor',
        'bio': 'Avid reader with a personal library that\'s always growing.',
        'interests_categories': ['arts', 'science'],
    },
    {
        'username': 'chef_master',
        'email': 'chef@example.com',
        'password': 'password123',
        'first_name': 'David',
        'last_name': 'Anderson',
        'bio': 'Home chef experimenting with cuisines from around the world.',
        'interests_categories': ['lifestyle', 'sports'],
    },
    {
        'username': 'gaming_pro',
        'email': 'gamer@example.com',
        'password': 'password123',
        'first_name': 'Daniel',
        'last_name': 'Thomas',
        'bio': 'Professional gamer and livestreamer with a competitive spirit.',
        'interests_categories': ['technology', 'sports'],
    },
    {
        'username': 'nature_lover',
        'email': 'nature@example.com',
        'password': 'password123',
        'first_name': 'Sophia',
        'last_name': 'Martin',
        'bio': 'Environmental scientist working on conservation projects.',
        'interests_categories': ['science', 'sports'],
    },
    {
        'username': 'music_fan',
        'email': 'music@example.com',
        'password': 'password123',
        'first_name': 'Emily',
        'last_name': 'Clark',
        'bio': 'Music producer and DJ with a passion for discovering new sounds.',
        'interests_categories': ['arts', 'technology'],
    },
]

class Command(BaseCommand):
    help = 'Creates test users with different interests for testing the recommendation system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing users except superusers before creating new ones',
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            if options['clear']:
                # Delete all existing users except superusers
                User.objects.filter(is_superuser=False).delete()
                self.stdout.write(self.style.SUCCESS('Deleted all non-superuser accounts'))
            
            created_count = 0
            skipped_count = 0
            
            for user_data in TEST_USERS:
                if User.objects.filter(username=user_data['username']).exists():
                    self.stdout.write(self.style.WARNING(f"User {user_data['username']} already exists, skipping"))
                    skipped_count += 1
                    continue
                
                # Generate interests from the categories
                interests = []
                for category in user_data['interests_categories']:
                    # Add 3-5 random interests from each category
                    num_interests = random.randint(3, 5)
                    category_interests = random.sample(INTERESTS_CATEGORIES[category], min(num_interests, len(INTERESTS_CATEGORIES[category])))
                    interests.extend(category_interests)
                
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    bio=user_data['bio'],
                    interests=', '.join(interests),
                )
                
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created user: {user.username} with interests: {user.interests}"))
            
            self.stdout.write(self.style.SUCCESS(f"Created {created_count} test users, skipped {skipped_count} existing users")) 