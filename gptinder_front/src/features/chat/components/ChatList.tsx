import { useNavigate, useParams } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';

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

const ChatList = ({ chats, isLoading }: ChatListProps) => {
  const navigate = useNavigate();
  const { chatId } = useParams();
  
  if (isLoading && chats.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        Loading chats...
      </div>
    );
  }
  
  if (chats.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        No chats yet. Start a new conversation!
      </div>
    );
  }
  
  return (
    <div className="divide-y divide-gray-200">
      {chats.map((chat) => (
        <div
          key={chat.id}
          onClick={() => navigate(`/chat/${chat.id}`)}
          className={`p-4 cursor-pointer hover:bg-gray-50 ${
            chatId === chat.id.toString() ? 'bg-gray-100' : ''
          }`}
        >
          <div className="flex justify-between items-start">
            <h3 className="text-sm font-medium text-gray-900 truncate">
              {chat.title || 'New Chat'}
            </h3>
            <span className="text-xs text-gray-500">
              {formatDistanceToNow(new Date(chat.updated_at), { addSuffix: true })}
            </span>
          </div>
          
          {chat.messages && chat.messages.length > 0 && (
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

export default ChatList; 