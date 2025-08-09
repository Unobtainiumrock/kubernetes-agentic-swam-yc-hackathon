import React, { createContext, useContext, useReducer, useEffect } from 'react';

const ChatContext = createContext();

// Chat state management
const initialState = {
  messages: [
    {
      id: 1,
      type: 'assistant',
      content: 'Hello! I\'m your Kubernetes infrastructure assistant. I can help you understand your cluster, diagnose issues, and perform operations. What would you like to know?',
      timestamp: new Date().toISOString()
    }
  ],
  isTyping: false,
  connected: false,
  error: null
};

const chatReducer = (state, action) => {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, {
          id: Date.now(),
          timestamp: new Date().toISOString(),
          ...action.payload
        }]
      };
    
    case 'SET_TYPING':
      return {
        ...state,
        isTyping: action.payload
      };
    
    case 'SET_CONNECTED':
      return {
        ...state,
        connected: action.payload
      };
    
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload
      };
    
    case 'CLEAR_MESSAGES':
      return {
        ...state,
        messages: [state.messages[0]] // Keep welcome message
      };
    
    default:
      return state;
  }
};

export const ChatProvider = ({ children, socket }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  useEffect(() => {
    if (!socket) return;

    // Listen for chat responses
    socket.on('chat_response', (data) => {
      dispatch({ type: 'SET_TYPING', payload: false });
      dispatch({ 
        type: 'ADD_MESSAGE', 
        payload: {
          type: 'assistant',
          content: data.message,
          metadata: data.metadata || {}
        }
      });
    });

    // Listen for typing indicators
    socket.on('chat_typing', (data) => {
      dispatch({ type: 'SET_TYPING', payload: data.typing });
    });

    // Connection status
    socket.on('connect', () => {
      dispatch({ type: 'SET_CONNECTED', payload: true });
    });

    socket.on('disconnect', () => {
      dispatch({ type: 'SET_CONNECTED', payload: false });
    });

    // Error handling
    socket.on('chat_error', (error) => {
      dispatch({ type: 'SET_TYPING', payload: false });
      dispatch({ type: 'SET_ERROR', payload: error.message });
      dispatch({ 
        type: 'ADD_MESSAGE', 
        payload: {
          type: 'error',
          content: `Error: ${error.message}`
        }
      });
    });

    return () => {
      socket.off('chat_response');
      socket.off('chat_typing');
      socket.off('chat_error');
    };
  }, [socket]);

  const actions = {
    sendMessage: (message) => {
      // Add user message to chat
      dispatch({ 
        type: 'ADD_MESSAGE', 
        payload: {
          type: 'user',
          content: message
        }
      });

      // Send to backend
      if (socket) {
        dispatch({ type: 'SET_TYPING', payload: true });
        socket.emit('chat_message', { message });
      }
    },

    clearChat: () => {
      dispatch({ type: 'CLEAR_MESSAGES' });
    },

    // Quick actions for common queries
    quickQuery: (query) => {
      const quickQueries = {
        'cluster_status': 'What is the current status of my Kubernetes cluster?',
        'pod_issues': 'Are there any pod issues I should be aware of?',
        'resource_usage': 'Show me the current resource usage across my cluster',
        'recent_events': 'What are the most recent events in my cluster?',
        'agent_status': 'How are my AI agents performing?'
      };

      const message = quickQueries[query] || query;
      actions.sendMessage(message);
    }
  };

  return (
    <ChatContext.Provider value={{ ...state, ...actions }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
