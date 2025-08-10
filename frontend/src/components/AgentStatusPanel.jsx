import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Activity, AlertTriangle, CheckCircle, Bot, Clock } from 'lucide-react'
import { getApiUrl, getWsUrl } from '../config'

const AgentStatusPanel = () => {
  const [agentStatus, setAgentStatus] = useState({})
  const [wsConnected, setWsConnected] = useState(false)
  const reconnectTimeoutRef = useRef(null)
  const isMountedRef = useRef(true) // Track if component is mounted
  const pollingIntervalRef = useRef(null) // For periodic status checks
  const [lastUpdate, setLastUpdate] = useState(null)

  // Safe state setter that checks if component is mounted
  const safeSetState = useCallback((setter, value) => {
    if (isMountedRef.current) {
      setter(value)
    }
  }, [])

  useEffect(() => {
    // Initial fetch of agent status
    const fetchAgentStatus = async () => {
      if (!isMountedRef.current) return
      
      try {
        const response = await fetch(getApiUrl('/api/agents'))
        if (response.ok) {
          const agents = await response.json()
          const statusMap = {}
          agents.forEach(agent => {
            statusMap[agent.agent_id] = agent
          })
          safeSetState(setAgentStatus, statusMap)
          safeSetState(setLastUpdate, new Date())
        }
      } catch (error) {
        console.error('Failed to fetch agent status:', error)
      }
    }

    // WebSocket for real-time updates
    const connectWebSocket = () => {
      if (!isMountedRef.current) return
      
      try {
        const wsUrl = getWsUrl('/ws/agent-status')
        const ws = new WebSocket(wsUrl)
        
        ws.onopen = () => {
          console.log('WebSocket connected to agent status panel')
          safeSetState(setWsConnected, true)
        }

        ws.onmessage = (event) => {
          if (!isMountedRef.current) return
          
          try {
            const data = JSON.parse(event.data)
            if (data.type === 'agent_status_update') {
              safeSetState(setAgentStatus, prev => ({
                ...prev,
                [data.data.agent_id]: data.data
              }))
              safeSetState(setLastUpdate, new Date())
            }
          } catch (e) {
            console.error('Error parsing WebSocket message:', e)
          }
        }

        ws.onclose = () => {
          console.log('WebSocket disconnected from agent status panel')
          safeSetState(setWsConnected, false)
          // Only reconnect if component is mounted and no existing timeout
          if (isMountedRef.current && !reconnectTimeoutRef.current) {
            reconnectTimeoutRef.current = setTimeout(() => {
              if (isMountedRef.current) {
                reconnectTimeoutRef.current = null
                connectWebSocket()
              }
            }, 3000)
          }
        }

        ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          safeSetState(setWsConnected, false)
        }

        return ws
      } catch (error) {
        console.error('WebSocket connection failed:', error)
        // Only reconnect if component is mounted and no existing timeout
        if (isMountedRef.current && !reconnectTimeoutRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            if (isMountedRef.current) {
              reconnectTimeoutRef.current = null
              connectWebSocket()
            }
          }, 3000)
        }
      }
    }

    // Delay initial fetch and WebSocket connection to ensure backend is ready
    const timeoutId = setTimeout(() => {
      if (isMountedRef.current) {
        fetchAgentStatus()
        const ws = connectWebSocket()
        
        // Start periodic polling as fallback (every 5 seconds)
        pollingIntervalRef.current = setInterval(() => {
          if (isMountedRef.current) {
            fetchAgentStatus()
          }
        }, 5000)
        
        // Cleanup function
        return () => {
          if (ws) {
            ws.close()
          }
        }
      }
    }, 1500)

    return () => {
      clearTimeout(timeoutId)
      isMountedRef.current = false
      
      // Clear any pending reconnection timeout
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      
      // Clear polling interval
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
        pollingIntervalRef.current = null
      }
    }
  }, [safeSetState])

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'issues_detected':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      case 'high_issues':
        return <AlertTriangle className="h-5 w-5 text-orange-500" />
      case 'critical_issues':
        return <AlertTriangle className="h-5 w-5 text-red-500" />
      default:
        return <Activity className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'border-green-200 bg-green-50'
      case 'issues_detected':
        return 'border-yellow-200 bg-yellow-50'
      case 'high_issues':
        return 'border-orange-200 bg-orange-50'
      case 'critical_issues':
        return 'border-red-200 bg-red-50'
      default:
        return 'border-gray-200 bg-gray-50'
    }
  }

  const formatStatus = (status) => {
    switch (status) {
      case 'healthy':
        return 'Healthy'
      case 'issues_detected':
        return 'Issues Detected'
      case 'high_issues':
        return 'High Priority Issues'
      case 'critical_issues':
        return 'Critical Issues'
      default:
        return 'Unknown'
    }
  }

  const autonomousMonitor = agentStatus['autonomous_monitor']

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Bot className="h-6 w-6 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-900">Agent Status</h2>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`h-2 w-2 rounded-full ${wsConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
          <span className="text-sm text-gray-600">
            {wsConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {autonomousMonitor ? (
        <div className={`border rounded-lg p-4 ${getStatusColor(autonomousMonitor.status)}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              {getStatusIcon(autonomousMonitor.status)}
              <div>
                <h3 className="font-semibold text-gray-900">Autonomous Monitor</h3>
                <p className="text-sm text-gray-600">{formatStatus(autonomousMonitor.status)}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">
                {new Date(autonomousMonitor.last_update).toLocaleTimeString()}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {autonomousMonitor.issues_count}
              </div>
              <div className="text-xs text-gray-600">Issues</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {autonomousMonitor.nodes_ready}/{autonomousMonitor.nodes_total}
              </div>
              <div className="text-xs text-gray-600">Nodes</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {autonomousMonitor.pods_running}
              </div>
              <div className="text-xs text-gray-600">Running Pods</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {autonomousMonitor.pods_total}
              </div>
              <div className="text-xs text-gray-600">Total Pods</div>
            </div>
          </div>
        </div>
      ) : (
        <div className="border border-gray-200 rounded-lg p-6 text-center">
          <Clock className="h-8 w-8 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-600">Waiting for agent status...</p>
          <p className="text-sm text-gray-400 mt-1">
            Make sure the autonomous monitor is running
          </p>
        </div>
      )}
    </div>
  )
}

export default AgentStatusPanel 