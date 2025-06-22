import React, { useState, useEffect } from 'react';
import { cmaApi } from '../services/api';
import { CMAHistory } from '../types';

interface CMAHistoryProps {
  onSelectAnalysis?: (analysisId: number) => void;
}

const CMAHistoryComponent: React.FC<CMAHistoryProps> = ({ onSelectAnalysis }) => {
  const [history, setHistory] = useState<CMAHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const data = await cmaApi.getCMAHistory();
      setHistory(data);
    } catch (err) {
      setError('Failed to load CMA history');
      console.error('Error fetching history:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-red-600 text-center">{error}</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Recent CMA Reports</h3>
      </div>
      
      {history.length === 0 ? (
        <div className="p-6 text-center text-gray-500">
          No CMA analyses yet. Create your first analysis above!
        </div>
      ) : (
        <div className="divide-y divide-gray-200">
          {history.map((analysis) => (
            <div key={analysis.analysis_id} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-gray-900 truncate">
                    {analysis.address || `Property Analysis #${analysis.analysis_id}`}
                  </h4>
                  <p className="text-sm text-gray-500 mt-1">
                    Estimated Value: {formatCurrency(analysis.estimated_value)}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    {formatDate(analysis.analysis_date)} • {Math.round(analysis.confidence_score * 100)}% confidence
                  </p>
                </div>
                
                <div className="flex space-x-2">
                  {onSelectAnalysis && (
                    <button
                      onClick={() => onSelectAnalysis(analysis.analysis_id)}
                      className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                    >
                      View
                    </button>
                  )}
                  <button
                    onClick={async () => {
                      try {
                        const blob = await cmaApi.downloadPDFReport(analysis.analysis_id);
                        const url = window.URL.createObjectURL(blob);
                        const link = document.createElement('a');
                        link.href = url;
                        link.download = `CMA-Report-${analysis.analysis_id}.pdf`;
                        document.body.appendChild(link);
                        link.click();
                        link.remove();
                        window.URL.revokeObjectURL(url);
                      } catch (err) {
                        console.error('Failed to download PDF:', err);
                      }
                    }}
                    className="text-green-600 hover:text-green-700 text-sm font-medium"
                  >
                    Download
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CMAHistoryComponent; 