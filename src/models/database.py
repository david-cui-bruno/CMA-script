"""
Database models for CMA Analysis
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    properties = relationship("Property", back_populates="owner")
    cma_analyses = relationship("CMAAnalysis", back_populates="user")

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(255), nullable=False, index=True)
    property_type = Column(String(50), default="single_family")
    square_footage = Column(Integer)
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    year_built = Column(Integer)
    lot_size = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign key to user
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for seed data
    
    # Relationships
    owner = relationship("User", back_populates="properties")
    sales = relationship("PropertySale", back_populates="property")

class PropertySale(Base):
    __tablename__ = "property_sales"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    sale_price = Column(Numeric(12, 2), nullable=False)
    sale_date = Column(DateTime, nullable=False)
    days_on_market = Column(Integer)
    sale_type = Column(String(50), default="standard")
    
    # Relationships
    property = relationship("Property", back_populates="sales")

class PropertyFeatures(Base):
    __tablename__ = "property_features"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    feature_name = Column(String(100), nullable=False)
    feature_value = Column(String(255))
    
    # Relationships
    property = relationship("Property")

class CMAAnalysis(Base):
    __tablename__ = "cma_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # New: link to user
    
    estimated_value_low = Column(Numeric(12, 2), nullable=False)
    estimated_value_high = Column(Numeric(12, 2), nullable=False)
    estimated_value_most_likely = Column(Numeric(12, 2), nullable=False)
    confidence_score = Column(Float, nullable=False)
    comparable_count = Column(Integer, default=0)
    
    analysis_date = Column(DateTime, default=datetime.utcnow)
    analysis_data = Column(Text)  # JSON data for detailed results
    
    # Relationships
    subject_property = relationship("Property")
    user = relationship("User", back_populates="cma_analyses") 