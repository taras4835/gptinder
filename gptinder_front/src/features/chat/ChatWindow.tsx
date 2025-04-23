import { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store/store';
import { fetchChat, sendMessage } from './chatSlice';
import { 
  sendUserMessage, 
  markUserChatRead
} from '../recommendations/recommendationsSlice';

interface ChatWindowProps {
  isUserChat?: boolean;
}

const ChatWindow = ({ isUserChat = false }: ChatWindowProps) => {
  const { chatId } = useParams();
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const dispatch = useDispatch<AppDispatch>();
  
  const { user } = useSelector((state: RootState) => state.auth);
  const { currentChat, isLoading: aiChatLoading } = useSelector((state: RootState) => state.chat);
  const { currentUserChat, isLoading: userChatLoading } = useSelector(
    (state: RootState) => state.recommendations
  );
  
  // Determine which chat data to use based on isUserChat prop
  const currentChatData = isUserChat ? currentUserChat : currentChat;
  const isLoading = isUserChat ? userChatLoading : aiChatLoading;
  
  // Find other participant in user chat
  const otherParticipant = isUserChat && currentUserChat
    ? currentUserChat.participants.find(p => p.id !== user?.id)
    : null;
  
  useEffect(() => {
    if (chatId) {
      if (isUserChat) {
        // Mark chat as read when opening
        dispatch(markUserChatRead(parseInt(chatId)));
      } else {
        dispatch(fetchChat(parseInt(chatId)));
      }
    }
  }, [chatId, dispatch, isUserChat]);
  
  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentChatData?.messages]);
  
  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!message.trim() || !chatId) return;
    
    // Create a temporary user message to display immediately
    const tempUserMessage = {
      id: Date.now(), // temporary ID
      role: 'user',
      content: message,
      created_at: new Date().toISOString()
    };
    
    if (isUserChat) {
      dispatch(sendUserMessage({
        chatId: parseInt(chatId),
        content: message
      }));
    } else {
      // Optionally add the message to the UI before the API response
      if (currentChat && currentChat.messages) {
        // This is just visual feedback, the actual update will happen in reducer
        const updatedMessages = [...currentChat.messages, tempUserMessage];
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }
      
      dispatch(sendMessage({
        chatId: parseInt(chatId),
        content: message
      }));
    }
    
    setMessage('');
  };
  
  if (!chatId) {
    return null;
  }
  
  if (!currentChatData && !isLoading) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        Chat not found
      </div>
    );
  }
  
  return (
    <div className="flex flex-col h-full">
      {/* Chat header */}
      <div className="px-4 py-3 border-b border-gray-200 flex items-center">
        {isUserChat && otherParticipant ? (
          <>
            <div className="flex-shrink-0 mr-3">
              {otherParticipant.profile_picture ? (
                <img
                  src={otherParticipant.profile_picture}
                  alt={otherParticipant.username}
                  className="h-8 w-8 rounded-full"
                />
              ) : (
                <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center text-white">
                  {otherParticipant.username.charAt(0).toUpperCase()}
                </div>
              )}
            </div>
            <h2 className="text-lg font-medium text-gray-900">{otherParticipant.username}</h2>
          </>
        ) : (
          <h2 className="text-lg font-medium text-gray-900">
            {currentChat?.title || 'AI Chat'}
          </h2>
        )}
      </div>
      
      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {isLoading && !currentChatData ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500">Loading messages...</p>
          </div>
        ) : (
          <>
            {/* System welcome message (for AI chats) */}
            {!isUserChat && currentChat?.messages.length === 0 && (
              <div className="flex items-start">
                <div className="flex-shrink-0 mr-3">
                  <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center text-white">
                    AI
                  </div>
                </div>
                <div className="message-bubble ai-message">
                  <p>Hello! I'm your AI assistant. How can I help you today?</p>
                </div>
              </div>
            )}
            
            {/* Chat messages */}
            {currentChatData?.messages.map((msg: any) => {
              const isUserMessage = isUserChat
                ? msg.sender === user?.id
                : msg.role === 'user';
              
              return (
                <div 
                  key={msg.id} 
                  className={`flex items-start ${isUserMessage ? 'justify-end' : ''}`}
                >
                  {!isUserMessage && (
                    <div className="flex-shrink-0 mr-3">
                      {isUserChat && (
                        <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center text-white">
                          {otherParticipant?.username.charAt(0).toUpperCase() || '?'}
                        </div>
                      )}
                      {!isUserChat && (
                        <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center text-white">
                          AI
                        </div>
                      )}
                    </div>
                  )}
                  
                  <div className={`message-bubble ${isUserMessage ? 'user-message' : 'ai-message'}`}>
                    <p>{msg.content}</p>
                  </div>
                  
                  {isUserMessage && (
                    <div className="flex-shrink-0 ml-3">
                      {user?.profile_picture ? (
                        <img
                          src={user.profile_picture}
                          alt={user.username}
                          className="h-8 w-8 rounded-full"
                        />
                      ) : (
                        <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center text-white">
                          {user?.username.charAt(0).toUpperCase()}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
            
            {/* AI is typing indicator */}
            {isLoading && !isUserChat && (
              <div className="flex items-start">
                <div className="flex-shrink-0 mr-3">
                  <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center text-white">
                    AI
                  </div>
                </div>
                <div className="message-bubble ai-message">
                  <p>Typing...</p>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </>
        )}
      </div>
      
      {/* Message input */}
      <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder={`Message ${isUserChat ? otherParticipant?.username || 'user' : 'AI'}...`}
            className="input-field"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !message.trim()}
            className="btn-primary"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatWindow; 