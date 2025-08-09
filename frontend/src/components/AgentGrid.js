import React from 'react';
import { useAgent } from '../contexts/AgentContext';
import { Bot, Activity, CheckCircle, AlertCircle, Clock, Zap } from 'lucide-react';

const AgentCard = ({ agent }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <Activity className="w-4 h-4 text-success-600 animate-pulse" />;
      case 'idle':
        return <CheckCircle className="w-4 h-4 text-gray-400" />;
      case 'working':
        return <Zap className="w-4 h-4 text-warning-600 animate-bounce" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-danger-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'border-success-200 bg-success-50';
      case 'working':
        return 'border-warning-200 bg-warning-50 agent-active';
      case 'error':
        return 'border-danger-200 bg-danger-50';
      default:
        return 'border-gray-200 bg-white';
    }
  };

  return (
    <div className={`card ${getStatusColor(agent.status)} transition-all duration-300`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex items-center justify-center w-10 h-10 bg-primary-100 rounded-lg">
            <Bot className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{agent.name}</h3>
            <p className="text-sm text-gray-500">{agent.type}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {getStatusIcon(agent.status)}
          <span className={`status-${agent.status}`}>
            {agent.status}
          </span>
        </div>
      </div>

      {/* Current Task */}
      {agent.currentTask && (
        <div className="mt-4 p-3 bg-gray-50 rounded-md">
          <p className="text-sm font-medium text-gray-700">Current Task:</p>
          <p className="text-sm text-gray-600 mt-1">{agent.currentTask}</p>
        </div>
      )}

      {/* Recent Actions */}
      {agent.recentActions && agent.recentActions.length > 0 && (
        <div className="mt-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Recent Actions:</p>
          <div className="space-y-1">
            {agent.recentActions.slice(0, 2).map((action, index) => (
              <div key={index} className="text-xs text-gray-600 bg-gray-50 px-2 py-1 rounded">
                {action.timestamp}: {action.description}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Metrics */}
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500">Tasks Completed:</span>
          <span className="ml-2 font-semibold text-gray-900">
            {agent.metrics?.tasksCompleted || 0}
          </span>
        </div>
        <div>
          <span className="text-gray-500">Success Rate:</span>
          <span className="ml-2 font-semibold text-gray-900">
            {agent.metrics?.successRate || '100'}%
          </span>
        </div>
      </div>
    </div>
  );
};

const AgentGrid = () => {
  const { agents, loading, error } = useAgent();

  if (loading) {
    return (
      <div className="card h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-2 text-gray-500">Loading agents...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card h-full flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-8 h-8 text-danger-600 mx-auto" />
          <p className="mt-2 text-danger-600">Error loading agents: {error}</p>
        </div>
      </div>
    );
  }

  // Mock agents if none are provided
  const mockAgents = [
    {
      id: 'agent-1',
      name: 'Diagnostic Agent',
      type: 'Monitor & Analyze',
      status: 'active',
      currentTask: 'Monitoring pod health across all namespaces',
      recentActions: [
        { timestamp: '14:32', description: 'Analyzed frontend pod restart' },
        { timestamp: '14:30', description: 'Generated cluster health report' }
      ],
      metrics: { tasksCompleted: 47, successRate: 98 }
    },
    {
      id: 'agent-2',
      name: 'Healing Agent',
      type: 'Auto-Remediation',
      status: 'working',
      currentTask: 'Scaling backend deployment due to high CPU usage',
      recentActions: [
        { timestamp: '14:33', description: 'Scaled backend-app from 4 to 6 replicas' },
        { timestamp: '14:31', description: 'Detected resource pressure' }
      ],
      metrics: { tasksCompleted: 23, successRate: 95 }
    },
    {
      id: 'agent-3',
      name: 'Security Agent',
      type: 'Security & Compliance',
      status: 'idle',
      currentTask: null,
      recentActions: [
        { timestamp: '14:25', description: 'Validated RBAC policies' },
        { timestamp: '14:20', description: 'Scanned for security vulnerabilities' }
      ],
      metrics: { tasksCompleted: 12, successRate: 100 }
    },
    {
      id: 'agent-4',
      name: 'Resource Agent',
      type: 'Resource Optimization',
      status: 'active',
      currentTask: 'Optimizing resource allocation for database pods',
      recentActions: [
        { timestamp: '14:34', description: 'Adjusted memory limits for Redis pods' },
        { timestamp: '14:28', description: 'Analyzed resource utilization patterns' }
      ],
      metrics: { tasksCompleted: 31, successRate: 97 }
    }
  ];

  const displayAgents = agents.length > 0 ? agents : mockAgents;

  return (
    <div className="h-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">AI Agents</h2>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
          <span>{displayAgents.filter(a => a.status === 'active' || a.status === 'working').length} active</span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 h-full overflow-auto custom-scrollbar">
        {displayAgents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
    </div>
  );
};

export default AgentGrid;
