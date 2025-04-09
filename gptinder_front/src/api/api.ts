import axios from 'axios';

// URL для API из переменной окружения
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the token in all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth services
export const authApi = {
  login: (username: string, password: string) => 
    api.post('/login/', { username, password }),
  
  logout: () => api.post('/logout/'),
  
  register: (userData: any) => api.post('/users/', userData),
  
  getCurrentUser: () => api.get('/users/me/'),
  
  updateProfile: (userData: FormData) => {
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    };
    return api.patch('/users/me/', userData, config);
  },
  
  updatePassword: (current_password: string, new_password: string) => 
    api.post('/change-password/', { current_password, new_password }),
};

// AI Chat services
export const chatApi = {
  getChats: () => api.get('/chats/'),
  
  createChat: (title: string = '') => api.post('/chats/', { title }),
  
  getChatMessages: (chatId: number) => api.get(`/chats/${chatId}/`),
  
  sendMessage: (chatId: number, content: string) => 
    api.post(`/chats/${chatId}/message/`, { content }),
};

// Recommendations services
export const recommendationsApi = {
  getRecommendations: () => api.get('/recommendations/'),
  
  generateRecommendations: () => api.post('/recommendations/generate/'),
  
  markViewed: (recommendationId: number) => 
    api.post(`/recommendations/${recommendationId}/mark_viewed/`),
};

// User Chat services
export const userChatApi = {
  getUserChats: () => api.get('/user-chats/'),
  
  createUserChat: (participants: number[]) => 
    api.post('/user-chats/', { participants }),
  
  sendUserMessage: (chatId: number, content: string) => 
    api.post(`/user-chats/${chatId}/message/`, { content }),
  
  markChatRead: (chatId: number) => 
    api.post(`/user-chats/${chatId}/mark_read/`),
};

export default api; 