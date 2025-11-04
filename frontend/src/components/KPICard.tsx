import React from 'react';

interface KPICardProps {
  kpiId: string;
  value: number;
  target: number;
  unit: string;
  status: 'OK' | 'WARNING' | 'CRITICAL';
  variance: number;
  onClick?: () => void;
}

export const KPICard: React.FC<KPICardProps> = ({
  kpiId,
  value,
  target,
  unit,
  status,
  variance,
  onClick
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'OK':
        return 'bg-green-50 border-green-500 text-green-700';
      case 'WARNING':
        return 'bg-yellow-50 border-yellow-500 text-yellow-700';
      case 'CRITICAL':
        return 'bg-red-50 border-red-500 text-red-700';
      default:
        return 'bg-gray-50 border-gray-500 text-gray-700';
    }
  };

  const getProgressBarColor = (status: string) => {
    switch (status) {
      case 'OK':
        return 'bg-green-500';
      case 'WARNING':
        return 'bg-yellow-500';
      case 'CRITICAL':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const progress = Math.min((value / target) * 100, 100);

  return (
    <div
      className={`bg-white p-4 rounded-lg shadow border-l-4 cursor-pointer hover:shadow-lg transition ${getStatusColor(status)}`}
      onClick={onClick}
    >
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-bold text-gray-700">{kpiId}</span>
        <span className={`text-xs font-bold px-2 py-1 rounded ${getProgressBarColor(status)} text-white`}>
          {status}
        </span>
      </div>
      <div className="flex items-baseline gap-1 mb-2">
        <span className="text-3xl font-bold text-gray-900">{value}</span>
        <span className="text-sm text-gray-600">/ {target} {unit}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
        <div
          className={`h-2 rounded-full ${getProgressBarColor(status)}`}
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <div className="flex justify-between items-center text-xs text-gray-600">
        <span>Variance: {variance > 0 ? '+' : ''}{variance}%</span>
        <span>Progress: {Math.round(progress)}%</span>
      </div>
    </div>
  );
};
