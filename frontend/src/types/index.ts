export interface PropertyRequest {
  address: string;
  property_type?: string;
  search_radius?: number;
  max_comparables?: number;
  square_footage?: number;
  bedrooms?: number;
  bathrooms?: number;
  year_built?: number;
  lot_size?: number;
}

export interface PropertyResponse {
  address: string;
  estimated_value: {
    low: number;
    high: number;
    most_likely: number;
  };
  comparables: Comparable[];
  analysis_date: string;
  confidence_score: number;
  property_id: number;
  analysis_id: number;
}

export interface Comparable {
  address: string;
  sale_price: number;
  sale_date: string;
  square_feet: number;
  bedrooms?: number;
  bathrooms?: number;
  year_built?: number;
  lot_size?: number;
  similarity_score: number;
  days_on_market?: number;
  adjustments: {
    size_adjustment?: number;
    bedroom_adjustment?: number;
    bathroom_adjustment?: number;
    age_adjustment?: number;
    total: number;
  };
  adjusted_price: number;
}

export interface CMAHistory {
  analysis_id: number;
  property_id: number;
  address?: string;
  estimated_value: number;
  confidence_score: number;
  analysis_date: string;
} 