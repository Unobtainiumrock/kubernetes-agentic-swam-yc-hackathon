import React, { createContext, useContext, useReducer, useEffect } from 'react';

const AgentContext = createContext();

// Agent state management
const initialState = {
  agents: [],
  clusterMetrics: {
    nodes: 0,
    pods: 0,
    services: 0,
    deployments: 0
  },
  events: [],
  loading: true,
  error: null
};

const agentReducer = (state, action) => {
  switch (action.type) {
    case 'SET_AGENTS':
      return {
        ...state,
        agents: action.payload,
        loading: false
      };
    
    case 'UPDATE_AGENT':
      return {
        ...state,
        agents: state.agents.map(agent =>
          agent.id === action.payload.id
            ? { ...agent, ...action.payload }
            : agent
        )
      };
    
    case 'ADD_EVENT':
      return {
        ...state,
        events: [action.payload, ...state.events].slice(0, 100) // Keep last 100 events
      };
    
    case 'SET_CLUSTER_METRICS':
      return {
        ...state,
        clusterMetrics: action.payload
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload
      };
    
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        loading: false
      };
    
    default:
      return state;
  }
};

export const AgentProvider = ({ children, socket }) => {
  const [state, dispatch] = useReducer(agentReducer, initialState);

  useEffect(() => {
    if (!socket) return;

    // Listen for agent updates
    socket.on('agent_status', (data) => {
      dispatch({ type: 'SET_AGENTS', payload: data.agents });
    });

    socket.on('agent_update', (data) => {
      dispatch({ type: 'UPDATE_AGENT', payload: data });
    });

    // Listen for cluster events
    socket.on('cluster_event', (data) => {
      dispatch({ type: 'ADD_EVENT', payload: {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        ...data
      }});
    });

    // Listen for cluster metrics
    socket.on('cluster_metrics', (data) => {
      dispatch({ type: 'SET_CLUSTER_METRICS', payload: data });
    });

    // Error handling
    socket.on('error', (error) => {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    });

    // Initial data fetch
    socket.emit('get_initial_state');

    return () => {
      socket.off('agent_status');
      socket.off('agent_update');
      socket.off('cluster_event');
      socket.off('cluster_metrics');
      socket.off('error');
    };
  }, [socket]);

  const actions = {
    triggerChaos: (scenario) => {
      if (socket) {
        socket.emit('trigger_chaos', { scenario });
      }
    },
    
    executeAgentAction: (agentId, action, params) => {
      if (socket) {
        socket.emit('agent_action', { agentId, action, params });
      }
    },
    
    refreshClusterState: () => {
      if (socket) {
        socket.emit('refresh_cluster');
      }
    }
  };

  return (
    <AgentContext.Provider value={{ ...state, ...actions }}>
      {children}
    </AgentContext.Provider>
  );
};

export const useAgent = () => {
  const context = useContext(AgentContext);
  if (!context) {
    throw new Error('useAgent must be used within an AgentProvider');
  }
  return context;
};
