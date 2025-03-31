import { useNavigate, useParams } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { formatDistanceToNow } from 'date-fns';
import { RootState } from '../../../store/store';

interface User {
  id: number;
  username: string;
  profile_picture: string | null;
}

interface UserMessage {
  id: number;
  sender: number;
  sender_username: string;
  content: string;
  created_at: string;
  is_read: boolean;
}

interface UserChat {
  id: number;
  participants: User[];
  messages: UserMessage[];
  last_message: UserMessage | null;
  updated_at: string;
}

interface UserChatListProps {
  userChats: UserChat[];
  isLoading: boolean;
}

const UserChatList = ({ userChats, isLoading }: UserChatListProps) => {
  const navigate = useNavigate();
  const { chatId } = useParams();
  const { user } = useSelector((state: RootState) => state.auth);
  
  if (isLoading && userChats.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        Loading chats...
      </div>
    );
  }
  
  if (userChats.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        No chats yet. Start a conversation with someone from the recommendations!
      </div>
    );
  }
  
  return (
    <div className="divide-y divide-gray-200">
      {userChats.map((chat) => {
        // Find other participant (not current user)
        const otherParticipant = chat.participants.find(p => p.id !== user?.id) || chat.participants[0];
        
        // Check if there are unread messages
        const hasUnreadMessages = chat.messages.some(msg => !msg.is_read && msg.sender !== user?.id);
        
        return (
          <div
            key={chat.id}
            onClick={() => navigate(`/user-chat/${chat.id}`)}
            className={`p-4 cursor-pointer hover:bg-gray-50 ${
              chatId === chat.id.toString() ? 'bg-gray-100' : ''
            }`}
          >
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                {otherParticipant.profile_picture ? (
                  <img
                    src={otherParticipant.profile_picture}
                    alt={otherParticipant.username}
                    className="h-10 w-10 rounded-full"
                  />
                ) : (
                  <div className="h-10 w-10 rounded-full bg-indigo-600 flex items-center justify-center text-white">
                    {otherParticipant.username.charAt(0).toUpperCase()}
                  </div>
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-center">
                  <h3 className={`text-sm font-medium ${hasUnreadMessages ? 'text-indigo-600 font-bold' : 'text-gray-900'}`}>
                    {otherParticipant.username}
                  </h3>
                  {chat.last_message && (
                    <span className="text-xs text-gray-500">
                      {formatDistanceToNow(new Date(chat.updated_at), { addSuffix: true })}
                    </span>
                  )}
                </div>
                
                {chat.last_message && (
                  <p className={`mt-1 text-xs truncate ${
                    hasUnreadMessages ? 'text-gray-900 font-medium' : 'text-gray-500'
                  }`}>
                    {chat.last_message.sender === user?.id ? 'You: ' : ''}
                    {chat.last_message.content}
                  </p>
                )}
              </div>
              
              {hasUnreadMessages && (
                <div className="w-2 h-2 bg-indigo-600 rounded-full"></div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default UserChatList; 