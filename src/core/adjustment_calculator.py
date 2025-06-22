"""
Calculate property adjustments for CMA analysis
"""
from models.database import Property, PropertySale
from typing import Dict
import math

class AdjustmentCalculator:
    def __init__(self):
        # Standard adjustment rates (can be customized by market)
        self.adjustment_rates = {
            "price_per_sqft_base": 150,  # Base $/sq ft for adjustments
            "bedroom_adjustment": 15000,  # $ per bedroom difference
            "bathroom_adjustment": 8000,  # $ per bathroom difference
            "age_adjustment_per_year": 500,  # $ per year age difference
            "garage_adjustment": 12000,  # $ per garage space
            "pool_adjustment": 25000,  # $ for pool
            "fireplace_adjustment": 5000,  # $ for fireplace
        }
    
    def calculate_adjustments(self, subject_property: Property, comparable_property: Property, comparable_sale: PropertySale) -> Dict:
        """
        Calculate all adjustments needed to make comparable similar to subject
        Returns dictionary with individual adjustments and total
        """
        adjustments = {}
        total_adjustment = 0
        
        # Size adjustment (most important)
        size_adj = self._calculate_size_adjustment(subject_property, comparable_property)
        if size_adj != 0:
            adjustments["size_adjustment"] = size_adj
            total_adjustment += size_adj
        
        # Bedroom adjustment
        bedroom_adj = self._calculate_bedroom_adjustment(subject_property, comparable_property)
        if bedroom_adj != 0:
            adjustments["bedroom_adjustment"] = bedroom_adj
            total_adjustment += bedroom_adj
        
        # Bathroom adjustment
        bathroom_adj = self._calculate_bathroom_adjustment(subject_property, comparable_property)
        if bathroom_adj != 0:
            adjustments["bathroom_adjustment"] = bathroom_adj
            total_adjustment += bathroom_adj
        
        # Age adjustment
        age_adj = self._calculate_age_adjustment(subject_property, comparable_property)
        if age_adj != 0:
            adjustments["age_adjustment"] = age_adj
            total_adjustment += age_adj
        
        # Lot size adjustment (if available)
        lot_adj = self._calculate_lot_size_adjustment(subject_property, comparable_property)
        if lot_adj != 0:
            adjustments["lot_size_adjustment"] = lot_adj
            total_adjustment += lot_adj
        
        # Market time adjustment (if sale was more than 90 days ago)
        time_adj = self._calculate_time_adjustment(comparable_sale)
        if time_adj != 0:
            adjustments["time_adjustment"] = time_adj
            total_adjustment += time_adj
        
        adjustments["total"] = int(total_adjustment)
        
        return adjustments
    
    def _calculate_size_adjustment(self, subject: Property, comparable: Property) -> float:
        """
        Calculate adjustment for square footage difference
        Positive = comparable needs to be adjusted UP to match subject
        """
        if not (subject.square_footage and comparable.square_footage):
            return 0
        
        size_difference = subject.square_footage - comparable.square_footage
        
        # Use price per square foot based on property size
        # Larger homes typically have lower $/sq ft, smaller homes higher
        if comparable.square_footage < 1500:
            price_per_sqft = self.adjustment_rates["price_per_sqft_base"] * 1.2
        elif comparable.square_footage > 3000:
            price_per_sqft = self.adjustment_rates["price_per_sqft_base"] * 0.8
        else:
            price_per_sqft = self.adjustment_rates["price_per_sqft_base"]
        
        return size_difference * price_per_sqft
    
    def _calculate_bedroom_adjustment(self, subject: Property, comparable: Property) -> float:
        """Calculate adjustment for bedroom count difference"""
        if not (subject.bedrooms and comparable.bedrooms):
            return 0
        
        bedroom_difference = subject.bedrooms - comparable.bedrooms
        return bedroom_difference * self.adjustment_rates["bedroom_adjustment"]
    
    def _calculate_bathroom_adjustment(self, subject: Property, comparable: Property) -> float:
        """Calculate adjustment for bathroom count difference"""
        if not (subject.bathrooms and comparable.bathrooms):
            return 0
        
        bathroom_difference = subject.bathrooms - comparable.bathrooms
        return bathroom_difference * self.adjustment_rates["bathroom_adjustment"]
    
    def _calculate_age_adjustment(self, subject: Property, comparable: Property) -> float:
        """
        Calculate adjustment for age difference
        Newer properties are typically worth more
        """
        if not (subject.year_built and comparable.year_built):
            return 0
        
        age_difference = subject.year_built - comparable.year_built
        
        # Cap the adjustment at 20 years to avoid extreme adjustments
        age_difference = max(-20, min(20, age_difference))
        
        return age_difference * self.adjustment_rates["age_adjustment_per_year"]
    
    def _calculate_lot_size_adjustment(self, subject: Property, comparable: Property) -> float:
        """Calculate adjustment for lot size difference"""
        if not (subject.lot_size and comparable.lot_size):
            return 0
        
        lot_difference = subject.lot_size - comparable.lot_size
        
        # Lot size adjustment: $5 per sq ft for first 5000 sq ft difference
        if abs(lot_difference) <= 5000:
            return lot_difference * 5
        else:
            # Diminishing returns for very large lot differences
            base_adjustment = 5000 * 5 * (1 if lot_difference > 0 else -1)
            remaining_difference = abs(lot_difference) - 5000
            additional_adjustment = remaining_difference * 2 * (1 if lot_difference > 0 else -1)
            return base_adjustment + additional_adjustment
    
    def _calculate_time_adjustment(self, comparable_sale: PropertySale) -> float:
        """
        Calculate adjustment for sale date (market time adjustment)
        Properties sold longer ago may need adjustment for market changes
        """
        from datetime import datetime, timedelta
        
        days_ago = (datetime.now() - comparable_sale.sale_date).days
        
        # No adjustment for sales within 90 days
        if days_ago <= 90:
            return 0
        
        # 1% appreciation per quarter (3 months) for older sales
        quarters_old = (days_ago - 90) / 90  # Quarters beyond the 90-day window
        appreciation_rate = 0.01 * quarters_old  # 1% per quarter
        
        # Cap at 2% total time adjustment to avoid excessive adjustments
        appreciation_rate = min(0.02, appreciation_rate)
        
        return float(comparable_sale.sale_price) * appreciation_rate
    
    def calculate_adjusted_price(self, comparable_sale_price: float, adjustments: Dict) -> float:
        """Calculate the final adjusted price"""
        return comparable_sale_price + adjustments.get("total", 0) 