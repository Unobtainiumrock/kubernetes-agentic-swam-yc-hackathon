import React from 'react'
import { TrendingUp, Cpu, HardDrive, Activity } from 'lucide-react'

const MetricsPanel = ({ metrics }) => {
  const getUsageColor = (usage) => {
    if (usage > 80) return 'text-red-600'
    if (usage > 60) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getUsageBgColor = (usage) => {
    if (usage > 80) return 'bg-red-500'
    if (usage > 60) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  return (
    <div className="card">
      <div className="flex items-center space-x-3 mb-6">
        <TrendingUp className="h-6 w-6 text-blue-600" />
        <h2 className="text-lg font-semibold text-gray-900">Cluster Metrics</h2>
      </div>

      <div className="space-y-6">
        {/* CPU Usage */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Cpu className="h-4 w-4 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">CPU Usage</span>
            </div>
            <span className={`text-sm font-semibold ${getUsageColor(metrics.cpuUsage)}`}>
              {metrics.cpuUsage.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-500 ${getUsageBgColor(metrics.cpuUsage)}`}
              style={{ width: `${metrics.cpuUsage}%` }}
            ></div>
          </div>
        </div>

        {/* Memory Usage */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <HardDrive className="h-4 w-4 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">Memory Usage</span>
            </div>
            <span className={`text-sm font-semibold ${getUsageColor(metrics.memoryUsage)}`}>
              {metrics.memoryUsage.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-500 ${getUsageBgColor(metrics.memoryUsage)}`}
              style={{ width: `${metrics.memoryUsage}%` }}
            ></div>
          </div>
        </div>

        {/* Pod Health */}
        <div className="pt-4 border-t border-gray-200">
          <div className="flex items-center space-x-2 mb-3">
            <Activity className="h-4 w-4 text-gray-400" />
            <span className="text-sm font-medium text-gray-700">Pod Health</span>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Running</span>
              <div className="flex items-center space-x-2">
                <div className="w-16 bg-gray-200 rounded-full h-1">
                  <div 
                    className="h-1 bg-green-500 rounded-full"
                    style={{ width: `${(metrics.runningPods / metrics.totalPods) * 100}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-500 w-8">{metrics.runningPods}</span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Failed</span>
              <div className="flex items-center space-x-2">
                <div className="w-16 bg-gray-200 rounded-full h-1">
                  <div 
                    className="h-1 bg-red-500 rounded-full"
                    style={{ width: `${(metrics.failedPods / metrics.totalPods) * 100}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-500 w-8">{metrics.failedPods}</span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Total</span>
              <span className="text-sm font-medium text-gray-900">{metrics.totalPods}</span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="pt-4 border-t border-gray-200">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Actions</h3>
          <div className="space-y-2">
            <button className="w-full btn-secondary text-xs py-2">
              Trigger Chaos Scenario
            </button>
            <button className="w-full btn-secondary text-xs py-2">
              View Detailed Metrics
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MetricsPanel 