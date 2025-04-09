import { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from './store/store';
import { getCurrentUser } from './features/auth/authSlice';

// Import pages
import Login from './features/auth/Login';
import Register from './features/auth/Register';
import ProfileSettings from './features/auth/ProfileSettings';
import ChatLayout from './features/chat/ChatLayout';
import ChatWindow from './features/chat/ChatWindow';

// Protected route component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useSelector((state: RootState) => state.auth);
  
  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

function App() {
  const dispatch = useDispatch<AppDispatch>();
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  
  useEffect(() => {
    if (localStorage.getItem('token')) {
      dispatch(getCurrentUser());
    }
  }, [dispatch]);
  
  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to="/" /> : <Login />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to="/" /> : <Register />} />
      <Route path="/profile/settings" element={
        <ProtectedRoute>
          <ProfileSettings />
        </ProtectedRoute>
      } />
      
      <Route path="/" element={
        <ProtectedRoute>
          <ChatLayout />
        </ProtectedRoute>
      }>
        <Route index element={<div className="flex items-center justify-center h-full text-gray-500">Select a chat or start a new one</div>} />
        <Route path="chat/:chatId" element={<ChatWindow />} />
        <Route path="user-chat/:chatId" element={<ChatWindow isUserChat />} />
      </Route>
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
