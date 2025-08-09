import React from 'react';
import { useAgent } from '../contexts/AgentContext';
import { Server, Box, Globe, Database, AlertTriangle, CheckCircle } from 'lucide-react';

const MetricCard = ({ icon: Icon, label, value, status = 'normal' }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'warning':
        return 'text-warning-600';
      case 'error':
        return 'text-danger-600';
      case 'success':
        return 'text-success-600';
      default:
        return 'text-gray-900';
    }
  };

  return (
    <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
      <Icon className={`w-5 h-5 ${getStatusColor(status)}`} />
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className={`text-lg font-semibold ${getStatusColor(status)}`}>{value}</p>
      </div>
    </div>
  );
};

const ClusterOverview = () => {
  const { clusterMetrics, loading } = useAgent();

  // Mock data if not available
  const mockMetrics = {
    nodes: 5,
    pods: 23,
    services: 8,
    deployments: 6,
    healthyPods: 21,
    unhealthyPods: 2,
    cpuUsage: 45,
    memoryUsage: 62
  };

  const metrics = Object.keys(clusterMetrics).length > 0 ? clusterMetrics : mockMetrics;

  if (loading) {
    return (
      <div className="card h-full">
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  const podHealthStatus = metrics.unhealthyPods > 0 ? 'warning' : 'success';
  const resourceStatus = metrics.cpuUsage > 80 || metrics.memoryUsage > 80 ? 'error' : 
                        metrics.cpuUsage > 60 || metrics.memoryUsage > 60 ? 'warning' : 'normal';

  return (
    <div className="card h-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Cluster Overview</h2>
        <div className="flex items-center space-x-2">
          <CheckCircle className="w-5 h-5 text-success-600" />
          <span className="text-sm text-success-600 font-medium">demo-cluster</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <MetricCard
          icon={Server}
          label="Nodes"
          value={metrics.nodes}
          status="success"
        />
        <MetricCard
          icon={Box}
          label="Pods"
          value={`${metrics.pods} (${metrics.healthyPods}/${metrics.unhealthyPods})`}
          status={podHealthStatus}
        />
        <MetricCard
          icon={Globe}
          label="Services"
          value={metrics.services}
        />
        <MetricCard
          icon={Database}
          label="Deployments"
          value={metrics.deployments}
        />
      </div>

      {/* Resource Usage */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-gray-700">Resource Usage</h3>
        
        {/* CPU Usage */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">CPU</span>
            <span className={`font-medium ${resourceStatus === 'error' ? 'text-danger-600' : 
                           resourceStatus === 'warning' ? 'text-warning-600' : 'text-gray-900'}`}>
              {metrics.cpuUsage}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${
                metrics.cpuUsage > 80 ? 'bg-danger-500' :
                metrics.cpuUsage > 60 ? 'bg-warning-500' : 'bg-success-500'
              }`}
              style={{ width: `${metrics.cpuUsage}%` }}
            ></div>
          </div>
        </div>

        {/* Memory Usage */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Memory</span>
            <span className={`font-medium ${resourceStatus === 'error' ? 'text-danger-600' : 
                           resourceStatus === 'warning' ? 'text-warning-600' : 'text-gray-900'}`}>
              {metrics.memoryUsage}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${
                metrics.memoryUsage > 80 ? 'bg-danger-500' :
                metrics.memoryUsage > 60 ? 'bg-warning-500' : 'bg-success-500'
              }`}
              style={{ width: `${metrics.memoryUsage}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Health Status */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Cluster Health</span>
          <div className="flex items-center space-x-2">
            {metrics.unhealthyPods === 0 ? (
              <>
                <CheckCircle className="w-4 h-4 text-success-600" />
                <span className="text-sm font-medium text-success-600">Healthy</span>
              </>
            ) : (
              <>
                <AlertTriangle className="w-4 h-4 text-warning-600" />
                <span className="text-sm font-medium text-warning-600">
                  {metrics.unhealthyPods} issue{metrics.unhealthyPods > 1 ? 's' : ''}
                </span>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClusterOverview;
