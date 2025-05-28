import React, { useState, useEffect } from 'react';
import Head from 'next/head';

interface WorkflowMetrics {
  workflows: {
    total: number;
    running: number;
    completed: number;
    failed: number;
  };
  components: {
    total: number;
    generated: number;
    updated: number;
  };
  performance: {
    avgWorkflowTime: number;
    successRate: number;
    lastUpdated: string;
  };
}

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  metadata?: any;
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<WorkflowMetrics>({
    workflows: { total: 0, running: 0, completed: 0, failed: 0 },
    components: { total: 0, generated: 0, updated: 0 },
    performance: { avgWorkflowTime: 0, successRate: 0, lastUpdated: '' },
  });

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [wsStatus, setWsStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');

  useEffect(() => {
    // WebSocket 연결
    let ws: WebSocket | null = null;
    
    const connectWebSocket = () => {
      ws = new WebSocket('ws://localhost:3001');
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setWsStatus('connected');
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
          case 'initial-metrics':
            setMetrics(data.data);
            break;
            
          case 'workflow-metrics':
            setMetrics(prev => ({
              ...prev,
              workflows: data.data
            }));
            break;
            
          case 'component-metrics':
            setMetrics(prev => ({
              ...prev,
              components: data.data
            }));
            break;
            
          case 'notification':
            setNotifications(prev => [data.data, ...prev].slice(0, 20));
            break;
        }
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setWsStatus('disconnected');
        // 재연결 시도
        setTimeout(connectWebSocket, 5000);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    };
    
    connectWebSocket();
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const getStatusColor = (type: string) => {
    switch (type) {
      case 'success': return 'text-green-600 bg-green-100';
      case 'error': return 'text-red-600 bg-red-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-blue-600 bg-blue-100';
    }
  };

  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    return `${(seconds / 60).toFixed(1)}m`;
  };

  return (
    <>
      <Head>
        <title>MCP Automation Dashboard</title>
        <meta name="description" content="Real-time monitoring for Figma to Code automation" />
      </Head>

      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              🎯 MCP Automation Dashboard
            </h1>
            <p className="text-gray-600">Real-time monitoring for Figma to Code automation</p>
            
            {/* WebSocket Status */}
            <div className="mt-4 flex items-center">
              <div className={`w-3 h-3 rounded-full mr-2 ${
                wsStatus === 'connected' ? 'bg-green-500' : 
                wsStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' : 
                'bg-red-500'
              }`} />
              <span className="text-sm text-gray-600">
                {wsStatus === 'connected' ? 'Connected' : 
                 wsStatus === 'connecting' ? 'Connecting...' : 
                 'Disconnected'}
              </span>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Workflow Metrics */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-700 mb-4">
                📊 Workflow Metrics
              </h2>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total</span>
                  <span className="font-semibold">{metrics.workflows.total}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Running</span>
                  <span className="font-semibold text-blue-600">
                    {metrics.workflows.running}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Completed</span>
                  <span className="font-semibold text-green-600">
                    {metrics.workflows.completed}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Failed</span>
                  <span className="font-semibold text-red-600">
                    {metrics.workflows.failed}
                  </span>
                </div>
              </div>
            </div>

            {/* Component Metrics */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-700 mb-4">
                🎨 Component Metrics
              </h2>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total</span>
                  <span className="font-semibold">{metrics.components.total}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Generated</span>
                  <span className="font-semibold text-blue-600">
                    {metrics.components.generated}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Updated</span>
                  <span className="font-semibold text-yellow-600">
                    {metrics.components.updated}
                  </span>
                </div>
              </div>
            </div>

            {/* Performance Metrics */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-700 mb-4">
                ⚡ Performance
              </h2>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg Time</span>
                  <span className="font-semibold">
                    {formatTime(metrics.performance.avgWorkflowTime)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Success Rate</span>
                  <span className="font-semibold text-green-600">
                    {metrics.performance.successRate.toFixed(1)}%
                  </span>
                </div>
                <div className="text-xs text-gray-500 mt-4">
                  Last updated: {metrics.performance.lastUpdated 
                    ? new Date(metrics.performance.lastUpdated).toLocaleString()
                    : 'N/A'}
                </div>
              </div>
            </div>
          </div>

          {/* Notifications */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-700">
                📱 Recent Notifications
              </h2>
            </div>
            
            <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  No notifications yet
                </div>
              ) : (
                notifications.map((notification) => (
                  <div key={notification.id} className="p-4 hover:bg-gray-50">
                    <div className="flex items-start">
                      <div className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(notification.type)}`}>
                        {notification.type.toUpperCase()}
                      </div>
                      <div className="ml-3 flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          {notification.title}
                        </p>
                        <p className="text-sm text-gray-600 mt-1">
                          {notification.message}
                        </p>
                        <p className="text-xs text-gray-500 mt-2">
                          {new Date(notification.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}