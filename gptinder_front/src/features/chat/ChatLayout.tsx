import { useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store/store';
import { logout } from '../auth/authSlice';
import { fetchChats, createChat } from './chatSlice';
import { 
  fetchRecommendations, 
  generateRecommendations,
  fetchUserChats
} from '../recommendations/recommendationsSlice';
import ChatList from './components/ChatList';
import RecommendationsList from '../recommendations/components/RecommendationsList';
import UserChatList from '../recommendations/components/UserChatList';

const ChatLayout = () => {
  const [activeTab, setActiveTab] = useState<'ai' | 'people' | 'chats'>('ai');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  
  const { user } = useSelector((state: RootState) => state.auth);
  const { chats, isLoading: chatsLoading } = useSelector((state: RootState) => state.chat);
  const { 
    recommendations, 
    userChats,
    isLoading: recommendationsLoading 
  } = useSelector((state: RootState) => state.recommendations);
  
  useEffect(() => {
    // Fetch initial data
    dispatch(fetchChats());
    dispatch(fetchRecommendations());
    dispatch(fetchUserChats());
  }, [dispatch]);
  
  // Force fetch chats when tab changes to AI
  useEffect(() => {
    if (activeTab === 'ai') {
      console.log('Forcing chat refresh on tab change');
      dispatch(fetchChats());
    }
  }, [activeTab, dispatch]);
  
  const handleCreateChat = () => {
    dispatch(createChat('')).then((result) => {
      if (createChat.fulfilled.match(result)) {
        navigate(`/chat/${result.payload.id}`);
      }
    });
  };
  
  const handleGenerateRecommendations = () => {
    dispatch(generateRecommendations());
  };
  
  const handleLogout = () => {
    dispatch(logout());
  };
  
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div 
        className={`${
          sidebarOpen ? 'w-80' : 'w-0'
        } transition-all duration-300 bg-white border-r border-gray-200 flex flex-col h-full`}
      >
        {sidebarOpen && (
          <>
            <div className="p-4 border-b border-gray-200 flex justify-between items-center">
              <h1 className="text-xl font-bold text-indigo-600">GPTinder</h1>
              <div className="flex space-x-2">
                <button 
                  onClick={activeTab === 'ai' ? handleCreateChat : undefined}
                  className="p-2 rounded-full hover:bg-gray-100"
                  title={activeTab === 'ai' ? 'New Chat' : undefined}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </button>
                <button 
                  onClick={() => setSidebarOpen(false)}
                  className="p-2 rounded-full hover:bg-gray-100"
                  title="Collapse sidebar"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div className="flex border-b border-gray-200">
              <button
                className={`flex-1 py-3 text-sm font-medium ${
                  activeTab === 'ai' ? 'text-indigo-600 border-b-2 border-indigo-600' : 'text-gray-500'
                }`}
                onClick={() => setActiveTab('ai')}
              >
                AI Chat
              </button>
              <button
                className={`flex-1 py-3 text-sm font-medium ${
                  activeTab === 'people' ? 'text-indigo-600 border-b-2 border-indigo-600' : 'text-gray-500'
                }`}
                onClick={() => setActiveTab('people')}
              >
                People
              </button>
              <button
                className={`flex-1 py-3 text-sm font-medium ${
                  activeTab === 'chats' ? 'text-indigo-600 border-b-2 border-indigo-600' : 'text-gray-500'
                }`}
                onClick={() => setActiveTab('chats')}
              >
                Chats
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto">
              {activeTab === 'ai' && (
                <>
                  {/* Debug info */}
                  {import.meta.env.DEV && (
                    <div className="p-2 text-xs text-gray-400">
                      Chats Array: {Array.isArray(chats) ? 'Yes' : 'No'}, 
                      Length: {Array.isArray(chats) ? chats.length : 'N/A'}
                    </div>
                  )}
                  <ChatList 
                    chats={Array.isArray(chats) ? chats : []} 
                    isLoading={chatsLoading} 
                  />
                </>
              )}
              
              {activeTab === 'people' && (
                <RecommendationsList 
                  recommendations={Array.isArray(recommendations) ? recommendations : []}
                  isLoading={recommendationsLoading}
                  onGenerateRecommendations={handleGenerateRecommendations}
                />
              )}
              
              {activeTab === 'chats' && (
                <UserChatList 
                  userChats={Array.isArray(userChats) ? userChats : []}
                  isLoading={recommendationsLoading}
                />
              )}
            </div>
            
            <div className="p-4 border-t border-gray-200">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  {user?.profile_picture ? (
                    <img
                      className="h-10 w-10 rounded-full"
                      src={user.profile_picture}
                      alt={user.username}
                    />
                  ) : (
                    <div className="h-10 w-10 rounded-full bg-indigo-600 flex items-center justify-center text-white">
                      {user?.username.charAt(0).toUpperCase()}
                    </div>
                  )}
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-700">{user?.username}</p>
                  <div className="flex space-x-4">
                    <button
                      onClick={() => navigate('/profile/settings')}
                      className="text-xs text-indigo-600 hover:text-indigo-700"
                    >
                      Settings
                    </button>
                    <button
                      onClick={handleLogout}
                      className="text-xs text-gray-500 hover:text-gray-700"
                    >
                      Sign out
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
      
      {/* Main content */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {!sidebarOpen && (
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 m-4 rounded-full bg-white shadow hover:bg-gray-100 absolute top-0 left-0 z-10"
            title="Expand sidebar"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
            </svg>
          </button>
        )}
        
        <div className="flex-1 bg-white overflow-hidden">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default ChatLayout; 