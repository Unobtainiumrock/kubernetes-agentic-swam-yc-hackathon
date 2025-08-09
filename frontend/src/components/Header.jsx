import React from 'react'
import { Activity, Bot, Server } from 'lucide-react'

const Header = () => {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Bot className="h-8 w-8 text-blue-600" />
            <h1 className="text-xl font-bold text-gray-900">
              Agentic K8s Operator
            </h1>
          </div>
          <div className="hidden md:flex items-center space-x-1 text-sm text-gray-500">
            <Server className="h-4 w-4" />
            <span>demo-cluster</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="h-2 w-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600">Live</span>
          </div>
          
          <div className="flex items-center space-x-2 text-sm">
            <Activity className="h-4 w-4 text-gray-400" />
            <span className="text-gray-600">2 Agents Active</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header 