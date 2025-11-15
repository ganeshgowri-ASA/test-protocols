"""
PDF Report Generator
====================
Generate PDF reports for audits using ReportLab.
"""

from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from config.settings import config
import os


def generate_audit_report_pdf(audit, output_path=None):
    """
    Generate comprehensive audit report PDF

    Args:
        audit: Audit object
        output_path: Optional output file path

    Returns:
        Path to generated PDF
    """
    if output_path is None:
        filename = f"audit_report_{audit.audit_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(config.REPORTS_DIR, filename)

    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        spaceBefore=12
    )

    # Title
    story.append(Paragraph("AUDIT REPORT", title_style))
    story.append(Spacer(1, 0.2*inch))

    # Audit Information Table
    audit_info_data = [
        ['Audit Number:', audit.audit_number],
        ['Audit Date:', audit.actual_date.strftime('%Y-%m-%d') if audit.actual_date else 'N/A'],
        ['Auditee Entity:', audit.schedule.auditee_entity.name if audit.schedule else 'N/A'],
        ['Audit Type:', audit.schedule.audit_type.name if audit.schedule else 'N/A'],
        ['Lead Auditor:', audit.schedule.auditor.full_name if audit.schedule else 'N/A'],
        ['Duration:', f"{audit.duration_hours} hours" if audit.duration_hours else 'N/A'],
        ['Status:', audit.status.value],
    ]

    audit_info_table = Table(audit_info_data, colWidths=[2*inch, 4*inch])
    audit_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))

    story.append(audit_info_table)
    story.append(Spacer(1, 0.3*inch))

    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    summary_text = audit.executive_summary or "No executive summary provided."
    story.append(Paragraph(summary_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    # Findings Summary
    story.append(Paragraph("Findings Summary", heading_style))

    findings_data = [
        ['Finding Type', 'Count'],
        ['Total Findings', str(audit.findings_count)],
        ['Non-Conformances (NC)', str(audit.nc_count)],
        ['Opportunities for Improvement (OFI)', str(audit.ofi_count)],
        ['Observations', str(audit.observations_count)],
    ]

    findings_table = Table(findings_data, colWidths=[3*inch, 2*inch])
    findings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))

    story.append(findings_table)
    story.append(Spacer(1, 0.3*inch))

    # Strengths
    if audit.strengths:
        story.append(Paragraph("Strengths", heading_style))
        story.append(Paragraph(audit.strengths, styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))

    # Opportunities
    if audit.opportunities:
        story.append(Paragraph("Opportunities for Improvement", heading_style))
        story.append(Paragraph(audit.opportunities, styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))

    # Overall Conclusion
    if audit.overall_conclusion:
        story.append(Paragraph("Overall Conclusion", heading_style))
        story.append(Paragraph(audit.overall_conclusion, styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))

    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer_text = f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {config.APP_NAME} | {config.SESSION_ID}"
    story.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )))

    # Build PDF
    doc.build(story)

    return output_path


def generate_nc_ofi_report_pdf(nc_ofis, output_path=None):
    """
    Generate NC/OFI summary report PDF

    Args:
        nc_ofis: List of NC/OFI objects
        output_path: Optional output file path

    Returns:
        Path to generated PDF
    """
    if output_path is None:
        filename = f"nc_ofi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(config.REPORTS_DIR, filename)

    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=20,
        alignment=TA_CENTER
    )

    story.append(Paragraph("NC/OFI Summary Report", title_style))
    story.append(Spacer(1, 0.3*inch))

    # NC/OFI Table
    table_data = [['NC #', 'Type', 'Severity', 'Category', 'Description', 'Status']]

    for nc in nc_ofis:
        desc = nc.description[:100] + '...' if len(nc.description) > 100 else nc.description
        table_data.append([
            nc.nc_number,
            nc.type.value.upper(),
            nc.severity.value,
            nc.category or '-',
            desc,
            nc.status.value
        ])

    nc_table = Table(table_data, colWidths=[1*inch, 0.6*inch, 0.8*inch, 1.2*inch, 2.5*inch, 1*inch])
    nc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))

    story.append(nc_table)

    # Build PDF
    doc.build(story)

    return output_path
