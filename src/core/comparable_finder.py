"""
Find comparable properties for CMA analysis
"""
from sqlalchemy.orm import Session
from models.database import Property, PropertySale
from typing import List, Tuple
import math
from datetime import datetime, timedelta

class ComparableFinder:
    def __init__(self, db: Session):
        self.db = db
    
    def find_comparables(self, subject_property: Property, max_results: int = 6) -> List[Tuple[Property, PropertySale, float]]:
        """
        Find comparable properties and return them with similarity scores
        """
        # Get properties with recent sales (within 6 months)
        cutoff_date = datetime.now() - timedelta(days=180)
        
        # Query for properties with sales, excluding the subject property
        query = self.db.query(Property, PropertySale).join(PropertySale).filter(
            PropertySale.sale_date >= cutoff_date,
            PropertySale.sale_type == "sold",
            Property.id != subject_property.id if subject_property.id else True
        )
        
        potential_comps = query.all()
        
        # Score each potential comparable
        scored_comps = []
        for prop, sale in potential_comps:
            score = self._calculate_similarity_score(subject_property, prop)
            scored_comps.append((prop, sale, score))
        
        # Sort by similarity score (higher is better) and return top results
        scored_comps.sort(key=lambda x: x[2], reverse=True)
        return scored_comps[:max_results]
    
    def _calculate_similarity_score(self, subject: Property, comparable: Property) -> float:
        """
        Calculate similarity score between subject and comparable property
        Score ranges from 0-100, higher is more similar
        """
        score = 0.0
        
        # Size similarity (30% of total score)
        if subject.square_footage and comparable.square_footage:
            size_diff = abs(subject.square_footage - comparable.square_footage)
            max_size = max(subject.square_footage, comparable.square_footage)
            size_similarity = max(0, 1 - (size_diff / max_size))
            score += size_similarity * 30
        
        # Bedroom similarity (15% of total score)
        if subject.bedrooms and comparable.bedrooms:
            bedroom_diff = abs(subject.bedrooms - comparable.bedrooms)
            bedroom_similarity = max(0, 1 - (bedroom_diff / 5))  # Max 5 bedroom difference
            score += bedroom_similarity * 15
        
        # Bathroom similarity (15% of total score)
        if subject.bathrooms and comparable.bathrooms:
            bathroom_diff = abs(subject.bathrooms - comparable.bathrooms)
            bathroom_similarity = max(0, 1 - (bathroom_diff / 3))  # Max 3 bathroom difference
            score += bathroom_similarity * 15
        
        # Age similarity (20% of total score)
        if subject.year_built and comparable.year_built:
            age_diff = abs(subject.year_built - comparable.year_built)
            age_similarity = max(0, 1 - (age_diff / 50))  # Max 50 year difference
            score += age_similarity * 20
        
        # Geographic proximity (20% of total score)
        if (subject.latitude and subject.longitude and 
            comparable.latitude and comparable.longitude):
            distance = self._calculate_distance(
                subject.latitude, subject.longitude,
                comparable.latitude, comparable.longitude
            )
            # Score decreases with distance (max 10 miles)
            distance_similarity = max(0, 1 - (distance / 10))
            score += distance_similarity * 20
        
        return score
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points in miles using Haversine formula
        """
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in miles
        r = 3956
        
        return c * r 