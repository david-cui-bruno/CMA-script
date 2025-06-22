import React from 'react';
import { PropertyResponse } from '../types';

interface ResultsDisplayProps {
  data: PropertyResponse;
  onDownloadPDF: (analysisId: number) => void;
  downloadingPDF: boolean;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ data, onDownloadPDF, downloadingPDF }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600 bg-green-100';
    if (score >= 0.8) return 'text-blue-600 bg-blue-100';
    if (score >= 0.7) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getSimilarityColor = (score: number) => {
    if (score >= 95) return 'text-green-600';
    if (score >= 90) return 'text-blue-600';
    if (score >= 85) return 'text-yellow-600';
    return 'text-orange-600';
  };

  return (
    <div className="space-y-6">
      {/* Header with Download Button */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Comparative Market Analysis</h2>
            <p className="text-gray-600 mt-1">{data.address}</p>
            <p className="text-sm text-gray-500">Analysis Date: {formatDate(data.analysis_date)}</p>
          </div>
          <button
            onClick={() => onDownloadPDF(data.analysis_id)}
            disabled={downloadingPDF}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md transition duration-200 flex items-center"
          >
            {downloadingPDF ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Generating...
              </>
            ) : (
              <>
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download Report
              </>
            )}
          </button>
        </div>

        {/* Estimated Value Section */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Estimated Market Value</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-sm text-gray-600">Low Estimate</p>
              <p className="text-2xl font-bold text-gray-800">{formatCurrency(data.estimated_value.low)}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Most Likely</p>
              <p className="text-3xl font-bold text-blue-600">{formatCurrency(data.estimated_value.most_likely)}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">High Estimate</p>
              <p className="text-2xl font-bold text-gray-800">{formatCurrency(data.estimated_value.high)}</p>
            </div>
          </div>
          
          <div className="mt-4 flex items-center justify-center">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(data.confidence_score)}`}>
              {formatPercentage(data.confidence_score * 100)} Confidence
            </span>
          </div>
        </div>
      </div>

      {/* Comparable Properties */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">Comparable Properties</h3>
        
        <div className="space-y-4">
          {data.comparables.map((comp, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h4 className="font-semibold text-gray-900">{comp.address}</h4>
                  <p className="text-sm text-gray-600">Sold: {formatDate(comp.sale_date)}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-gray-900">{formatCurrency(comp.sale_price)}</p>
                  <p className={`text-sm font-medium ${getSimilarityColor(comp.similarity_score)}`}>
                    {formatPercentage(comp.similarity_score)} Match
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                <div>
                  <p className="text-xs text-gray-500">Square Feet</p>
                  <p className="font-medium">{comp.square_feet?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Bed/Bath</p>
                  <p className="font-medium">{comp.bedrooms}/{comp.bathrooms}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Year Built</p>
                  <p className="font-medium">{comp.year_built}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Days on Market</p>
                  <p className="font-medium">{comp.days_on_market || 'N/A'}</p>
                </div>
              </div>

              {/* Adjustments */}
              {comp.adjustments.total !== 0 && (
                <div className="bg-gray-50 rounded p-3 mt-3">
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Price Adjustments</h5>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                    {comp.adjustments.size_adjustment && (
                      <div>
                        <span className="text-gray-500">Size: </span>
                        <span className={comp.adjustments.size_adjustment > 0 ? 'text-green-600' : 'text-red-600'}>
                          {comp.adjustments.size_adjustment > 0 ? '+' : ''}{formatCurrency(comp.adjustments.size_adjustment)}
                        </span>
                      </div>
                    )}
                    {comp.adjustments.bedroom_adjustment && (
                      <div>
                        <span className="text-gray-500">Bedrooms: </span>
                        <span className={comp.adjustments.bedroom_adjustment > 0 ? 'text-green-600' : 'text-red-600'}>
                          {comp.adjustments.bedroom_adjustment > 0 ? '+' : ''}{formatCurrency(comp.adjustments.bedroom_adjustment)}
                        </span>
                      </div>
                    )}
                    {comp.adjustments.bathroom_adjustment && (
                      <div>
                        <span className="text-gray-500">Bathrooms: </span>
                        <span className={comp.adjustments.bathroom_adjustment > 0 ? 'text-green-600' : 'text-red-600'}>
                          {comp.adjustments.bathroom_adjustment > 0 ? '+' : ''}{formatCurrency(comp.adjustments.bathroom_adjustment)}
                        </span>
                      </div>
                    )}
                    {comp.adjustments.age_adjustment && (
                      <div>
                        <span className="text-gray-500">Age: </span>
                        <span className={comp.adjustments.age_adjustment > 0 ? 'text-green-600' : 'text-red-600'}>
                          {comp.adjustments.age_adjustment > 0 ? '+' : ''}{formatCurrency(comp.adjustments.age_adjustment)}
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <div className="mt-2 pt-2 border-t border-gray-200 flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700">Adjusted Price:</span>
                    <span className="text-lg font-bold text-gray-900">{formatCurrency(comp.adjusted_price)}</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Analysis Summary */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Analysis Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-sm text-gray-600">Total Comparables</p>
            <p className="text-2xl font-bold text-gray-900">{data.comparables.length}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Average Sale Price</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency(data.comparables.reduce((sum, comp) => sum + comp.sale_price, 0) / data.comparables.length)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Price Per Sq Ft</p>
            <p className="text-2xl font-bold text-gray-900">
              ${Math.round(data.estimated_value.most_likely / (data.comparables[0]?.square_feet || 2300))}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsDisplay; 