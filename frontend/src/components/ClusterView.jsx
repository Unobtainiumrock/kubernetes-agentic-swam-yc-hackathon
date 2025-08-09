import React, { useState } from 'react'
import { Server, Box, CheckCircle, AlertTriangle, Clock } from 'lucide-react'

const ClusterView = () => {
  const [selectedNode, setSelectedNode] = useState(null)
  
  const nodes = [
    {
      name: 'control-plane',
      role: 'control-plane',
      status: 'Ready',
      pods: 8,
      tier: 'control',
      zone: 'us-west-1a'
    },
    {
      name: 'worker-1',
      role: 'worker',
      status: 'Ready',
      pods: 12,
      tier: 'frontend',
      zone: 'us-west-1a'
    },
    {
      name: 'worker-2',
      role: 'worker',
      status: 'Ready',
      pods: 10,
      tier: 'backend',
      zone: 'us-west-1b'
    },
    {
      name: 'worker-3',
      role: 'worker',
      status: 'Ready',
      pods: 8,
      tier: 'database',
      zone: 'us-west-1c'
    },
    {
      name: 'worker-4',
      role: 'worker',
      status: 'Ready',
      pods: 6,
      tier: 'cache',
      zone: 'us-west-1a'
    }
  ]

  const getTierColor = (tier) => {
    switch (tier) {
      case 'control': return 'bg-purple-100 border-purple-300'
      case 'frontend': return 'bg-frontend-primary border-blue-300'
      case 'backend': return 'bg-backend-primary border-green-300'
      case 'database': return 'bg-yellow-100 border-yellow-300'
      case 'cache': return 'bg-gray-100 border-gray-300'
      default: return 'bg-gray-100 border-gray-300'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Ready':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'NotReady':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  return (
    <div className="card">
      <div className="flex items-center space-x-3 mb-6">
        <Server className="h-6 w-6 text-blue-600" />
        <h2 className="text-lg font-semibold text-gray-900">Cluster View</h2>
      </div>

      <div className="space-y-4">
        {/* Cluster topology */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {nodes.map((node) => (
            <div
              key={node.name}
              onClick={() => setSelectedNode(node)}
              className={`
                p-3 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md
                ${getTierColor(node.tier)}
                ${selectedNode?.name === node.name ? 'ring-2 ring-blue-500' : ''}
              `}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <Server className="h-4 w-4 text-gray-600" />
                  <span className="text-xs font-medium text-gray-900">
                    {node.name}
                  </span>
                </div>
                {getStatusIcon(node.status)}
              </div>
              
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">Role:</span>
                  <span className="font-medium text-gray-900">{node.role}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">Pods:</span>
                  <span className="font-medium text-gray-900">{node.pods}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">Tier:</span>
                  <span className="font-medium text-gray-900 capitalize">{node.tier}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Selected node details */}
        {selectedNode && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg border">
            <h3 className="font-medium text-gray-900 mb-3">
              Node Details: {selectedNode.name}
            </h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Status:</span>
                <div className="flex items-center space-x-2 mt-1">
                  {getStatusIcon(selectedNode.status)}
                  <span className="font-medium">{selectedNode.status}</span>
                </div>
              </div>
              <div>
                <span className="text-gray-600">Zone:</span>
                <p className="font-medium mt-1">{selectedNode.zone}</p>
              </div>
              <div>
                <span className="text-gray-600">Role:</span>
                <p className="font-medium mt-1 capitalize">{selectedNode.role}</p>
              </div>
              <div>
                <span className="text-gray-600">Pod Count:</span>
                <p className="font-medium mt-1">{selectedNode.pods} pods</p>
              </div>
            </div>
          </div>
        )}

        {/* Legend */}
        <div className="pt-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Tier Legend</h4>
          <div className="flex flex-wrap gap-2">
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-purple-100 border border-purple-300 rounded"></div>
              <span className="text-xs text-gray-600">Control</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-frontend-primary border border-blue-300 rounded"></div>
              <span className="text-xs text-gray-600">Frontend</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-backend-primary border border-green-300 rounded"></div>
              <span className="text-xs text-gray-600">Backend</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-yellow-100 border border-yellow-300 rounded"></div>
              <span className="text-xs text-gray-600">Database</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-gray-100 border border-gray-300 rounded"></div>
              <span className="text-xs text-gray-600">Cache</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ClusterView 