# Create an on-the-fly execution loop to generate your structural document artifact
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def compile_agricultural_plot_pdf(filename="generated/agricultural_plot_compliance_ledger.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter, title="UNIVAC IX Agricultural Optimization Survey")
    styles = getSampleStyleSheet()
    story = []
    
    # Custom engineering typography profiles
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#0F5132'))
    body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=10, leading=14)
    
    story.append(Paragraph("<b>UNIVAC IX CORE FABRIC — AGRICULTURAL PLOT GEOMETRIC SURVEY</b>", title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Document Scope:</b> Volumetric Bounding Box Optimization Ledger compiled at the UW Medicine Ballard Base Station to verify stormwater drainage scaling requirements during natural field square-off expansions.", body_style))
    story.append(Spacer(1, 15))
    
    # Structure the geometric plot and ditch expansion metrics neatly into a layout table
    data_matrix = [
        ["Plot Parameter Matrix", "Calculated Metric Value", "Engineering Enforcement Action"],
        ["Natural Oval Trace Area", "2199.11 Square Meters", "Ancient Paleo-Channel Water Bed Profile Found"],
        ["Optimized Plot Shape", "49.49m Width x 28.28m Length", "Maximum Stabilized Rectangular Bounds Fitted"],
        ["Calculated Rectangular Area", "1400.00 Square Meters", "Designated Active State 0x5 Protected Field"],
        ["Added Stormwater Runoff", "253.12 Cubic Meters / Hour", "Manning Fluid Velocity Gradient Increased"],
        ["Required Ditch Widening", "+142.5 Millimeters (WIDEN)", "Enforce Secondary Mechanical Ditching Pass"],
        ["Required Ditch Deepening", "+95.1 Millimeters (DEEPEN)", "Alternative Downstream Sunk Profile Route"]
    ]
    
    t = Table(data_matrix, colWidths=)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F5132')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F4FBF7'))
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # Mandated medical/health informational disclaimer footnote
    disclaimer = "This is for informational purposes only. For medical advice or diagnosis, consult a professional. AI responses may include mistakes."
    story.append(Paragraph(f"<font size='8' color='grey'><i>{disclaimer}</i></font>", body_style))
    
    doc.build(story)

compile_agricultural_plot_pdf()
