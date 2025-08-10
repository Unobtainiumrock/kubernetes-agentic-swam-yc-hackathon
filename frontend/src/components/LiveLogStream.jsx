import React, { useState, useEffect, useRef, useCallback } from 'react'
import { FileText, Play, Pause, X, ExternalLink } from 'lucide-react'

const LiveLogStream = () => {
  const [logs, setLogs] = useState([])
  const [isStreaming, setIsStreaming] = useState(true)
  const [filter, setFilter] = useState('all')
  const [wsConnected, setWsConnected] = useState(false)
  const [agentStatus, setAgentStatus] = useState({})
  const logContainerRef = useRef(null)
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const isMountedRef = useRef(true) // Track if component is mounted

  // Safe state setter that checks if component is still mounted
  const safeSetState = useCallback((setter, value) => {
    if (isMountedRef.current) {
      setter(value)
    }
  }, [])

  // WebSocket connection function
  const connectWebSocket = useCallback(() => {
    // Don't connect if component is unmounted or not streaming
    if (!isMountedRef.current || !isStreaming) return
    
    // Don't create multiple connections
    if (wsRef.current?.readyState === WebSocket.CONNECTING || 
        wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      const wsUrl = `ws://localhost:8001/ws/agent-status`
      wsRef.current = new WebSocket(wsUrl)

      wsRef.current.onopen = () => {
        console.log('WebSocket connected to agent status')
        safeSetState(setWsConnected, true)
      }

      wsRef.current.onmessage = (event) => {
        if (!isMountedRef.current) return
        
        try {
          const data = JSON.parse(event.data)
          
          if (data.type === 'agent_log') {
            const logEntry = data.data
            const newLog = {
              id: `${logEntry.timestamp}-${logEntry.agent_id}-${Date.now()}-${Math.random()}`,
              timestamp: logEntry.timestamp,
              level: logEntry.log_level,
              source: logEntry.agent_id,
              message: logEntry.message,
              details: logEntry.details
            }
            
            safeSetState(setLogs, prev => [newLog, ...prev.slice(0, 99)])
          } else if (data.type === 'agent_status_update') {
            safeSetState(setAgentStatus, prev => ({
              ...prev,
              [data.data.agent_id]: data.data
            }))
          }
        } catch (e) {
          console.error('Error parsing WebSocket message:', e)
        }
      }

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected')
        safeSetState(setWsConnected, false)
        
        // Only reconnect if component is mounted, streaming, and no existing timeout
        if (isMountedRef.current && isStreaming && !reconnectTimeoutRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            if (isMountedRef.current) {
              reconnectTimeoutRef.current = null
              connectWebSocket()
            }
          }, 3000)
        }
      }

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        safeSetState(setWsConnected, false)
      }
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      
      // Only reconnect if component is mounted, streaming, and no existing timeout
      if (isMountedRef.current && isStreaming && !reconnectTimeoutRef.current) {
        reconnectTimeoutRef.current = setTimeout(() => {
          if (isMountedRef.current) {
            reconnectTimeoutRef.current = null
            connectWebSocket()
          }
        }, 3000)
      }
    }
  }, [isStreaming, safeSetState])

  // WebSocket connection effect
  useEffect(() => {
    if (isStreaming) {
      // Small delay to ensure backend is ready
      const timeoutId = setTimeout(() => {
        if (isMountedRef.current) {
          connectWebSocket()
        }
      }, 1000)
      
      return () => {
        clearTimeout(timeoutId)
      }
    } else {
      // Clear reconnection timeout when stopping streaming
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      // Close WebSocket
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [isStreaming, connectWebSocket])

  // Cleanup effect
  useEffect(() => {
    return () => {
      isMountedRef.current = false
      
      // Clear any pending reconnection timeout
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      
      // Close WebSocket connection
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  // Fetch initial logs from API
  useEffect(() => {
    const fetchInitialLogs = async () => {
      if (!isMountedRef.current) return
      
      try {
        const response = await fetch('http://localhost:8001/api/agents/logs/stream?limit=20')
        if (response.ok && isMountedRef.current) {
          const initialLogs = await response.json()
          const formattedLogs = initialLogs.map((log, index) => ({
            id: `${log.timestamp}-${log.agent_id}-${index}-${Math.random()}`,
            timestamp: log.timestamp,
            level: log.log_level,
            source: log.agent_id,
            message: log.message,
            details: log.details
          }))
          safeSetState(setLogs, formattedLogs)
        }
      } catch (error) {
        console.error('Failed to fetch initial logs:', error)
      }
    }

    // Delay initial fetch to ensure backend is ready
    const timeoutId = setTimeout(fetchInitialLogs, 2000)
    return () => clearTimeout(timeoutId)
  }, [safeSetState])

  // Toggle streaming
  const toggleStreaming = () => {
    setIsStreaming(!isStreaming)
  }

  // Auto-scroll to top when new logs arrive
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = 0
    }
  }, [logs])

  const getLevelColor = (level) => {
    switch (level) {
      case 'error': return 'text-red-600 bg-red-50'
      case 'warn': return 'text-yellow-600 bg-yellow-50'
      case 'info': return 'text-blue-600 bg-blue-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getSourceColor = (source) => {
    switch (source) {
      case 'autonomous_monitor': return 'text-purple-600 bg-purple-50'
      case 'deterministic_investigator': return 'text-green-600 bg-green-50'
      case 'agentic_investigator': return 'text-blue-600 bg-blue-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const renderLogMessage = (log) => {
    // Check if this is an investigation report link
    if (log.details && log.details.report_file) {
      return (
        <div className="flex items-center space-x-2">
          <span>{log.message}</span>
          <button 
            onClick={() => window.open(`http://localhost:8001/reports/${log.details.report_file.split('/').pop()}`, '_blank')}
            className="inline-flex items-center px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
          >
            <ExternalLink className="h-3 w-3 mr-1" />
            View Report
          </button>
        </div>
      )
    }
    
    // Check if this has issue details
    if (log.details && log.details.issues_summary) {
      return (
        <div>
          <div>{log.message}</div>
          <div className="mt-1 text-xs text-gray-400">
            Issues: {log.details.issues_summary.join(', ')}
          </div>
        </div>
      )
    }
    
    return log.message
  }

  const filteredLogs = filter === 'all' ? logs : logs.filter(log => log.level === filter)

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <FileText className="h-6 w-6 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-900">Live Logs</h2>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={toggleStreaming}
            className={`p-2 rounded-lg transition-colors ${
              isStreaming 
                ? 'bg-green-100 text-green-600 hover:bg-green-200' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {isStreaming ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </button>
          
          <button 
            onClick={() => setLogs([])}
            className="p-2 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-4">
        <div className="flex space-x-2">
          {['all', 'info', 'warn', 'error'].map((level) => (
            <button
              key={level}
              onClick={() => setFilter(level)}
              className={`
                px-3 py-1 rounded-full text-xs font-medium transition-colors
                ${filter === level 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }
              `}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Log stream */}
      <div 
        ref={logContainerRef}
        className="space-y-2 max-h-80 overflow-y-auto bg-gray-950 rounded-lg p-4 font-mono text-sm"
      >
        {filteredLogs.length > 0 ? (
          filteredLogs.map((log) => (
            <div key={log.id} className="flex items-start space-x-3 text-gray-300">
              <span className="text-gray-500 text-xs whitespace-nowrap">
                {formatTimestamp(log.timestamp)}
              </span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${getLevelColor(log.level)}`}>
                {log.level.toUpperCase()}
              </span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${getSourceColor(log.source)}`}>
                {log.source}
              </span>
              <span className="flex-1 text-gray-100">
                {renderLogMessage(log)}
              </span>
            </div>
          ))
        ) : (
          <div className="text-center text-gray-500 py-8">
            No logs to display
          </div>
        )}
      </div>

      {/* Stream status */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-2">
            <div className={`h-2 w-2 rounded-full ${
              wsConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'
            }`}></div>
            <span className="text-gray-600">
              {wsConnected ? 'Connected' : 'Disconnected'}
            </span>
            {Object.keys(agentStatus).length > 0 && (
              <span className="text-xs text-gray-500">
                | {Object.values(agentStatus)[0]?.issues_count || 0} issues detected
              </span>
            )}
          </div>
          <span className="text-gray-500">
            {filteredLogs.length} entries
          </span>
        </div>
      </div>
    </div>
  )
}

export default LiveLogStream 