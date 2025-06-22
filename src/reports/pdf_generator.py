"""
Professional PDF Report Generator for CMA Analysis
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, List
import base64

class CMAReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C3E50')
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#34495E'),
            borderWidth=2,
            borderColor=colors.HexColor('#3498DB'),
            borderPadding=5
        ))
        
        # Property details style
        self.styles.add(ParagraphStyle(
            name='PropertyDetail',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=20
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey
        ))
    
    def generate_cma_report(self, analysis_data: Dict, subject_property: Dict) -> bytes:
        """Generate a complete CMA report PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build the report content
        story = []
        
        # Title page
        story.extend(self._create_title_page(subject_property, analysis_data))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(analysis_data))
        
        # Subject property details
        story.extend(self._create_subject_property_section(subject_property))
        
        # Comparable properties analysis
        story.extend(self._create_comparables_section(analysis_data['comparables']))
        
        # Market analysis and conclusions
        story.extend(self._create_market_analysis_section(analysis_data))
        
        # Appendix
        story.extend(self._create_appendix())
        
        # Build the PDF
        doc.build(story)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_title_page(self, subject_property: Dict, analysis_data: Dict) -> List:
        """Create the title page"""
        story = []
        
        # Main title
        story.append(Paragraph("COMPARATIVE MARKET ANALYSIS", self.styles['ReportTitle']))
        story.append(Spacer(1, 30))
        
        # Property address
        story.append(Paragraph(
            f"<b>{subject_property.get('address', 'Property Address')}</b>",
            self.styles['Heading1']
        ))
        story.append(Spacer(1, 20))
        
        # Key metrics box
        estimated_value = analysis_data['estimated_value']
        key_metrics = [
            ['Estimated Market Value', f"${estimated_value['most_likely']:,}"],
            ['Value Range', f"${estimated_value['low']:,} - ${estimated_value['high']:,}"],
            ['Confidence Level', f"{analysis_data['confidence_score']*100:.0f}%"],
            ['Comparable Properties', f"{len(analysis_data['comparables'])}"],
            ['Analysis Date', datetime.now().strftime("%B %d, %Y")]
        ]
        
        key_table = Table(key_metrics, colWidths=[3*inch, 2*inch])
        key_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ECF0F1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
        ]))
        
        story.append(key_table)
        story.append(Spacer(1, 40))
        
        # Disclaimer
        disclaimer = """
        <i>This Comparative Market Analysis (CMA) is based on recent sales of similar properties 
        in the area and is intended for informational purposes only. This analysis does not 
        constitute a formal appraisal and should not be used for lending purposes.</i>
        """
        story.append(Paragraph(disclaimer, self.styles['Normal']))
        
        return story
    
    def _create_executive_summary(self, analysis_data: Dict) -> List:
        """Create executive summary section"""
        story = []
        
        story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        
        estimated_value = analysis_data['estimated_value']
        confidence = analysis_data['confidence_score'] * 100
        
        summary_text = f"""
        Based on an analysis of {len(analysis_data['comparables'])} comparable properties 
        that have sold recently in the area, the estimated market value for this property 
        is <b>${estimated_value['most_likely']:,}</b>.
        
        <br/><br/>
        
        The analysis indicates a value range between ${estimated_value['low']:,} and 
        ${estimated_value['high']:,}, with a confidence level of {confidence:.0f}%.
        
        <br/><br/>
        
        Key findings from the analysis:
        """
        
        story.append(Paragraph(summary_text, self.styles['Normal']))
        
        # Key findings
        avg_adjustment = analysis_data.get('adjustment_summary', {}).get('average_adjustment', 0)
        findings = [
            f"• Average adjustment to comparables: ${abs(avg_adjustment):,}",
            f"• Most similar comparable has {max(comp['similarity_score'] for comp in analysis_data['comparables']):.1f}% similarity",
            f"• Price range of comparables: ${min(comp['sale_price'] for comp in analysis_data['comparables']):,} - ${max(comp['sale_price'] for comp in analysis_data['comparables']):,}",
            f"• Average days on market: {sum(comp['days_on_market'] for comp in analysis_data['comparables']) // len(analysis_data['comparables'])} days"
        ]
        
        for finding in findings:
            story.append(Paragraph(finding, self.styles['PropertyDetail']))
        
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_subject_property_section(self, subject_property: Dict) -> List:
        """Create subject property details section"""
        story = []
        
        story.append(Paragraph("SUBJECT PROPERTY DETAILS", self.styles['SectionHeader']))
        
        # Property details table
        property_details = [
            ['Address', subject_property.get('address', 'N/A')],
            ['Property Type', subject_property.get('property_type', 'N/A').title()],
            ['Square Footage', f"{subject_property.get('square_footage', 'N/A'):,}" if subject_property.get('square_footage') else 'N/A'],
            ['Bedrooms', str(subject_property.get('bedrooms', 'N/A'))],
            ['Bathrooms', str(subject_property.get('bathrooms', 'N/A'))],
            ['Year Built', str(subject_property.get('year_built', 'N/A'))],
            ['Lot Size', f"{subject_property.get('lot_size', 'N/A'):,} sq ft" if subject_property.get('lot_size') else 'N/A']
        ]
        
        property_table = Table(property_details, colWidths=[2*inch, 4*inch])
        property_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(property_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_comparables_section(self, comparables: List[Dict]) -> List:
        """Create comparable properties section"""
        story = []
        
        story.append(Paragraph("COMPARABLE PROPERTIES ANALYSIS", self.styles['SectionHeader']))
        
        # Comparables table headers
        headers = ['Address', 'Sale Price', 'Adj. Price', 'Sq Ft', 'BR/BA', 'Year', 'DOM', 'Similarity']
        
        # Build table data
        table_data = [headers]
        
        for comp in comparables:
            row = [
                comp['address'][:30] + '...' if len(comp['address']) > 30 else comp['address'],
                f"${comp['sale_price']:,}",
                f"${comp['adjusted_price']:,}",
                f"{comp['square_feet']:,}" if comp['square_feet'] else 'N/A',
                f"{comp['bedrooms']}/{comp['bathrooms']}" if comp['bedrooms'] and comp['bathrooms'] else 'N/A',
                str(comp['year_built']) if comp['year_built'] else 'N/A',
                str(comp['days_on_market']) if comp['days_on_market'] else 'N/A',
                f"{comp['similarity_score']:.1f}%"
            ]
            table_data.append(row)
        
        # Create table
        comp_table = Table(table_data, colWidths=[2*inch, 0.8*inch, 0.8*inch, 0.6*inch, 0.6*inch, 0.5*inch, 0.5*inch, 0.7*inch])
        comp_table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Center all except address
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),     # Left align address
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
        ]))
        
        story.append(comp_table)
        story.append(Spacer(1, 20))
        
        # Detailed adjustments section
        story.append(Paragraph("ADJUSTMENT DETAILS", self.styles['Heading2']))
        
        for i, comp in enumerate(comparables, 1):
            story.append(Paragraph(f"<b>Comparable {i}: {comp['address']}</b>", self.styles['Normal']))
            
            adjustments = comp['adjustments']
            if adjustments['total'] != 0:
                adj_text = "Adjustments made: "
                adj_items = []
                for key, value in adjustments.items():
                    if key != 'total' and value != 0:
                        adj_items.append(f"{key.replace('_', ' ').title()}: ${value:+,}")
                
                if adj_items:
                    adj_text += ", ".join(adj_items)
                    adj_text += f" | <b>Total Adjustment: ${adjustments['total']:+,}</b>"
                else:
                    adj_text += "No adjustments needed"
            else:
                adj_text = "No adjustments needed - excellent comparable"
            
            story.append(Paragraph(adj_text, self.styles['PropertyDetail']))
            story.append(Spacer(1, 8))
        
        return story
    
    def _create_market_analysis_section(self, analysis_data: Dict) -> List:
        """Create market analysis section"""
        story = []
        
        story.append(Paragraph("MARKET ANALYSIS & CONCLUSIONS", self.styles['SectionHeader']))
        
        # Analysis conclusions
        estimated_value = analysis_data['estimated_value']
        confidence = analysis_data['confidence_score'] * 100
        
        conclusion_text = f"""
        <b>Valuation Conclusion:</b><br/>
        Based on the analysis of comparable sales, the most likely market value for this property 
        is <b>${estimated_value['most_likely']:,}</b>. This estimate is supported by 
        {len(analysis_data['comparables'])} recent comparable sales with a confidence level of {confidence:.0f}%.
        
        <br/><br/>
        
        <b>Market Conditions:</b><br/>
        The comparable properties sold between {min(comp['days_on_market'] for comp in analysis_data['comparables'])} 
        and {max(comp['days_on_market'] for comp in analysis_data['comparables'])} days on market, 
        indicating {"a balanced" if 30 <= sum(comp['days_on_market'] for comp in analysis_data['comparables']) // len(analysis_data['comparables']) <= 60 else "varying"} market conditions.
        
        <br/><br/>
        
        <b>Methodology:</b><br/>
        This analysis uses the Sales Comparison Approach, comparing the subject property to recently sold 
        similar properties. Adjustments were made for differences in size, age, bedrooms, bathrooms, 
        and other relevant factors to arrive at an adjusted value for each comparable.
        """
        
        story.append(Paragraph(conclusion_text, self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        return story
    
    def _create_appendix(self) -> List:
        """Create appendix section"""
        story = []
        
        story.append(Paragraph("APPENDIX - METHODOLOGY", self.styles['SectionHeader']))
        
        methodology_text = """
        <b>Adjustment Methodology:</b><br/>
        • <b>Size Adjustments:</b> $150 per square foot difference<br/>
        • <b>Bedroom Adjustments:</b> $15,000 per bedroom difference<br/>
        • <b>Bathroom Adjustments:</b> $8,000 per bathroom difference<br/>
        • <b>Age Adjustments:</b> $500 per year difference<br/>
        • <b>Time Adjustments:</b> Applied for sales older than 90 days<br/>
        
        <br/>
        
        <b>Similarity Scoring:</b><br/>
        Properties are scored based on:<br/>
        • Size similarity (30%)<br/>
        • Bedroom count (15%)<br/>
        • Bathroom count (15%)<br/>
        • Age similarity (20%)<br/>
        • Geographic proximity (20%)<br/>
        
        <br/>
        
        <b>Data Sources:</b><br/>
        • Multiple Listing Service (MLS) data<br/>
        • Public records<br/>
        • Recent comparable sales within 6 months<br/>
        """
        
        story.append(Paragraph(methodology_text, self.styles['Normal']))
        
        return story 