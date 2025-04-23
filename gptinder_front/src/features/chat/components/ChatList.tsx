import { useNavigate, useParams } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { useEffect } from 'react';

interface Chat {
  id: number;
  title: string;
  updated_at: string;
  messages: any[];
}

interface ChatListProps {
  chats: Chat[];
  isLoading: boolean;
}

const ChatList = ({ chats = [], isLoading }: ChatListProps) => {
  const navigate = useNavigate();
  const { chatId } = useParams();
  
  // More detailed debugging
  useEffect(() => {
    console.log("ChatList received chats:", chats);
    console.log("ChatList chats type:", typeof chats);
    console.log("ChatList is Array:", Array.isArray(chats));
    
    if (Array.isArray(chats) && chats.length > 0) {
      console.log("First chat:", chats[0]);
    }
  }, [chats]);
  
  // Handle loading state
  if (isLoading) {
    return (
      <div className="p-4 text-center text-gray-500">
        Loading chats...
      </div>
    );
  }
  
  // Make sure chats is always an array
  const safeChats = Array.isArray(chats) ? chats : [];
  
  // Filter out invalid chats
  const validChats = safeChats.filter(chat => chat && typeof chat === 'object' && chat.id);
  
  console.log("Valid chats count:", validChats.length);
  
  if (validChats.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        <p>No chats available.</p>
        <button 
          onClick={() => window.location.reload()}
          className="mt-2 text-indigo-600 hover:text-indigo-800 text-sm"
        >
          Refresh
        </button>
      </div>
    );
  }
  
  return (
    <div className="divide-y divide-gray-200">
      {validChats.map((chat) => (
        <div
          key={chat.id}
          onClick={() => navigate(`/chat/${chat.id}`)}
          className={`p-4 cursor-pointer hover:bg-gray-50 ${
            chatId === chat.id.toString() ? 'bg-gray-100' : ''
          }`}
        >
          <div className="flex justify-between items-start">
            <h3 className="text-sm font-medium text-gray-900 truncate">
              {chat.title || getChatTitle(chat)}
            </h3>
            <span className="text-xs text-gray-500">
              {formatDistanceToNow(new Date(chat.updated_at || new Date()), { addSuffix: true })}
            </span>
          </div>
          
          {chat.messages && Array.isArray(chat.messages) && chat.messages.length > 0 && (
            <p className="mt-1 text-xs text-gray-500 truncate">
              {chat.messages[chat.messages.length - 1].content.slice(0, 50)}
              {chat.messages[chat.messages.length - 1].content.length > 50 ? '...' : ''}
            </p>
          )}
        </div>
      ))}
    </div>
  );
};

// Helper function to generate a meaningful chat title
const getChatTitle = (chat: Chat): string => {
  if (chat.title) return chat.title;
  
  // Use first message content as the title if available
  if (chat.messages && Array.isArray(chat.messages) && chat.messages.length > 0) {
    const firstMessage = chat.messages[0];
    if (firstMessage.content) {
      const titleText = firstMessage.content.trim();
      // Limit to first 25 characters
      return titleText.length > 25 ? titleText.substring(0, 25) + '...' : titleText;
    }
  }
  
  // Default fallback
  return 'New Chat';
};

export default ChatList; 