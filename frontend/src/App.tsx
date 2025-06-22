import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import AuthWrapper from './components/auth/AuthWrapper';
import PropertyForm from './components/PropertyForm';
import ResultsDisplay from './components/ResultsDisplay';
import UserProfile from './components/UserProfile';
import CMAHistoryComponent from './components/CMAHistory';
import { cmaApi } from './services/api';
import { PropertyRequest, PropertyResponse } from './types';

const AppContent: React.FC = () => {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [results, setResults] = useState<PropertyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [downloadingPDF, setDownloadingPDF] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'analyze' | 'history'>('analyze');

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthWrapper />;
  }

  const handleAnalyze = async (data: PropertyRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await cmaApi.analyzeCMA(data);
      setResults(response);
      setActiveTab('analyze'); // Stay on analyze tab to show results
    } catch (err) {
      setError('Failed to analyze property. Please check your connection and try again.');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async (analysisId: number) => {
    setDownloadingPDF(true);
    
    try {
      const blob = await cmaApi.downloadPDFReport(analysisId);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `CMA-Report-${analysisId}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download PDF report. Please try again.');
      console.error('PDF download error:', err);
    } finally {
      setDownloadingPDF(false);
    }
  };

  const handleNewAnalysis = () => {
    setResults(null);
    setError(null);
    setActiveTab('analyze');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">CMA Analysis Tool</h1>
              <p className="text-gray-600">Professional Comparative Market Analysis</p>
            </div>
            <UserProfile />
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('analyze')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'analyze'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              New Analysis
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'history'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              CMA History
            </button>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analyze' && (
          <>
            {!results ? (
              <PropertyForm onSubmit={handleAnalyze} loading={loading} />
            ) : (
              <div>
                <div className="mb-6">
                  <button
                    onClick={handleNewAnalysis}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition duration-200"
                  >
                    New Analysis
                  </button>
                </div>
                <ResultsDisplay 
                  data={results} 
                  onDownloadPDF={handleDownloadPDF}
                  downloadingPDF={downloadingPDF}
                />
              </div>
            )}
          </>
        )}

        {activeTab === 'history' && (
          <CMAHistoryComponent />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-500 text-sm">
            CMA Analysis Tool - Professional Real Estate Valuation
          </p>
        </div>
      </footer>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
