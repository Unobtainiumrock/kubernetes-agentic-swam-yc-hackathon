import React, { useState, useEffect } from 'react'
import { Bot, Activity, AlertCircle, CheckCircle, Clock, PlayCircle, StopCircle } from 'lucide-react'

const AgentStatusGrid = () => {
  const [agents, setAgents] = useState([
    {
      id: 'agent-001',
      name: 'Cluster Monitor',
      status: 'running',
      lastAction: 'Monitoring pod health in frontend namespace',
      lastSeen: new Date(),
      namespace: 'frontend',
      actionsToday: 8,
      uptime: '2h 34m'
    },
    {
      id: 'agent-002',
      name: 'Healing Agent',
      status: 'idle',
      lastAction: 'Restarted failed pod: backend-app-xyz',
      lastSeen: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
      namespace: 'backend',
      actionsToday: 4,
      uptime: '2h 34m'
    }
  ])

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <PlayCircle className="h-4 w-4 text-green-500" />
      case 'idle':
        return <CheckCircle className="h-4 w-4 text-blue-500" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      case 'stopped':
        return <StopCircle className="h-4 w-4 text-gray-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'status-running'
      case 'idle':
        return 'status-idle'
      case 'error':
        return 'status-failed'
      case 'stopped':
        return 'status-pending'
      default:
        return 'status-pending'
    }
  }

  const handleAgentAction = (agentId, action) => {
    setAgents(prev => prev.map(agent => 
      agent.id === agentId 
        ? { 
            ...agent, 
            status: action === 'restart' ? 'running' : 'stopped',
            lastSeen: new Date()
          }
        : agent
    ))
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Bot className="h-6 w-6 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-900">Agent Status</h2>
        </div>
        <div className="flex items-center space-x-2">
          <div className="h-2 w-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-600">Live Updates</span>
        </div>
      </div>

      <div className="space-y-4">
        {agents.map((agent) => (
          <div key={agent.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <div className="h-10 w-10 bg-agent-primary rounded-lg flex items-center justify-center">
                    <Bot className="h-5 w-5 text-pink-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{agent.name}</h3>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(agent.status)}
                      <span className={`${getStatusColor(agent.status)} capitalize`}>
                        {agent.status}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Last Action:</span> {agent.lastAction}
                  </p>
                  
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    <span>Namespace: {agent.namespace}</span>
                    <span>Actions today: {agent.actionsToday}</span>
                    <span>Uptime: {agent.uptime}</span>
                  </div>
                  
                  <div className="flex items-center space-x-2 text-xs text-gray-500">
                    <Clock className="h-3 w-3" />
                    <span>Last seen: {agent.lastSeen.toLocaleTimeString()}</span>
                  </div>
                </div>
              </div>
              
              <div className="flex space-x-2 ml-4">
                <button
                  onClick={() => handleAgentAction(agent.id, 'restart')}
                  className="btn-secondary text-xs py-1 px-2"
                  disabled={agent.status === 'running'}
                >
                  Restart
                </button>
                <button
                  onClick={() => handleAgentAction(agent.id, 'stop')}
                  className="btn-danger text-xs py-1 px-2"
                  disabled={agent.status === 'stopped'}
                >
                  Stop
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">
            {agents.filter(a => a.status === 'running').length} of {agents.length} agents active
          </span>
          <button className="btn-primary text-xs py-1 px-3">
            View All Agents
          </button>
        </div>
      </div>
    </div>
  )
}

export default AgentStatusGrid 