import os
import pinecone
import openai
import numpy as np
from django.conf import settings
from django.utils import timezone

from users.models import User
from .models import UserRecommendation


class EmbeddingService:
    """Service for handling user embeddings"""
    
    def __init__(self):
        # Initialize Pinecone with new API
        self.pc = pinecone.Pinecone(
            api_key=settings.PINECONE_API_KEY
        )
        
        # Get or create index
        index_name = settings.PINECONE_INDEX_NAME
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=index_name,
                dimension=1536,  # OpenAI embeddings dimension
                metric='cosine'
            )
        
        # Connect to the index
        self.index = self.pc.Index(index_name)
        
        # Set up OpenAI
        openai.api_key = settings.OPENAI_API_KEY
    
    def generate_user_embedding(self, user):
        """Generate embedding for a user based on their interests and bio"""
        # Combine user interests and bio for embedding
        text_to_embed = f"Interests: {user.interests}\nBio: {user.bio}"
        
        if not text_to_embed.strip():
            return None
        
        try:
            # Generate embedding using OpenAI
            response = openai.embeddings.create(
                model="text-embedding-ada-002",  # Uses 1536 dimensions
                input=text_to_embed
            )
            embedding = response.data[0].embedding
            
            # Update user model with embedding data
            user.embedding = embedding
            user.embedding_updated_at = timezone.now()
            user.save(update_fields=['embedding', 'embedding_updated_at'])
            
            # Store in Pinecone
            self.index.upsert(
                vectors=[{
                    'id': f"user:{user.id}",
                    'values': embedding,
                    'metadata': {
                        'user_id': user.id,
                        'username': user.username,
                        'interests': user.interests,
                        'bio': user.bio
                    }
                }]
            )
            
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def find_similar_users(self, user_id, top_k=10):
        """Find users with similar interests to the given user"""
        target_user = User.objects.get(id=user_id)
        
        # Get or generate embedding for target user
        if not target_user.embedding:
            embedding = self.generate_user_embedding(target_user)
            if not embedding:
                return []
        else:
            embedding = target_user.embedding
        
        # Query Pinecone for similar users
        query_response = self.index.query(
            vector=embedding,
            top_k=top_k + 1,  # +1 because we'll filter out the user themselves
            include_metadata=True
        )
        
        # Filter out the user themselves and convert to list of user IDs
        similar_users = []
        for match in query_response['matches']:
            match_id = match['id']
            
            # Skip if this is the target user
            if match_id == f"user:{user_id}":
                continue
                
            # Extract user ID from the ID string (format: "user:123")
            if match_id.startswith('user:'):
                similar_user_id = int(match_id.split(':', 1)[1])
                similarity_score = match['score']
                metadata = match['metadata']
                
                similar_users.append({
                    'user_id': similar_user_id,
                    'similarity_score': similarity_score,
                    'metadata': metadata
                })
        
        return similar_users
    
    def explain_similarity(self, user1, user2):
        """Generate an explanation of why two users are similar using OpenAI"""
        interests1 = user1.interests
        interests2 = user2.interests
        bio1 = user1.bio
        bio2 = user2.bio
        
        prompt = f"""
        I need to explain why these two people might be a good match for a conversation.
        
        Person 1:
        Interests: {interests1}
        Bio: {bio1}
        
        Person 2:
        Interests: {interests2}
        Bio: {bio2}
        
        Please provide a brief, natural sounding explanation of why these two people might enjoy talking to each other.
        Focus on specific shared interests or complementary skills/experiences.
        Keep it short (max 30 words) and casual, addressing Person 1 directly.
        
        Example format: "Hey [Person 1 name], [Person 2 name] is also into [specific shared interest]. They're currently working on [something relevant], maybe you two could chat about it!"
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a friendly AI helping to explain why two people might enjoy talking to each other."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            explanation = response.choices[0].message.content.strip()
            return explanation
        except Exception as e:
            print(f"Error generating explanation: {e}")
            return f"{user2.first_name or user2.username} seems to share similar interests with you!"

    def update_all_user_embeddings(self):
        """Update embeddings for all users"""
        users = User.objects.all()
        updated_count = 0
        
        for user in users:
            if self.generate_user_embedding(user):
                updated_count += 1
        
        return updated_count
    
    def generate_recommendations(self, user_id):
        """Generate recommendations for a user and save them to the database"""
        # Find similar users
        similar_users = self.find_similar_users(user_id)
        target_user = User.objects.get(id=user_id)
        
        # Clear existing recommendations
        UserRecommendation.objects.filter(user_id=user_id).delete()
        
        # Create new recommendations
        for similar in similar_users:
            similar_user_id = similar['user_id']
            similarity_score = similar['similarity_score']
            
            try:
                similar_user = User.objects.get(id=similar_user_id)
                
                # Skip if users are the same (shouldn't happen, but just in case)
                if similar_user_id == user_id:
                    continue
                
                # Generate explanation
                explanation = self.explain_similarity(target_user, similar_user)
                
                # Extract common interests (basic method, can be improved)
                user_interests = set(i.strip().lower() for i in target_user.interests.split(',') if i.strip())
                similar_interests = set(i.strip().lower() for i in similar_user.interests.split(',') if i.strip())
                common_interests = list(user_interests.intersection(similar_interests))
                
                # Create recommendation
                UserRecommendation.objects.create(
                    user=target_user,
                    recommended_user=similar_user,
                    similarity_score=similarity_score,
                    common_interests=common_interests,
                    explanation=explanation
                )
            except User.DoesNotExist:
                print(f"User with ID {similar_user_id} not found")
        
        return UserRecommendation.objects.filter(user_id=user_id).count() 