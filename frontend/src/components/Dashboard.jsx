import React, { useState, useEffect } from 'react'
import { 
  Bot, 
  Server, 
  Activity, 
  Zap, 
  AlertTriangle, 
  CheckCircle,
  Clock,
  TrendingUp
} from 'lucide-react'
import AgentStatusGrid from './AgentStatusGrid'
import ClusterView from './ClusterView'
import MetricsPanel from './MetricsPanel'
import LiveLogStream from './LiveLogStream'

const Dashboard = () => {
  const [clusterMetrics, setClusterMetrics] = useState({
    totalNodes: 5,
    readyNodes: 5,
    totalPods: 15,
    runningPods: 13,
    failedPods: 2,
    cpuUsage: 24.5,
    memoryUsage: 38.2
  })

  const [agentStats, setAgentStats] = useState({
    totalAgents: 2,
    activeAgents: 2,
    lastAction: "2 minutes ago",
    actionsToday: 12
  })

  // Mock real-time data updates
  useEffect(() => {
    const interval = setInterval(() => {
      setClusterMetrics(prev => ({
        ...prev,
        cpuUsage: Math.max(10, Math.min(80, prev.cpuUsage + (Math.random() - 0.5) * 5)),
        memoryUsage: Math.max(20, Math.min(90, prev.memoryUsage + (Math.random() - 0.5) * 3))
      }))
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Real-time overview of your agentic Kubernetes cluster</p>
      </div>

      {/* Quick Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Agents</p>
              <p className="text-2xl font-bold text-gray-900">{agentStats.activeAgents}</p>
            </div>
            <div className="h-12 w-12 bg-agent-primary rounded-lg flex items-center justify-center">
              <Bot className="h-6 w-6 text-pink-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600">All systems operational</span>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cluster Nodes</p>
              <p className="text-2xl font-bold text-gray-900">
                {clusterMetrics.readyNodes}/{clusterMetrics.totalNodes}
              </p>
            </div>
            <div className="h-12 w-12 bg-cluster-primary rounded-lg flex items-center justify-center">
              <Server className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600">All nodes ready</span>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Running Pods</p>
              <p className="text-2xl font-bold text-gray-900">
                {clusterMetrics.runningPods}/{clusterMetrics.totalPods}
              </p>
            </div>
            <div className="h-12 w-12 bg-frontend-primary rounded-lg flex items-center justify-center">
              <Activity className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            {clusterMetrics.failedPods > 0 ? (
              <>
                <AlertTriangle className="h-4 w-4 text-yellow-500 mr-1" />
                <span className="text-yellow-600">{clusterMetrics.failedPods} pods need attention</span>
              </>
            ) : (
              <>
                <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
                <span className="text-green-600">All pods healthy</span>
              </>
            )}
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Agent Actions</p>
              <p className="text-2xl font-bold text-gray-900">{agentStats.actionsToday}</p>
            </div>
            <div className="h-12 w-12 bg-backend-primary rounded-lg flex items-center justify-center">
              <Zap className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <Clock className="h-4 w-4 text-gray-400 mr-1" />
            <span className="text-gray-600">Last action {agentStats.lastAction}</span>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent Status - Takes 2 columns */}
        <div className="lg:col-span-2">
          <AgentStatusGrid />
        </div>
        
        {/* Metrics Panel */}
        <div>
          <MetricsPanel metrics={clusterMetrics} />
        </div>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cluster View */}
        <div>
          <ClusterView />
        </div>
        
        {/* Live Logs */}
        <div>
          <LiveLogStream />
        </div>
      </div>
    </div>
  )
}

export default Dashboard 