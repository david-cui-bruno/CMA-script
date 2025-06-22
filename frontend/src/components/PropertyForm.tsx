import React, { useState } from 'react';
import { PropertyRequest } from '../types';

interface PropertyFormProps {
  onSubmit: (data: PropertyRequest) => void;
  loading: boolean;
}

const PropertyForm: React.FC<PropertyFormProps> = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState<PropertyRequest>({
    address: '',
    property_type: 'single_family',
    search_radius: 1.0,
    max_comparables: 6,
    square_footage: undefined,
    bedrooms: undefined,
    bathrooms: undefined,
    year_built: undefined,
    lot_size: undefined,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value === '' ? undefined : isNaN(Number(value)) ? value : Number(value),
    }));
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Property Information</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Address */}
        <div>
          <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
            Property Address *
          </label>
          <input
            type="text"
            id="address"
            name="address"
            required
            value={formData.address}
            onChange={handleChange}
            placeholder="123 Main Street, City, State ZIP"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Property Type */}
        <div>
          <label htmlFor="property_type" className="block text-sm font-medium text-gray-700 mb-2">
            Property Type
          </label>
          <select
            id="property_type"
            name="property_type"
            value={formData.property_type}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="single_family">Single Family</option>
            <option value="condo">Condominium</option>
            <option value="townhouse">Townhouse</option>
            <option value="multi_family">Multi-Family</option>
          </select>
        </div>

        {/* Property Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="square_footage" className="block text-sm font-medium text-gray-700 mb-2">
              Square Footage
            </label>
            <input
              type="number"
              id="square_footage"
              name="square_footage"
              value={formData.square_footage || ''}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="bedrooms" className="block text-sm font-medium text-gray-700 mb-2">
              Bedrooms
            </label>
            <input
              type="number"
              id="bedrooms"
              name="bedrooms"
              value={formData.bedrooms || ''}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="bathrooms" className="block text-sm font-medium text-gray-700 mb-2">
              Bathrooms
            </label>
            <input
              type="number"
              step="0.5"
              id="bathrooms"
              name="bathrooms"
              value={formData.bathrooms || ''}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="year_built" className="block text-sm font-medium text-gray-700 mb-2">
              Year Built
            </label>
            <input
              type="number"
              id="year_built"
              name="year_built"
              value={formData.year_built || ''}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="lot_size" className="block text-sm font-medium text-gray-700 mb-2">
              Lot Size (sq ft)
            </label>
            <input
              type="number"
              id="lot_size"
              name="lot_size"
              value={formData.lot_size || ''}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="search_radius" className="block text-sm font-medium text-gray-700 mb-2">
              Search Radius (miles)
            </label>
            <input
              type="number"
              step="0.1"
              id="search_radius"
              name="search_radius"
              value={formData.search_radius}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-md transition duration-200 flex items-center justify-center"
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analyzing...
            </>
          ) : (
            'Analyze Property'
          )}
        </button>
      </form>
    </div>
  );
};

export default PropertyForm; 