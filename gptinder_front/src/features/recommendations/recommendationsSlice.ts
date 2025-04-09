import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { recommendationsApi, userChatApi } from '../../api/api';

// Types
interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  profile_picture: string | null;
  bio: string;
  interests: string;
  date_joined: string;
}

interface Recommendation {
  id: number;
  recommended_user: User;
  similarity_score: number;
  common_interests: string[];
  created_at: string;
  is_viewed: boolean;
}

interface UserMessage {
  id: number;
  sender: number;
  sender_username: string;
  sender_profile_picture: string | null;
  content: string;
  created_at: string;
  is_read: boolean;
}

interface UserChat {
  id: number;
  participants: User[];
  created_at: string;
  updated_at: string;
  messages: UserMessage[];
  last_message: UserMessage | null;
}

interface RecommendationsState {
  recommendations: Recommendation[];
  userChats: UserChat[];
  currentUserChat: UserChat | null;
  isLoading: boolean;
  error: string | null;
}

// Initial state
const initialState: RecommendationsState = {
  recommendations: [],
  userChats: [],
  currentUserChat: null,
  isLoading: false,
  error: null,
};

// Async thunks for recommendations
export const fetchRecommendations = createAsyncThunk(
  'recommendations/fetchRecommendations',
  async (_, { rejectWithValue }) => {
    try {
      const response = await recommendationsApi.getRecommendations();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch recommendations');
    }
  }
);

export const generateRecommendations = createAsyncThunk(
  'recommendations/generateRecommendations',
  async (_, { rejectWithValue }) => {
    try {
      const response = await recommendationsApi.generateRecommendations();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to generate recommendations');
    }
  }
);

export const markRecommendationViewed = createAsyncThunk(
  'recommendations/markViewed',
  async (id: number, { rejectWithValue }) => {
    try {
      await recommendationsApi.markViewed(id);
      return id;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to mark recommendation as viewed');
    }
  }
);

// Async thunks for user chats
export const fetchUserChats = createAsyncThunk(
  'recommendations/fetchUserChats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await userChatApi.getUserChats();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch user chats');
    }
  }
);

export const createUserChat = createAsyncThunk(
  'recommendations/createUserChat',
  async (participantId: number, { rejectWithValue }) => {
    try {
      const response = await userChatApi.createUserChat([participantId]);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create user chat');
    }
  }
);

export const sendUserMessage = createAsyncThunk(
  'recommendations/sendUserMessage',
  async ({ chatId, content }: { chatId: number; content: string }, { rejectWithValue }) => {
    try {
      const response = await userChatApi.sendUserMessage(chatId, content);
      return {
        chatId,
        message: response.data,
      };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to send message');
    }
  }
);

export const markUserChatRead = createAsyncThunk(
  'recommendations/markUserChatRead',
  async (chatId: number, { rejectWithValue }) => {
    try {
      await userChatApi.markChatRead(chatId);
      return chatId;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to mark chat as read');
    }
  }
);

// Slice
const recommendationsSlice = createSlice({
  name: 'recommendations',
  initialState,
  reducers: {
    setCurrentUserChat: (state, action: PayloadAction<UserChat | null>) => {
      state.currentUserChat = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch recommendations
      .addCase(fetchRecommendations.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchRecommendations.fulfilled, (state, action: PayloadAction<Recommendation[]>) => {
        state.isLoading = false;
        state.recommendations = action.payload;
      })
      .addCase(fetchRecommendations.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Generate recommendations
      .addCase(generateRecommendations.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(generateRecommendations.fulfilled, (state, action: PayloadAction<Recommendation[]>) => {
        state.isLoading = false;
        state.recommendations = action.payload;
      })
      .addCase(generateRecommendations.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Mark recommendation as viewed
      .addCase(markRecommendationViewed.fulfilled, (state, action: PayloadAction<number>) => {
        const index = state.recommendations.findIndex(rec => rec.id === action.payload);
        if (index !== -1) {
          state.recommendations[index].is_viewed = true;
        }
      })
      
      // Fetch user chats
      .addCase(fetchUserChats.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchUserChats.fulfilled, (state, action: PayloadAction<UserChat[]>) => {
        state.isLoading = false;
        state.userChats = action.payload;
      })
      .addCase(fetchUserChats.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Create user chat
      .addCase(createUserChat.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createUserChat.fulfilled, (state, action: PayloadAction<UserChat>) => {
        state.isLoading = false;
        if (!Array.isArray(state.userChats)) {
          state.userChats = [];
        }
        state.userChats.unshift(action.payload);
        state.currentUserChat = action.payload;
      })
      .addCase(createUserChat.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Send user message
      .addCase(sendUserMessage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(sendUserMessage.fulfilled, (state, action: PayloadAction<{ chatId: number; message: UserMessage }>) => {
        state.isLoading = false;
        
        if (state.currentUserChat && state.currentUserChat.id === action.payload.chatId) {
          // Add the message to the current chat
          state.currentUserChat.messages.push(action.payload.message);
          state.currentUserChat.last_message = action.payload.message;
        }
        
        // Ensure userChats is an array
        if (!Array.isArray(state.userChats)) {
          state.userChats = [];
        }
        
        // Update the chat in the list
        const chatIndex = state.userChats.findIndex(chat => chat.id === action.payload.chatId);
        if (chatIndex !== -1) {
          state.userChats[chatIndex].updated_at = new Date().toISOString();
          state.userChats[chatIndex].last_message = action.payload.message;
          
          // Reorder chats to show the most recent at the top
          const chat = state.userChats.splice(chatIndex, 1)[0];
          state.userChats.unshift(chat);
        }
      })
      .addCase(sendUserMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Mark chat as read
      .addCase(markUserChatRead.fulfilled, (state, action: PayloadAction<number>) => {
        const chatIndex = state.userChats.findIndex(chat => chat.id === action.payload);
        if (chatIndex !== -1 && state.userChats[chatIndex].messages) {
          state.userChats[chatIndex].messages.forEach(message => {
            message.is_read = true;
          });
        }
        
        if (state.currentUserChat && state.currentUserChat.id === action.payload) {
          state.currentUserChat.messages.forEach(message => {
            message.is_read = true;
          });
        }
      });
  },
});

export const { setCurrentUserChat, clearError } = recommendationsSlice.actions;
export default recommendationsSlice.reducer; 