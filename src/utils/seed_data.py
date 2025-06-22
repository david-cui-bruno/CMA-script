"""
Seed the database with sample property data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from models.database import Property, PropertySale
from data.database import SessionLocal
from datetime import datetime, timedelta
from decimal import Decimal
import random

def create_sample_properties():
    """Create sample properties for testing CMA analysis"""
    db = SessionLocal()
    
    try:
        # Sample properties in different areas
        sample_properties = [
            # Beverly Hills area
            {
                "address": "123 Beverly Drive, Beverly Hills, CA 90210",
                "latitude": 34.0736, "longitude": -118.4004,
                "square_footage": 2400, "bedrooms": 4, "bathrooms": 3.0,
                "year_built": 2015, "property_type": "single_family", "lot_size": 8000,
                "sale_price": 1200000, "sale_date": datetime.now() - timedelta(days=45)
            },
            {
                "address": "456 Rodeo Avenue, Beverly Hills, CA 90210", 
                "latitude": 34.0697, "longitude": -118.4015,
                "square_footage": 2200, "bedrooms": 3, "bathrooms": 2.5,
                "year_built": 2018, "property_type": "single_family", "lot_size": 7500,
                "sale_price": 1150000, "sale_date": datetime.now() - timedelta(days=62)
            },
            {
                "address": "789 Canon Street, Beverly Hills, CA 90210",
                "latitude": 34.0728, "longitude": -118.3987,
                "square_footage": 2600, "bedrooms": 4, "bathrooms": 3.5,
                "year_built": 2012, "property_type": "single_family", "lot_size": 9000,
                "sale_price": 1350000, "sale_date": datetime.now() - timedelta(days=30)
            },
            # West Hollywood area
            {
                "address": "111 Sunset Plaza Drive, West Hollywood, CA 90069",
                "latitude": 34.0928, "longitude": -118.3774,
                "square_footage": 2100, "bedrooms": 3, "bathrooms": 2.0,
                "year_built": 2020, "property_type": "single_family", "lot_size": 6500,
                "sale_price": 980000, "sale_date": datetime.now() - timedelta(days=55)
            },
            {
                "address": "222 Laurel Canyon Blvd, West Hollywood, CA 90069",
                "latitude": 34.0945, "longitude": -118.3788,
                "square_footage": 2300, "bedrooms": 3, "bathrooms": 2.5,
                "year_built": 2017, "property_type": "single_family", "lot_size": 7000,
                "sale_price": 1050000, "sale_date": datetime.now() - timedelta(days=38)
            },
            # Hollywood area
            {
                "address": "333 Hollywood Boulevard, Hollywood, CA 90028",
                "latitude": 34.1022, "longitude": -118.3267,
                "square_footage": 1900, "bedrooms": 3, "bathrooms": 2.0,
                "year_built": 2010, "property_type": "single_family", "lot_size": 6000,
                "sale_price": 850000, "sale_date": datetime.now() - timedelta(days=72)
            },
            {
                "address": "444 Vine Street, Hollywood, CA 90028",
                "latitude": 34.1016, "longitude": -118.3259,
                "square_footage": 2500, "bedrooms": 4, "bathrooms": 3.0,
                "year_built": 2016, "property_type": "single_family", "lot_size": 8500,
                "sale_price": 1100000, "sale_date": datetime.now() - timedelta(days=41)
            },
        ]
        
        for prop_data in sample_properties:
            # Create property
            property_record = Property(
                address=prop_data["address"],
                latitude=prop_data["latitude"],
                longitude=prop_data["longitude"],
                square_footage=prop_data["square_footage"],
                bedrooms=prop_data["bedrooms"],
                bathrooms=prop_data["bathrooms"],
                year_built=prop_data["year_built"],
                property_type=prop_data["property_type"],
                lot_size=prop_data["lot_size"]
            )
            
            db.add(property_record)
            db.flush()  # Get the ID
            
            # Create sale record
            sale_record = PropertySale(
                property_id=property_record.id,
                sale_price=prop_data["sale_price"],
                sale_date=prop_data["sale_date"],
                list_price=prop_data["sale_price"] * 1.05,  # Listed 5% higher
                days_on_market=random.randint(20, 90),
                sale_type="sold"
            )
            
            db.add(sale_record)
        
        db.commit()
        print(f"✅ Created {len(sample_properties)} sample properties with sales data")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating sample properties: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_properties() 