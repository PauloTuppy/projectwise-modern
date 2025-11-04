import React, { useEffect, useState } from 'react';
import axios from 'axios';

// TypeScript Interfaces
interface KPI {
  kpi_id: string;
  value: number;
  target: number;
  threshold_warning: number;
  threshold_critical: number;
  status: 'OK' | 'WARNING' | 'CRITICAL';
  variance: number;
  unit: string;
}

interface DashboardData {
  timestamp: string;
  documents: {
    total: number;
    analyzed: number;
    pending: number;
  };
  rfis: {
    total: number;
    open: number;
    overdue: number;
    closed: number;
  };
  transmittals: {
    total: number;
    pending: number;
    approved: number;
  };
  kpis: {
    ok: number;
    warning: number;
    critical: number;
  };
}

interface Alert {
  id: string;
  kpi_id: string;
  type: string;
  message: string;
  created_at: string;
  acknowledged: boolean;
}

interface HistoricalDataPoint {
  date: string;
  avg: number;
  max: number;
  min: number;
}

interface DashboardProps {
  projectId: string;
}

export const Dashboard: React.FC<DashboardProps> = ({ projectId }) => {
  // State
  const [kpis, setKpis] = useState<Record<string, KPI>>({});
  const [summary, setSummary] = useState<DashboardData | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedKpi, setSelectedKpi] = useState<string>('KPI-001');
  const [kpiHistory, setKpiHistory] = useState<HistoricalDataPoint[]>([]);

  // Fetch dashboard data
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, [projectId]);

  // Fetch KPI history when selected KPI changes
  useEffect(() => {
    if (selectedKpi) {
      fetchKpiHistory();
    }
  }, [selectedKpi, projectId]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [kpiResponse, summaryResponse, alertsResponse] = await Promise.all([
        axios.get(`/api/v1/projects/${projectId}/dashboard/kpis`),
        axios.get(`/api/v1/projects/${projectId}/dashboard/summary`),
        axios.get(`/api/v1/projects/${projectId}/dashboard/alerts?acknowledged=false`)
      ]);

      setKpis(kpiResponse.data);
      setSummary(summaryResponse.data);
      setAlerts(alertsResponse.data.alerts || []);
    } catch (err: any) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data. Retrying...');
      
      // Retry after 5 seconds
      setTimeout(fetchDashboardData, 5000);
    } finally {
      setLoading(false);
    }
  };

  const fetchKpiHistory = async () => {
    try {
      const response = await axios.get(
        `/api/v1/projects/${projectId}/dashboard/kpi/${selectedKpi}/history?days=7`
      );
      setKpiHistory(response.data.data || []);
    } catch (err) {
      console.error('Error fetching KPI history:', err);
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      await axios.post(
        `/api/v1/projects/${projectId}/dashboard/alerts/${alertId}/acknowledge`
      );
      
      // Remove alert from list
      setAlerts(alerts.filter(a => a.id !== alertId));
    } catch (err) {
      console.error('Error acknowledging alert:', err);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'OK': 'bg-green-100 border-green-500',
      'WARNING': 'bg-yellow-100 border-yellow-500',
      'CRITICAL': 'bg-red-100 border-red-500'
    };
    return colors[status] || 'bg-gray-100 border-gray-500';
  };

  const getStatusBgColor = (status: string) => {
    const colors: Record<string, string> = {
      'OK': 'bg-green-500',
      'WARNING': 'bg-yellow-500',
      'CRITICAL': 'bg-red-500'
    };
    return colors[status] || 'bg-gray-500';
  };

  const getKpiName = (kpiId: string): string => {
    const names: Record<string, string> = {
      'KPI-001': 'Upload Success Rate',
      'KPI-002': 'AI Analysis Time',
      'KPI-003': 'AI Accuracy',
      'KPI-004': 'RFI Response Time',
      'KPI-005': 'RFI Closure Rate',
      'KPI-006': 'Transmittal Approval',
      'KPI-007': 'On-time Completion'
    };
    return names[kpiId] || kpiId;
  };

  if (loading && !summary) {
    return (
      <div className="p-6 text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Dashboard</h1>
          <div className="flex items-center gap-4 mt-2">
            <p className="text-gray-600">
              Last updated: {summary ? new Date(summary.timestamp).toLocaleString() : 'N/A'}
            </p>
            {error && (
              <div className="text-sm text-red-600 bg-red-50 px-3 py-1 rounded">
                {error}
              </div>
            )}
          </div>
        </div>

        {/* KPI Status Summary */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-green-500 text-white p-6 rounded-lg shadow">
            <p className="text-sm font-semibold opacity-90">ON TARGET</p>
            <p className="text-3xl font-bold">{summary?.kpis.ok || 0}</p>
          </div>
          <div className="bg-yellow-500 text-white p-6 rounded-lg shadow">
            <p className="text-sm font-semibold opacity-90">WARNING</p>
            <p className="text-3xl font-bold">{summary?.kpis.warning || 0}</p>
          </div>
          <div className="bg-red-500 text-white p-6 rounded-lg shadow">
            <p className="text-sm font-semibold opacity-90">CRITICAL</p>
            <p className="text-3xl font-bold">{summary?.kpis.critical || 0}</p>
          </div>
        </div>

        {/* Main Metrics */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {/* Documents */}
          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
            <p className="text-gray-600 text-sm font-semibold">Documents</p>
            <p className="text-2xl font-bold text-gray-900">{summary?.documents.total || 0}</p>
            <div className="mt-2 text-xs text-gray-600">
              <p>✓ Analyzed: {summary?.documents.analyzed || 0}</p>
              <p>⏳ Pending: {summary?.documents.pending || 0}</p>
            </div>
          </div>

          {/* RFIs */}
          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-orange-500">
            <p className="text-gray-600 text-sm font-semibold">RFIs</p>
            <p className="text-2xl font-bold text-gray-900">{summary?.rfis.total || 0}</p>
            <div className="mt-2 text-xs text-gray-600">
              <p>📖 Open: {summary?.rfis.open || 0}</p>
              <p>⚠️ Overdue: {summary?.rfis.overdue || 0}</p>
            </div>
          </div>

          {/* Transmittals */}
          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-purple-500">
            <p className="text-gray-600 text-sm font-semibold">Transmittals</p>
            <p className="text-2xl font-bold text-gray-900">{summary?.transmittals.total || 0}</p>
            <div className="mt-2 text-xs text-gray-600">
              <p>⏳ Pending: {summary?.transmittals.pending || 0}</p>
              <p>✓ Approved: {summary?.transmittals.approved || 0}</p>
            </div>
          </div>

          {/* Alerts */}
          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-red-500">
            <p className="text-gray-600 text-sm font-semibold">Alerts</p>
            <p className="text-2xl font-bold text-red-600">{alerts.length}</p>
            <div className="mt-2">
              <button 
                className="text-xs text-blue-600 hover:underline"
                onClick={() => document.getElementById('alerts-section')?.scrollIntoView({ behavior: 'smooth' })}
              >
                View all →
              </button>
            </div>
          </div>
        </div>

        {/* KPI Cards Grid */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          {Object.entries(kpis).map(([kpiId, kpi]) => (
            <div
              key={kpiId}
              className={`bg-white p-6 rounded-lg shadow border-l-4 cursor-pointer hover:shadow-lg transition ${getStatusColor(kpi.status)}`}
              onClick={() => setSelectedKpi(kpiId)}
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <p className="text-gray-600 text-sm font-semibold">{kpiId}</p>
                  <p className="text-xs text-gray-500">{getKpiName(kpiId)}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {kpi.value}
                    <span className="text-sm text-gray-500 ml-1">{kpi.unit}</span>
                  </p>
                </div>
                <div className={`${getStatusBgColor(kpi.status)} text-white px-3 py-1 rounded text-xs font-bold`}>
                  {kpi.status}
                </div>
              </div>
              
              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                <div
                  className={`h-2 rounded-full ${getStatusBgColor(kpi.status)}`}
                  style={{ width: `${Math.min((kpi.value / kpi.target) * 100, 100)}%` }}
                ></div>
              </div>
              
              <div className="space-y-1 text-xs text-gray-600">
                <p>🎯 Target: {kpi.target} {kpi.unit}</p>
                <p className={kpi.variance >= 0 ? 'text-green-600' : 'text-red-600'}>
                  Variance: {kpi.variance > 0 ? '+' : ''}{kpi.variance}%
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* KPI History Chart */}
        {kpiHistory.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow mb-8">
            <h2 className="text-xl font-bold mb-4">
              {selectedKpi} - {getKpiName(selectedKpi)} (7 Day Trend)
            </h2>
            <div className="h-64 flex items-end justify-between gap-2">
              {kpiHistory.map((point, idx) => {
                const maxValue = Math.max(...kpiHistory.map(p => p.max));
                const height = (point.avg / maxValue) * 100;
                
                return (
                  <div key={idx} className="flex-1 flex flex-col items-center">
                    <div className="w-full bg-blue-200 rounded-t relative group" style={{ height: `${height}%` }}>
                      <div className="absolute bottom-full mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded py-1 px-2 whitespace-nowrap">
                        Avg: {point.avg.toFixed(1)}<br/>
                        Max: {point.max.toFixed(1)}<br/>
                        Min: {point.min.toFixed(1)}
                      </div>
                    </div>
                    <p className="text-xs text-gray-600 mt-2 transform -rotate-45 origin-top-left">
                      {new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Alerts Section */}
        {alerts.length > 0 && (
          <div id="alerts-section" className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">⚠️ Active Alerts ({alerts.length})</h2>
            <div className="space-y-3">
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-4 rounded border-l-4 ${
                    alert.type === 'critical' ? 'bg-red-50 border-red-500' :
                    alert.type === 'warning' ? 'bg-yellow-50 border-yellow-500' :
                    'bg-blue-50 border-blue-500'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <p className="font-semibold text-gray-900">{alert.kpi_id}</p>
                      <p className="text-sm text-gray-700 mt-1">{alert.message}</p>
                      <p className="text-xs text-gray-500 mt-2">
                        {new Date(alert.created_at).toLocaleString()}
                      </p>
                    </div>
                    <button
                      onClick={() => acknowledgeAlert(alert.id)}
                      className="ml-4 px-3 py-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-700 transition"
                    >
                      Acknowledge
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-bold text-blue-800 mb-2">📊 Dashboard Features</h4>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Auto-refreshes every 30 seconds</li>
            <li>• Click on KPI cards to view 7-day trends</li>
            <li>• Acknowledge alerts to remove them from the list</li>
            <li>• Green = On Target, Yellow = Warning, Red = Critical</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
