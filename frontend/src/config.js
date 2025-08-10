// API Configuration
// This file handles different API URLs for development vs production

export const API_CONFIG = {
  // In development, use local backend
  // In production, use same domain (Netlify Functions)
  baseURL: import.meta.env.PROD 
    ? ''  // Same domain - Netlify will route /api/* to functions
    : 'http://localhost:3000',  // Use Vite dev server for proxying
  
  // WebSocket URL - Use Vite proxy in development
  wsURL: import.meta.env.PROD
    ? 'wss://your-netlify-app.netlify.app'   // You'll need WebSocket service for production
    : 'ws://localhost:3000',  // Use Vite dev server proxy
    
  // API endpoints
  endpoints: {
    agents: '/api/agents',
    cluster: '/api/cluster', 
    chaos: '/api/chaos',
    adk: '/api/adk'
  }
}

// Helper function to get full API URL
export const getApiUrl = (endpoint) => {
  return `${API_CONFIG.baseURL}${endpoint}`
}

// Helper function to get WebSocket URL  
export const getWsUrl = (path) => {
  return `${API_CONFIG.wsURL}${path}`
} 