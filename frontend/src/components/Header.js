import React from 'react';
import { Activity, Wifi, WifiOff, Bot, Shield } from 'lucide-react';

const Header = ({ connected }) => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-lg">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                K8s Agent Dashboard
              </h1>
              <p className="text-sm text-gray-500">
                Agentic Kubernetes Operator
              </p>
            </div>
          </div>

          {/* Status Indicators */}
          <div className="flex items-center space-x-6">
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              {connected ? (
                <>
                  <Wifi className="w-5 h-5 text-success-600" />
                  <span className="text-sm font-medium text-success-600">
                    Connected
                  </span>
                </>
              ) : (
                <>
                  <WifiOff className="w-5 h-5 text-danger-600" />
                  <span className="text-sm font-medium text-danger-600">
                    Disconnected
                  </span>
                </>
              )}
            </div>

            {/* Cluster Status */}
            <div className="flex items-center space-x-2">
              <Shield className="w-5 h-5 text-primary-600" />
              <span className="text-sm font-medium text-gray-700">
                demo-cluster
              </span>
            </div>

            {/* Activity Indicator */}
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-warning-600 animate-pulse" />
              <span className="text-sm font-medium text-gray-700">
                Monitoring
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
