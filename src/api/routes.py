"""
API Routes for CMA Analysis
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from data.database import get_db
from data.property_service import PropertyService
from models.database import Property, User
from reports.pdf_generator import CMAReportGenerator
from core.auth import get_current_user
import io

router = APIRouter()

class PropertyRequest(BaseModel):
    address: str
    property_type: Optional[str] = "single_family"
    search_radius: float = 1.0
    max_comparables: int = 6
    # Optional property details
    square_footage: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    year_built: Optional[int] = None
    lot_size: Optional[int] = None
    # Add location for better comparable search
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PropertyResponse(BaseModel):
    address: str
    estimated_value: dict
    comparables: List[dict]
    analysis_date: datetime
    confidence_score: float
    property_id: int
    analysis_id: int

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@router.post("/cma/analyze", response_model=PropertyResponse)
async def analyze_property(
    request: PropertyRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform CMA analysis for a property (requires authentication)
    """
    try:
        print(f"🔍 Starting CMA analysis for user: {current_user.email}")
        print(f"🔍 Property address: {request.address}")
        
        property_service = PropertyService(db)
        
        # Check if property exists, if not create it and link to user
        print("🔍 Looking for existing property...")
        property_record = property_service.get_property_by_address(request.address)
        
        if not property_record:
            print("🔍 Creating new property...")
            property_record = property_service.create_property(
                address=request.address,
                property_type=request.property_type,
                square_footage=request.square_footage,
                bedrooms=request.bedrooms,
                bathrooms=request.bathrooms,
                year_built=request.year_built,
                lot_size=request.lot_size,
                latitude=request.latitude,
                longitude=request.longitude,
                owner_id=current_user.id
            )
            print(f"✅ Created property with ID: {property_record.id}")
        else:
            print(f"✅ Found existing property with ID: {property_record.id}")
        
        # Perform CMA analysis with real comparables
        print("🔍 Performing CMA analysis...")
        analysis_results = property_service.perform_cma_analysis(property_record)
        print(f"✅ CMA analysis complete. Found {len(analysis_results['comparables'])} comparables")
        
        # Save analysis to database with user link
        print("🔍 Saving CMA analysis...")
        cma_record = property_service.save_cma_analysis(
            property_record.id, 
            analysis_results,
            user_id=current_user.id
        )
        print(f"✅ Saved CMA analysis with ID: {cma_record.id}")
        
        return PropertyResponse(
            address=request.address,
            estimated_value=analysis_results["estimated_value"],
            comparables=analysis_results["comparables"],
            analysis_date=cma_record.analysis_date,
            confidence_score=analysis_results["confidence_score"],
            property_id=property_record.id,
            analysis_id=cma_record.id
        )
        
    except Exception as e:
        print(f"❌ CMA Analysis Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/cma/report/pdf")
async def generate_pdf_report(request: PropertyRequest, db: Session = Depends(get_db)):
    """
    Generate a professional PDF report for CMA analysis
    """
    try:
        property_service = PropertyService(db)
        
        # Get or create property
        property_record = property_service.get_property_by_address(request.address)
        if not property_record:
            property_record = property_service.create_property(
                address=request.address,
                property_type=request.property_type,
                square_footage=request.square_footage,
                bedrooms=request.bedrooms,
                bathrooms=request.bathrooms,
                year_built=request.year_built,
                latitude=request.latitude,
                longitude=request.longitude
            )
        
        # Perform analysis
        analysis_results = property_service.perform_cma_analysis(property_record)
        
        # Save analysis
        cma_record = property_service.save_cma_analysis(property_record.id, analysis_results)
        
        # Convert property record to dict for PDF generator
        subject_property = {
            "address": property_record.address,
            "property_type": property_record.property_type,
            "square_footage": property_record.square_footage,
            "bedrooms": property_record.bedrooms,
            "bathrooms": property_record.bathrooms,
            "year_built": property_record.year_built,
            "lot_size": property_record.lot_size
        }
        
        # Generate PDF
        pdf_generator = CMAReportGenerator()
        pdf_content = pdf_generator.generate_cma_report(analysis_results, subject_property)
        
        # Create filename
        safe_address = "".join(c for c in request.address if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"CMA_Report_{safe_address}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Return PDF as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.get("/cma/history")
async def get_analysis_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get CMA analysis history for current user"""
    property_service = PropertyService(db)
    analyses = property_service.get_user_cma_analyses(current_user.id)
    
    return [
        {
            "analysis_id": analysis.id,
            "property_id": analysis.subject_property_id,
            "address": analysis.subject_property.address,
            "estimated_value": analysis.estimated_value_most_likely,
            "confidence_score": analysis.confidence_score,
            "analysis_date": analysis.analysis_date
        }
        for analysis in analyses
    ]

@router.get("/properties/{property_id}")
async def get_property(
    property_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get property details by ID (user must own the property)"""
    property_record = db.query(Property).filter(
        Property.id == property_id,
        Property.owner_id == current_user.id
    ).first()
    
    if not property_record:
        raise HTTPException(status_code=404, detail="Property not found")
    
    return {
        "id": property_record.id,
        "address": property_record.address,
        "square_footage": property_record.square_footage,
        "bedrooms": property_record.bedrooms,
        "bathrooms": property_record.bathrooms,
        "year_built": property_record.year_built,
        "property_type": property_record.property_type
    }

@router.get("/cma/report/{analysis_id}")
async def download_cma_report(
    analysis_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download PDF report for an existing CMA analysis (requires authentication)
    """
    try:
        property_service = PropertyService(db)
        
        # Get the analysis record
        analysis = property_service.get_cma_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
        
        # Check if user owns this analysis
        if analysis.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to this analysis")
        
        # Get the property record
        property_record = db.query(Property).filter(Property.id == analysis.subject_property_id).first()
        if not property_record:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Parse stored analysis data
        try:
            import json
            stored_analysis = json.loads(analysis.analysis_data)
        except:
            stored_analysis = {
                "estimated_value": {
                    "low": analysis.estimated_value_low,
                    "high": analysis.estimated_value_high,
                    "most_likely": analysis.estimated_value_most_likely
                },
                "confidence_score": analysis.confidence_score,
                "comparables": []
            }
        
        # Convert property record to dict
        subject_property = {
            "address": property_record.address,
            "property_type": property_record.property_type or "single_family",
            "square_footage": property_record.square_footage or 2000,
            "bedrooms": property_record.bedrooms or 3,
            "bathrooms": property_record.bathrooms or 2.0,
            "year_built": property_record.year_built or 2020,
            "lot_size": property_record.lot_size or 7000
        }
        
        # Generate PDF
        pdf_generator = CMAReportGenerator()
        pdf_content = pdf_generator.generate_cma_report(stored_analysis, subject_property)
        
        # Create filename
        safe_address = "".join(c for c in property_record.address if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"CMA_Report_{analysis_id}.pdf"
        
        # Return PDF as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF download failed: {str(e)}") 