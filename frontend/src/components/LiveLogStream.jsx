import React, { useState, useEffect, useRef } from 'react'
import { FileText, Play, Pause, X } from 'lucide-react'

const LiveLogStream = () => {
  const [logs, setLogs] = useState([])
  const [isStreaming, setIsStreaming] = useState(true)
  const [filter, setFilter] = useState('all')
  const logContainerRef = useRef(null)

  // Mock log data
  const mockLogs = [
    { id: 1, timestamp: new Date().toISOString(), level: 'info', source: 'agent-001', message: 'Started monitoring frontend namespace' },
    { id: 2, timestamp: new Date().toISOString(), level: 'info', source: 'agent-002', message: 'Detected pod restart in backend namespace' },
    { id: 3, timestamp: new Date().toISOString(), level: 'warn', source: 'agent-001', message: 'High CPU usage detected on worker-2' },
    { id: 4, timestamp: new Date().toISOString(), level: 'info', source: 'agent-002', message: 'Successfully scaled deployment backend-app from 2 to 4 replicas' },
    { id: 5, timestamp: new Date().toISOString(), level: 'error', source: 'agent-001', message: 'Failed to connect to pod frontend-app-xyz' }
  ]

  useEffect(() => {
    setLogs(mockLogs)
  }, [])

  // Simulate real-time log streaming
  useEffect(() => {
    if (!isStreaming) return

    const interval = setInterval(() => {
      const newLog = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        level: ['info', 'warn', 'error'][Math.floor(Math.random() * 3)],
        source: ['agent-001', 'agent-002'][Math.floor(Math.random() * 2)],
        message: [
          'Monitoring cluster health',
          'Detected anomaly in pod scheduling',
          'Auto-scaling triggered for backend service',
          'Network connectivity check completed',
          'Pod memory usage within normal range',
          'Database connection pool optimized'
        ][Math.floor(Math.random() * 6)]
      }

      setLogs(prev => [newLog, ...prev.slice(0, 49)]) // Keep last 50 logs
    }, 3000)

    return () => clearInterval(interval)
  }, [isStreaming])

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
      case 'agent-001': return 'text-purple-600 bg-purple-50'
      case 'agent-002': return 'text-green-600 bg-green-50'
      default: return 'text-gray-600 bg-gray-50'
    }
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
            onClick={() => setIsStreaming(!isStreaming)}
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
                {log.message}
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
            <div className={`h-2 w-2 rounded-full ${isStreaming ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`}></div>
            <span className="text-gray-600">
              {isStreaming ? 'Streaming live' : 'Stream paused'}
            </span>
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