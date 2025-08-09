import React from 'react';
import AgentGrid from './AgentGrid';
import ClusterOverview from './ClusterOverview';
import EventStream from './EventStream';
import MetricsPanel from './MetricsPanel';

const Dashboard = () => {
  return (
    <div className="space-y-6 h-full">
      {/* Top Row - Cluster Overview and Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ClusterOverview />
        <MetricsPanel />
      </div>

      {/* Middle Row - Agent Grid */}
      <div className="h-64">
        <AgentGrid />
      </div>

      {/* Bottom Row - Event Stream */}
      <div className="flex-1 min-h-0">
        <EventStream />
      </div>
    </div>
  );
};

export default Dashboard;
