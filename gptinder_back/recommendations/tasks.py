import random
import numpy as np
import openai
from celery import shared_task
from django.conf import settings
from django.db.models import Q

from users.models import User
from ai_chat.models import Message
from .models import UserRecommendation
from .embeddings import EmbeddingService


@shared_task
def analyze_messages_for_recommendations():
    """
    Periodically analyze user messages to find users that might be useful to each other.
    The task:
    1. Selects random users who have similar embeddings (profile-based)
    2. Analyzes their chat messages to find similar topics/interests
    3. If messages similarity is high, creates a recommendation
    """
    embedding_service = EmbeddingService()
    
    # Get all users with embeddings
    users = User.objects.filter(embedding__isnull=False).order_by('?')
    
    # Limit to a reasonable number to avoid overload
    max_users = min(50, users.count())
    selected_users = users[:max_users]
    
    recommendations_count = 0
    
    for user in selected_users:
        # Find users with similar embeddings
        similar_users_data = embedding_service.find_similar_users(user.id, top_k=5)
        
        if not similar_users_data:
            continue
            
        # Get user's messages with embeddings
        user_messages = Message.objects.filter(
            chat__user=user,
            role='user',
            embedding__isnull=False
        ).order_by('-created_at')[:20]  # Get recent messages
        
        if not user_messages:
            continue
            
        # Extract message embeddings
        user_msg_embeddings = [msg.embedding for msg in user_messages if msg.embedding]
        
        for similar_user_data in similar_users_data:
            similar_user_id = similar_user_data['user_id']
            profile_similarity = similar_user_data['similarity_score']
            
            # Skip if a recommendation already exists
            if UserRecommendation.objects.filter(
                user=user, 
                recommended_user_id=similar_user_id
            ).exists():
                continue
                
            # Get similar user messages with embeddings
            similar_user_messages = Message.objects.filter(
                chat__user_id=similar_user_id,
                role='user',
                embedding__isnull=False
            ).order_by('-created_at')[:20]
            
            if not similar_user_messages:
                continue
                
            # Extract message embeddings for similar user
            similar_user_msg_embeddings = [
                msg.embedding for msg in similar_user_messages if msg.embedding
            ]
            
            # Analyze message similarity
            message_similarities = []
            
            # Compare embeddings of messages from both users
            for embed1 in user_msg_embeddings:
                for embed2 in similar_user_msg_embeddings:
                    # Calculate cosine similarity
                    similarity = calculate_cosine_similarity(embed1, embed2)
                    message_similarities.append(similarity)
            
            # Check if there are any highly similar messages
            if message_similarities:
                # Get max similarity
                max_message_similarity = max(message_similarities)
                
                # Calculate overall relevance score (combine profile + message similarity)
                relevance_score = (profile_similarity + max_message_similarity) / 2
                
                # If messages are similar enough, create a recommendation
                if max_message_similarity > 0.75 or relevance_score > 0.7:
                    similar_user = User.objects.get(id=similar_user_id)
                    
                    # Find the most similar messages for explanation
                    user_msg_idx, similar_user_msg_idx = find_most_similar_messages(
                        user_msg_embeddings, similar_user_msg_embeddings
                    )
                    
                    most_similar_user_msg = user_messages[user_msg_idx].content
                    most_similar_other_msg = similar_user_messages[similar_user_msg_idx].content
                    
                    # Generate explanation based on the most similar messages
                    explanation = generate_usefulness_explanation(
                        user, similar_user, most_similar_user_msg, most_similar_other_msg
                    )
                    
                    # Extract common interests
                    user_interests = set(i.strip().lower() for i in user.interests.split(',') if i.strip())
                    similar_interests = set(i.strip().lower() for i in similar_user.interests.split(',') if i.strip())
                    common_interests = list(user_interests.intersection(similar_interests))
                    
                    # Create the recommendation
                    UserRecommendation.objects.create(
                        user=user,
                        recommended_user=similar_user,
                        similarity_score=relevance_score,
                        common_interests=common_interests,
                        explanation=explanation
                    )
                    
                    recommendations_count += 1
    
    return f"Created {recommendations_count} new recommendations based on message analysis"


def calculate_cosine_similarity(embed1, embed2):
    """Calculate cosine similarity between two embedding vectors"""
    if not embed1 or not embed2:
        return 0
        
    a = np.array(embed1)
    b = np.array(embed2)
    
    # Compute cosine similarity
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def find_most_similar_messages(user_embeddings, other_embeddings):
    """Find indices of the most similar message pair between two users"""
    max_similarity = -1
    best_pair = (0, 0)
    
    for i, embed1 in enumerate(user_embeddings):
        for j, embed2 in enumerate(other_embeddings):
            similarity = calculate_cosine_similarity(embed1, embed2)
            if similarity > max_similarity:
                max_similarity = similarity
                best_pair = (i, j)
    
    return best_pair


def generate_usefulness_explanation(user1, user2, msg1, msg2):
    """Generate an explanation of why these users might be useful to each other"""
    try:
        prompt = f"""
        I need to explain why these two people might be useful to each other based on their messages.
        
        Person 1:
        Name: {user1.first_name or user1.username}
        Interests: {user1.interests}
        Example message: {msg1[:200]}
        
        Person 2:
        Name: {user2.first_name or user2.username}
        Interests: {user2.interests}
        Example message: {msg2[:200]}
        
        Please provide a brief, natural sounding explanation of why these two people might be useful to each other.
        Focus on their specific shared interests and the content of their messages.
        Keep it short (max 40 words) and casual, addressing Person 1 directly.
        
        Example format: "Hey [Person 1 name], [Person 2 name] seems to be discussing similar topics around [specific topic from messages]. You might find their perspective on [something from messages] helpful!"
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a friendly AI helping to explain why two people might be useful to each other."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        explanation = response.choices[0].message.content.strip()
        return explanation
    except Exception as e:
        print(f"Error generating explanation: {e}")
        return f"{user2.first_name or user2.username} has been discussing topics that might be relevant to your interests!" 