import React, { useState, useEffect } from 'react';
import { Bot, Activity, Wifi, WifiOff, MessageSquare, Send, Server, Box, AlertCircle } from 'lucide-react';

function App() {
  const [connected, setConnected] = useState(false);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: 'Hello! I\'m your Kubernetes infrastructure assistant. I can help you understand your cluster, diagnose issues, and perform operations.',
      timestamp: new Date().toISOString()
    }
  ]);

  // Mock connection status
  useEffect(() => {
    const timer = setTimeout(() => setConnected(true), 1000);
    return () => clearTimeout(timer);
  }, []);

  const sendMessage = () => {
    if (!message.trim()) return;
    
    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    
    // Mock AI response
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `I understand you're asking about: "${message}". This is a mock response - the FastAPI backend will provide real k8sgpt-powered responses soon!`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-lg">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">K8s Agent Dashboard</h1>
                <p className="text-sm text-gray-500">Agentic Kubernetes Operator</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                {connected ? (
                  <>
                    <Wifi className="w-5 h-5 text-success-600" />
                    <span className="text-sm font-medium text-success-600">Connected</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="w-5 h-5 text-danger-600" />
                    <span className="text-sm font-medium text-danger-600">Disconnected</span>
                  </>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <Activity className="w-5 h-5 text-warning-600 animate-pulse" />
                <span className="text-sm font-medium text-gray-700">demo-cluster</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-120px)]">
          
          {/* Dashboard Section */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Cluster Overview */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Cluster Overview</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <Server className="w-8 h-8 text-primary-600 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-gray-900">5</p>
                  <p className="text-sm text-gray-500">Nodes</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <Box className="w-8 h-8 text-success-600 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-gray-900">23</p>
                  <p className="text-sm text-gray-500">Pods</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <Activity className="w-8 h-8 text-warning-600 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-gray-900">4</p>
                  <p className="text-sm text-gray-500">Agents</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <AlertCircle className="w-8 h-8 text-danger-600 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-gray-900">2</p>
                  <p className="text-sm text-gray-500">Issues</p>
                </div>
              </div>
            </div>

            {/* Agent Status */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Agents</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { name: 'Diagnostic Agent', status: 'active', task: 'Monitoring pod health' },
                  { name: 'Healing Agent', status: 'working', task: 'Scaling backend deployment' },
                  { name: 'Security Agent', status: 'idle', task: 'Standby' },
                  { name: 'Resource Agent', status: 'active', task: 'Optimizing resources' }
                ].map((agent, index) => (
                  <div key={index} className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-gray-900">{agent.name}</h3>
                      <span className={`status-${agent.status}`}>{agent.status}</span>
                    </div>
                    <p className="text-sm text-gray-600">{agent.task}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Events */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Events</h2>
              <div className="space-y-2 max-h-48 overflow-y-auto custom-scrollbar">
                {[
                  { time: '14:35', event: 'Backend deployment scaled to 6 replicas', type: 'info' },
                  { time: '14:33', event: 'Pod frontend-app-xyz restarted', type: 'warning' },
                  { time: '14:30', event: 'Cluster health check completed', type: 'success' },
                  { time: '14:28', event: 'Resource optimization applied', type: 'info' },
                  { time: '14:25', event: 'Security scan completed', type: 'success' }
                ].map((event, index) => (
                  <div key={index} className="flex items-start space-x-3 p-2 hover:bg-gray-50 rounded">
                    <span className="text-xs text-gray-500 mt-1 w-12">{event.time}</span>
                    <span className="text-sm text-gray-700 flex-1">{event.event}</span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      event.type === 'success' ? 'bg-success-100 text-success-700' :
                      event.type === 'warning' ? 'bg-warning-100 text-warning-700' :
                      'bg-primary-100 text-primary-700'
                    }`}>
                      {event.type}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Chat Interface */}
          <div className="lg:col-span-1">
            <div className="card h-full flex flex-col">
              <div className="flex items-center space-x-2 mb-4 pb-4 border-b border-gray-200">
                <MessageSquare className="w-5 h-5 text-primary-600" />
                <h2 className="text-lg font-semibold text-gray-900">Chat with Infrastructure</h2>
              </div>
              
              {/* Messages */}
              <div className="flex-1 overflow-y-auto custom-scrollbar space-y-4 mb-4">
                {messages.map((msg) => (
                  <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      msg.type === 'user' 
                        ? 'bg-primary-600 text-white message-user' 
                        : 'bg-gray-100 text-gray-900 message-assistant'
                    }`}>
                      <p className="text-sm">{msg.content}</p>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Input */}
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Ask about your cluster..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <button
                  onClick={sendMessage}
                  className="btn-primary flex items-center space-x-1"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
