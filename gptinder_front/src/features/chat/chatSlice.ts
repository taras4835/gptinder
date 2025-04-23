import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { chatApi } from '../../api/api';

// Types
interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

interface Chat {
  id: number;
  title: string;
  user: number;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

interface ChatState {
  chats: Chat[];
  currentChat: Chat | null;
  isLoading: boolean;
  error: string | null;
}

// Initial state
const initialState: ChatState = {
  chats: [],
  currentChat: null,
  isLoading: false,
  error: null,
};

// Async thunks
export const fetchChats = createAsyncThunk(
  'chat/fetchChats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await chatApi.getChats();
      console.log('API response data:', response.data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch chats');
    }
  }
);

export const fetchChat = createAsyncThunk(
  'chat/fetchChat',
  async (chatId: number, { rejectWithValue }) => {
    try {
      const response = await chatApi.getChatMessages(chatId);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch chat');
    }
  }
);

export const createChat = createAsyncThunk(
  'chat/createChat',
  async (title: string = '', { rejectWithValue }) => {
    try {
      const response = await chatApi.createChat(title);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create chat');
    }
  }
);

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ chatId, content }: { chatId: number; content: string }, { rejectWithValue }) => {
    try {
      const response = await chatApi.sendMessage(chatId, content);
      return {
        chatId,
        message: response.data.message,
      };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to send message');
    }
  }
);

// Slice
const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setCurrentChat: (state, action: PayloadAction<Chat | null>) => {
      state.currentChat = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch chats
      .addCase(fetchChats.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchChats.fulfilled, (state, action) => {
        state.isLoading = false;
        
        console.log('Raw fetchChats response:', action.payload);
        
        // Handle paginated response from Django REST framework
        if (action.payload && typeof action.payload === 'object') {
          if (Array.isArray(action.payload)) {
            // Direct array response
            state.chats = action.payload;
          } else if (action.payload.results && Array.isArray(action.payload.results)) {
            // Paginated response with results field
            state.chats = action.payload.results;
          } else {
            // Fallback to empty array
            state.chats = [];
          }
        } else {
          state.chats = [];
        }
        
        console.log('Processed chats:', state.chats);
      })
      .addCase(fetchChats.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Fetch single chat
      .addCase(fetchChat.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchChat.fulfilled, (state, action: PayloadAction<Chat>) => {
        state.isLoading = false;
        state.currentChat = action.payload;
        
        // Ensure chats is an array
        if (!Array.isArray(state.chats)) {
          state.chats = [];
        }
        
        // Update the chat in the list
        const index = state.chats.findIndex(chat => chat.id === action.payload.id);
        if (index !== -1) {
          state.chats[index] = action.payload;
        }
      })
      .addCase(fetchChat.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Create chat
      .addCase(createChat.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createChat.fulfilled, (state, action: PayloadAction<Chat>) => {
        state.isLoading = false;
        if (!Array.isArray(state.chats)) {
          state.chats = [];
        }
        state.chats.unshift(action.payload);
        state.currentChat = action.payload;
      })
      .addCase(createChat.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Send message
      .addCase(sendMessage.pending, (state, action) => {
        state.isLoading = true;
        state.error = null;
        
        // Add user message immediately to UI for better UX
        // We extract the payload from the action's meta
        const { chatId, content } = action.meta.arg;
        
        if (state.currentChat && state.currentChat.id === chatId) {
          // Create a temporary message with a negative ID (will be replaced later)
          const tempMessage: Message = {
            id: -Date.now(), // Temporary negative ID to distinguish it
            role: 'user',
            content: content,
            created_at: new Date().toISOString()
          };
          
          // Add to current chat
          state.currentChat.messages.push(tempMessage);
          
          // Ensure chats is an array
          if (!Array.isArray(state.chats)) {
            state.chats = [];
          }
          
          // Also update in the chats list if present
          const chatIndex = state.chats.findIndex(chat => chat.id === chatId);
          if (chatIndex !== -1) {
            if (!state.chats[chatIndex].messages) {
              state.chats[chatIndex].messages = [];
            }
            state.chats[chatIndex].messages.push(tempMessage);
            state.chats[chatIndex].updated_at = new Date().toISOString();
          }
        }
      })
      .addCase(sendMessage.fulfilled, (state, action: PayloadAction<{ chatId: number; message: Message }>) => {
        state.isLoading = false;
        
        if (state.currentChat && state.currentChat.id === action.payload.chatId) {
          // Add the message to the current chat
          state.currentChat.messages.push(action.payload.message);
        }
        
        // Ensure chats is an array
        if (!Array.isArray(state.chats)) {
          state.chats = [];
        }
        
        // Update the chat in the list
        const chatIndex = state.chats.findIndex(chat => chat.id === action.payload.chatId);
        if (chatIndex !== -1) {
          // Ensure we update the message list in the chat list too
          if (!state.chats[chatIndex].messages) {
            state.chats[chatIndex].messages = [];
          }
          state.chats[chatIndex].messages.push(action.payload.message);
          state.chats[chatIndex].updated_at = new Date().toISOString();
          
          // Move chat to top of list (most recent first)
          const chat = state.chats.splice(chatIndex, 1)[0];
          state.chats.unshift(chat);
        }
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { setCurrentChat, clearError } = chatSlice.actions;
export default chatSlice.reducer; 