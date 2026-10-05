# Create an on-the-fly execution loop to generate your structural document artifact
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def compile_geotech_pdf_report(filename="generated/geotechnical_compliance_ledger.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter, title="UNIVAC IX Sub-surface Compliance Matrix")
    styles = getSampleStyleSheet()
    story = []
    
    # Custom engineering typography profiles
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#1A365D'))
    body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=10, leading=14)
    
    story.append(Paragraph("<b>UNIVAC IX CORE FABRIC — GEOTECHNICAL COMPLIANCE REPORT</b>", title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Document Scope:</b> Volumetric Airborne Acoustic Sub-surface Profiling Analysis data compiled at the UW Medicine Ballard Base Station to verify municipal land carving clear zones.", body_style))
    story.append(Spacer(1, 15))
    
    # Structure the IPC/IEC and hydrologic data rows neatly into a layout table
    data_matrix = [
        ["Target Parameter", "Measured Values", "Regulatory Evaluation Status"],
        ["Bedrock Stratum Depth", "5.2 Meters Subgrade", "VERIFIED STABLE — EXCELLENT SURCHARGE ANCHOR"],
        ["Saturated Silt Pocket", "8.4 Meters Subgrade", "🚨 CRITICAL EXCEPTION — LANDSLIDE COLLAPSE HAZARD"],
        ["Storm Runoff Coeff (C)", "0.85 (Max Limit)", "HIGH RISK — DESIGN FLASH FLOOD CHANNELS DIRECTLY"],
        ["OSHA Breathing Zone O2", "19.5% Baseline", "NOMINAL — COMPLIANT WITH SAFETY ACTIONS [1.15]"]
    ]
    
    t = Table(data_matrix, colWidths=[150, 120, 230])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F7FAFC'))
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # Mandated medical/health informational disclaimer footnote [1.1]
    disclaimer = "This is for informational purposes only. For medical advice or diagnosis, consult a professional. AI responses may include mistakes."
    story.append(Paragraph(f"<font size='8' color='grey'><i>{disclaimer}</i></font>", body_style))
    
    doc.build(story)

compile_geotech_pdf_report()
