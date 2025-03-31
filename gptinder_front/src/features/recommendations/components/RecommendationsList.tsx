import { useDispatch } from 'react-redux';
import { AppDispatch } from '../../../store/store';
import { createUserChat } from '../recommendationsSlice';
import { useNavigate } from 'react-router-dom';

interface User {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  profile_picture: string | null;
  bio: string;
}

interface Recommendation {
  id: number;
  recommended_user: User;
  similarity_score: number;
  common_interests: string[];
  is_viewed: boolean;
}

interface RecommendationsListProps {
  recommendations: Recommendation[];
  isLoading: boolean;
  onGenerateRecommendations: () => void;
}

const RecommendationsList = ({ 
  recommendations, 
  isLoading,
  onGenerateRecommendations
}: RecommendationsListProps) => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  
  const handleStartChat = (userId: number) => {
    dispatch(createUserChat(userId)).then((result) => {
      if (createUserChat.fulfilled.match(result)) {
        navigate(`/user-chat/${result.payload.id}`);
      }
    });
  };
  
  if (isLoading && recommendations.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        Loading recommendations...
      </div>
    );
  }
  
  if (recommendations.length === 0) {
    return (
      <div className="p-4 text-center">
        <p className="text-gray-500 mb-4">
          No recommendations yet. Generate recommendations based on your chat history.
        </p>
        <button
          onClick={onGenerateRecommendations}
          className="btn-primary"
          disabled={isLoading}
        >
          {isLoading ? 'Generating...' : 'Generate Recommendations'}
        </button>
      </div>
    );
  }
  
  return (
    <div>
      <div className="p-3 bg-gray-50 border-b border-gray-200">
        <button
          onClick={onGenerateRecommendations}
          className="btn-secondary w-full"
          disabled={isLoading}
        >
          {isLoading ? 'Updating...' : 'Update Recommendations'}
        </button>
      </div>
      
      <div className="divide-y divide-gray-200">
        {recommendations.map((recommendation) => (
          <div
            key={recommendation.id}
            className="p-4 hover:bg-gray-50"
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                {recommendation.recommended_user.profile_picture ? (
                  <img
                    src={recommendation.recommended_user.profile_picture}
                    alt={recommendation.recommended_user.username}
                    className="h-10 w-10 rounded-full"
                  />
                ) : (
                  <div className="h-10 w-10 rounded-full bg-indigo-600 flex items-center justify-center text-white">
                    {recommendation.recommended_user.username.charAt(0).toUpperCase()}
                  </div>
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium text-gray-900">
                    {recommendation.recommended_user.first_name 
                      ? `${recommendation.recommended_user.first_name} ${recommendation.recommended_user.last_name}`
                      : recommendation.recommended_user.username}
                  </h3>
                  <span className="text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-1 rounded-full">
                    {Math.round(recommendation.similarity_score * 100)}% match
                  </span>
                </div>
                
                {recommendation.common_interests && recommendation.common_interests.length > 0 && (
                  <div className="mt-1">
                    <p className="text-xs text-gray-500 mb-1">Common interests:</p>
                    <div className="flex flex-wrap gap-1">
                      {recommendation.common_interests.slice(0, 3).map((interest, index) => (
                        <span key={index} className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded-full">
                          {interest}
                        </span>
                      ))}
                      {recommendation.common_interests.length > 3 && (
                        <span className="text-xs text-gray-500">
                          +{recommendation.common_interests.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
                
                {recommendation.recommended_user.bio && (
                  <p className="mt-1 text-xs text-gray-500 line-clamp-2">
                    {recommendation.recommended_user.bio}
                  </p>
                )}
                
                <div className="mt-2">
                  <button
                    onClick={() => handleStartChat(recommendation.recommended_user.id)}
                    className="text-xs font-medium text-indigo-600 hover:text-indigo-500"
                  >
                    Start Chat
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecommendationsList; 