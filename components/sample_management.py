"""
Sample Management Utilities
===========================
Comprehensive utilities for sample lifecycle management including:
- Auto-generated Sample IDs (SAMPLE-YYYY-XXXXX)
- Auto-generated Project IDs (PROJECT-YYYY-XXXXX)
- QR Code generation with encoded sample data
- Route Card PDF generation
- Sample status workflow management
"""

import os
import io
import json
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List
from pathlib import Path

import qrcode
from qrcode.image.pil import PilImage
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from config.database import get_db
from sqlalchemy import select, func


# ============================================================================
# ID GENERATION UTILITIES
# ============================================================================

def generate_sample_id() -> str:
    """
    Generate a unique Sample ID in format: SAMPLE-YYYY-XXXXX

    Returns:
        str: Unique sample identifier (e.g., SAMPLE-2024-00001)
    """
    from database import Sample

    year = datetime.now().year
    prefix = f"SAMPLE-{year}-"

    with get_db() as db:
        # Get the highest sequence number for this year
        result = db.execute(
            select(Sample.sample_id)
            .where(Sample.sample_id.like(f"{prefix}%"))
            .order_by(Sample.sample_id.desc())
            .limit(1)
        ).scalar()

        if result:
            # Extract the sequence number and increment
            try:
                seq_num = int(result.split('-')[-1])
                next_seq = seq_num + 1
            except (ValueError, IndexError):
                next_seq = 1
        else:
            next_seq = 1

        return f"{prefix}{next_seq:05d}"


def generate_project_id() -> str:
    """
    Generate a unique Project ID in format: PROJECT-YYYY-XXXXX

    Returns:
        str: Unique project identifier (e.g., PROJECT-2024-00001)
    """
    from database import Sample

    year = datetime.now().year
    prefix = f"PROJECT-{year}-"

    with get_db() as db:
        # Get the highest sequence number for this year
        result = db.execute(
            select(Sample.project_id)
            .where(Sample.project_id.like(f"{prefix}%"))
            .order_by(Sample.project_id.desc())
            .limit(1)
        ).scalar()

        if result:
            try:
                seq_num = int(result.split('-')[-1])
                next_seq = seq_num + 1
            except (ValueError, IndexError):
                next_seq = 1
        else:
            next_seq = 1

        return f"{prefix}{next_seq:05d}"


def generate_receipt_number() -> str:
    """Generate unique receipt number: RCP-YYYYMMDD-XXXXX"""
    from database import SampleReceipt

    date_str = datetime.now().strftime("%Y%m%d")
    prefix = f"RCP-{date_str}-"

    with get_db() as db:
        result = db.execute(
            select(SampleReceipt.receipt_number)
            .where(SampleReceipt.receipt_number.like(f"{prefix}%"))
            .order_by(SampleReceipt.receipt_number.desc())
            .limit(1)
        ).scalar()

        if result:
            try:
                seq_num = int(result.split('-')[-1])
                next_seq = seq_num + 1
            except (ValueError, IndexError):
                next_seq = 1
        else:
            next_seq = 1

        return f"{prefix}{next_seq:05d}"


def generate_route_card_number() -> str:
    """Generate unique route card number: RC-YYYYMMDD-XXXXX"""
    from database import RouteCard

    date_str = datetime.now().strftime("%Y%m%d")
    prefix = f"RC-{date_str}-"

    with get_db() as db:
        result = db.execute(
            select(RouteCard.route_card_number)
            .where(RouteCard.route_card_number.like(f"{prefix}%"))
            .order_by(RouteCard.route_card_number.desc())
            .limit(1)
        ).scalar()

        if result:
            try:
                seq_num = int(result.split('-')[-1])
                next_seq = seq_num + 1
            except (ValueError, IndexError):
                next_seq = 1
        else:
            next_seq = 1

        return f"{prefix}{next_seq:05d}"


def generate_assignment_number() -> str:
    """Generate unique test assignment number: TA-YYYYMMDD-XXXXX"""
    from database import SampleTestAssignment

    date_str = datetime.now().strftime("%Y%m%d")
    prefix = f"TA-{date_str}-"

    with get_db() as db:
        result = db.execute(
            select(SampleTestAssignment.assignment_number)
            .where(SampleTestAssignment.assignment_number.like(f"{prefix}%"))
            .order_by(SampleTestAssignment.assignment_number.desc())
            .limit(1)
        ).scalar()

        if result:
            try:
                seq_num = int(result.split('-')[-1])
                next_seq = seq_num + 1
            except (ValueError, IndexError):
                next_seq = 1
        else:
            next_seq = 1

        return f"{prefix}{next_seq:05d}"


# ============================================================================
# QR CODE GENERATION
# ============================================================================

def generate_sample_qr_code(
    sample_id: str,
    project_id: str,
    additional_data: Optional[Dict[str, Any]] = None
) -> Tuple[str, bytes, str]:
    """
    Generate QR code for a sample with encoded data.

    QR Code Format: "sample_id|project_id|timestamp"
    Additional data is stored in the database, not in the QR code itself.

    Args:
        sample_id: The sample identifier
        project_id: The project identifier
        additional_data: Optional additional metadata

    Returns:
        Tuple of (qr_code_string, image_bytes, file_path)
    """
    # Create QR code data string
    timestamp = datetime.now().isoformat()
    qr_data_string = f"{sample_id}|{project_id}|{timestamp}"

    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data_string)
    qr.make(fit=True)

    # Create image
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Save to bytes
    img_bytes = io.BytesIO()
    qr_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Save to file
    qr_dir = Path("static/qr_codes")
    qr_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{sample_id.replace('-', '_')}_qr.png"
    file_path = qr_dir / filename

    with open(file_path, 'wb') as f:
        f.write(img_bytes.getvalue())

    img_bytes.seek(0)
    return qr_data_string, img_bytes.getvalue(), str(file_path)


def decode_sample_qr_code(qr_data: str) -> Optional[Dict[str, str]]:
    """
    Decode a sample QR code string.

    Args:
        qr_data: The QR code data string

    Returns:
        Dictionary with sample_id, project_id, timestamp or None if invalid
    """
    try:
        parts = qr_data.split('|')
        if len(parts) >= 3:
            return {
                'sample_id': parts[0],
                'project_id': parts[1],
                'timestamp': parts[2]
            }
    except Exception:
        pass
    return None


def get_sample_by_qr_code(qr_data: str) -> Optional[Any]:
    """
    Look up a sample by its QR code data.

    Args:
        qr_data: The QR code data string

    Returns:
        Sample object or None if not found
    """
    from database import Sample

    decoded = decode_sample_qr_code(qr_data)
    if not decoded:
        return None

    with get_db() as db:
        sample = db.execute(
            select(Sample).where(Sample.sample_id == decoded['sample_id'])
        ).scalar()
        return sample


# ============================================================================
# ROUTE CARD PDF GENERATION
# ============================================================================

def generate_route_card_pdf(
    sample_id: str,
    project_id: str,
    service_request_number: str,
    client_name: str,
    sample_type: str,
    protocols: List[Dict[str, Any]],
    qr_code_path: str,
    additional_info: Optional[Dict[str, Any]] = None
) -> Tuple[bytes, str]:
    """
    Generate a Route Card PDF for sample tracking.

    Args:
        sample_id: Sample identifier
        project_id: Project identifier
        service_request_number: Service request number
        client_name: Client name
        sample_type: Type of sample
        protocols: List of protocol dictionaries with 'id', 'name', 'status'
        qr_code_path: Path to QR code image
        additional_info: Optional additional information

    Returns:
        Tuple of (pdf_bytes, file_path)
    """
    # Create output directory
    route_cards_dir = Path("static/route_cards")
    route_cards_dir.mkdir(parents=True, exist_ok=True)

    filename = f"route_card_{sample_id.replace('-', '_')}.pdf"
    file_path = route_cards_dir / filename

    # Create PDF buffer
    buffer = io.BytesIO()

    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'RouteCardTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=10*mm,
        textColor=colors.HexColor('#FF6B35')
    )

    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=5*mm,
        spaceAfter=3*mm,
        textColor=colors.HexColor('#1a1a2e')
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=2*mm,
        spaceAfter=2*mm
    )

    # Build content
    story = []

    # Title
    story.append(Paragraph("SAMPLE ROUTE CARD", title_style))
    story.append(Spacer(1, 5*mm))

    # Header info table with QR code
    header_data = [
        ['Sample ID:', sample_id, '', ''],
        ['Project ID:', project_id, '', ''],
        ['Service Request:', service_request_number, '', ''],
        ['Client:', client_name, '', ''],
        ['Sample Type:', sample_type, '', ''],
        ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M'), '', '']
    ]

    # Add QR code if available
    qr_image = None
    if qr_code_path and os.path.exists(qr_code_path):
        qr_image = RLImage(qr_code_path, width=30*mm, height=30*mm)
        # Add QR code to first row spanning multiple rows
        header_data[0][2] = qr_image
        header_data[0][3] = 'Scan for\nSample Info'

    header_table = Table(header_data, colWidths=[35*mm, 55*mm, 35*mm, 35*mm])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (3, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SPAN', (2, 0), (2, 5)),  # QR code spans all rows
        ('SPAN', (3, 0), (3, 5)),  # Label spans all rows
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0, 0), (1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 3*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10*mm))

    # Test Protocol Workflow Section
    story.append(Paragraph("TEST PROTOCOL WORKFLOW", header_style))

    # Protocol table
    protocol_data = [['#', 'Protocol ID', 'Protocol Name', 'Status', 'Date', 'Technician']]

    for idx, protocol in enumerate(protocols, 1):
        protocol_data.append([
            str(idx),
            protocol.get('id', ''),
            protocol.get('name', '')[:40],  # Truncate long names
            protocol.get('status', 'Pending'),
            '',  # Date to be filled
            ''   # Technician to be filled
        ])

    protocol_table = Table(
        protocol_data,
        colWidths=[10*mm, 25*mm, 55*mm, 25*mm, 25*mm, 25*mm]
    )
    protocol_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B35')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 2*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2*mm),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(protocol_table)
    story.append(Spacer(1, 10*mm))

    # Status Tracking Section
    story.append(Paragraph("STATUS TRACKING", header_style))

    status_data = [
        ['Status', 'Date', 'Time', 'Location', 'Performed By', 'Signature'],
        ['RECEIVED', '', '', '', '', ''],
        ['INSPECTED', '', '', '', '', ''],
        ['ALLOCATED', '', '', '', '', ''],
        ['IN TEST', '', '', '', '', ''],
        ['COMPLETED', '', '', '', '', ''],
        ['ANALYZED', '', '', '', '', ''],
        ['REPORTED', '', '', '', '', ''],
    ]

    status_table = Table(
        status_data,
        colWidths=[25*mm, 25*mm, 20*mm, 30*mm, 30*mm, 30*mm]
    )
    status_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 3*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 10*mm))

    # Notes Section
    story.append(Paragraph("NOTES / OBSERVATIONS", header_style))

    notes_data = [[''] for _ in range(5)]  # 5 empty rows for notes
    notes_table = Table(notes_data, colWidths=[160*mm], rowHeights=[8*mm] * 5)
    notes_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(notes_table)
    story.append(Spacer(1, 10*mm))

    # Footer with signatures
    story.append(Paragraph("APPROVALS", header_style))

    approval_data = [
        ['Prepared By:', '', 'Reviewed By:', '', 'Approved By:', ''],
        ['Signature:', '', 'Signature:', '', 'Signature:', ''],
        ['Date:', '', 'Date:', '', 'Date:', ''],
    ]

    approval_table = Table(
        approval_data,
        colWidths=[25*mm, 28*mm, 25*mm, 28*mm, 25*mm, 28*mm]
    )
    approval_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
        ('LINEBELOW', (1, 0), (1, -1), 0.5, colors.black),
        ('LINEBELOW', (3, 0), (3, -1), 0.5, colors.black),
        ('LINEBELOW', (5, 0), (5, -1), 0.5, colors.black),
    ]))
    story.append(approval_table)

    # Build PDF
    doc.build(story)

    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()

    # Save to file
    with open(file_path, 'wb') as f:
        f.write(pdf_bytes)

    return pdf_bytes, str(file_path)


# ============================================================================
# SAMPLE STATUS WORKFLOW
# ============================================================================

SAMPLE_STATUS_WORKFLOW = {
    'received': ['inspected', 'rejected', 'on_hold'],
    'inspected': ['allocated', 'rejected', 'on_hold'],
    'allocated': ['assigned', 'on_hold'],
    'assigned': ['in_test', 'on_hold'],
    'in_test': ['completed', 'on_hold'],
    'completed': ['analyzed', 'on_hold'],
    'analyzed': ['reported', 'on_hold'],
    'reported': [],  # Terminal state
    'rejected': [],  # Terminal state
    'on_hold': ['received', 'inspected', 'allocated', 'assigned', 'in_test', 'completed', 'analyzed']  # Can resume from on_hold
}


def can_transition_to(current_status: str, new_status: str) -> bool:
    """
    Check if a status transition is valid.

    Args:
        current_status: Current sample status
        new_status: Desired new status

    Returns:
        True if transition is allowed, False otherwise
    """
    allowed = SAMPLE_STATUS_WORKFLOW.get(current_status.lower(), [])
    return new_status.lower() in allowed


def update_sample_status(
    sample_id: int,
    new_status: str,
    changed_by_id: int,
    changed_by_name: str,
    new_location: Optional[str] = None,
    change_source: str = "manual",
    reason: Optional[str] = None,
    notes: Optional[str] = None,
    qr_scan_id: Optional[int] = None
) -> Tuple[bool, str]:
    """
    Update sample status with full audit trail.

    Args:
        sample_id: Database ID of the sample
        new_status: New status to set
        changed_by_id: User ID making the change
        changed_by_name: User name making the change
        new_location: Optional new location
        change_source: Source of change (manual, qr_scan, system, workflow)
        reason: Reason for status change
        notes: Additional notes
        qr_scan_id: QR scan log ID if triggered by scan

    Returns:
        Tuple of (success, message)
    """
    from database import Sample, SampleStatusHistory, SampleStatus

    with get_db() as db:
        # Get the sample
        sample = db.execute(
            select(Sample).where(Sample.id == sample_id)
        ).scalar()

        if not sample:
            return False, "Sample not found"

        # Check if transition is valid
        current_status = sample.status.value if hasattr(sample.status, 'value') else str(sample.status)
        if not can_transition_to(current_status, new_status):
            return False, f"Cannot transition from {current_status} to {new_status}"

        # Create status history record
        history = SampleStatusHistory(
            sample_id=sample_id,
            previous_status=current_status,
            new_status=new_status,
            previous_location=sample.current_location,
            new_location=new_location or sample.current_location,
            changed_by_id=changed_by_id,
            changed_by_name=changed_by_name,
            change_source=change_source,
            qr_scan_id=qr_scan_id,
            reason=reason,
            notes=notes,
            metadata={
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        db.add(history)

        # Update sample status
        sample.status = SampleStatus(new_status)
        if new_location:
            sample.current_location = new_location

        # Update timestamps based on status
        if new_status == 'completed':
            sample.completed_at = datetime.utcnow()

        db.commit()

        return True, f"Status updated from {current_status} to {new_status}"


def get_sample_status_history(sample_id: int) -> List[Dict[str, Any]]:
    """
    Get the complete status history for a sample.

    Args:
        sample_id: Database ID of the sample

    Returns:
        List of status history records
    """
    from database import SampleStatusHistory

    with get_db() as db:
        records = db.execute(
            select(SampleStatusHistory)
            .where(SampleStatusHistory.sample_id == sample_id)
            .order_by(SampleStatusHistory.changed_at.desc())
        ).scalars().all()

        return [
            {
                'id': r.id,
                'previous_status': r.previous_status,
                'new_status': r.new_status,
                'previous_location': r.previous_location,
                'new_location': r.new_location,
                'changed_by': r.changed_by_name,
                'change_source': r.change_source,
                'reason': r.reason,
                'notes': r.notes,
                'changed_at': r.changed_at.isoformat() if r.changed_at else None
            }
            for r in records
        ]


# ============================================================================
# SAMPLE ALLOCATION
# ============================================================================

def allocate_samples_from_inspection(
    inspection_id: int,
    service_request_id: int,
    allocated_by_id: int,
    sample_count: int = 1
) -> List[Dict[str, Any]]:
    """
    Allocate samples after successful inspection.
    Creates Sample records with auto-generated IDs and QR codes.

    Args:
        inspection_id: Incoming inspection ID
        service_request_id: Service request ID
        allocated_by_id: User ID performing allocation
        sample_count: Number of samples to allocate

    Returns:
        List of created sample dictionaries
    """
    from database import Sample, SampleReceipt, ServiceRequest, IncomingInspection, SampleStatus

    created_samples = []

    with get_db() as db:
        # Get service request for details
        sr = db.execute(
            select(ServiceRequest).where(ServiceRequest.id == service_request_id)
        ).scalar()

        # Get inspection for details
        inspection = db.execute(
            select(IncomingInspection).where(IncomingInspection.id == inspection_id)
        ).scalar()

        if not sr:
            return []

        # Generate a project ID for this batch
        project_id = generate_project_id()

        for i in range(sample_count):
            # Generate unique sample ID
            sample_id_code = generate_sample_id()

            # Generate QR code
            qr_code_string, qr_bytes, qr_path = generate_sample_qr_code(
                sample_id_code,
                project_id,
                additional_data={
                    'service_request': sr.request_number,
                    'client': sr.client_name
                }
            )

            # Create sample record
            sample = Sample(
                sample_id=sample_id_code,
                project_id=project_id,
                service_request_id=service_request_id,
                inspection_id=inspection_id,
                sample_type=sr.sample_type,
                manufacturer=sr.manufacturer,
                model_number=sr.model_number,
                serial_number=sr.serial_numbers[i] if sr.serial_numbers and i < len(sr.serial_numbers) else None,
                qr_code=qr_code_string,
                qr_code_image_path=qr_path,
                qr_data={
                    'sample_id': sample_id_code,
                    'project_id': project_id,
                    'service_request': sr.request_number,
                    'allocated_at': datetime.utcnow().isoformat()
                },
                status=SampleStatus.ALLOCATED,
                current_location="Receiving",
                allocation_date=datetime.utcnow(),
                allocated_by_id=allocated_by_id,
                assigned_protocol_ids=sr.requested_protocols,
                tests_total=len(sr.requested_protocols) if sr.requested_protocols else 0,
                specifications={
                    'length_mm': inspection.length_mm if inspection else None,
                    'width_mm': inspection.width_mm if inspection else None,
                    'thickness_mm': inspection.thickness_mm if inspection else None,
                    'weight_kg': inspection.weight_kg if inspection else None
                }
            )

            db.add(sample)
            db.flush()  # Get the ID

            created_samples.append({
                'id': sample.id,
                'sample_id': sample_id_code,
                'project_id': project_id,
                'qr_code': qr_code_string,
                'qr_code_path': qr_path,
                'status': 'allocated'
            })

        # Mark inspection as having triggered allocation
        if inspection:
            inspection.allocation_triggered = True
            inspection.allocated_sample_id = created_samples[0]['id'] if created_samples else None

        db.commit()

    return created_samples


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_samples_by_status(status: str) -> List[Dict[str, Any]]:
    """Get all samples with a specific status."""
    from database import Sample

    with get_db() as db:
        samples = db.execute(
            select(Sample).where(Sample.status == status)
        ).scalars().all()

        return [
            {
                'id': s.id,
                'sample_id': s.sample_id,
                'project_id': s.project_id,
                'status': s.status.value if hasattr(s.status, 'value') else str(s.status),
                'current_location': s.current_location,
                'sample_type': s.sample_type,
                'manufacturer': s.manufacturer,
                'created_at': s.created_at.isoformat() if s.created_at else None
            }
            for s in samples
        ]


def get_sample_dashboard_stats() -> Dict[str, Any]:
    """Get statistics for sample dashboard."""
    from database import Sample, SampleStatus

    with get_db() as db:
        # Count by status
        stats = {}
        for status in SampleStatus:
            count = db.execute(
                select(func.count(Sample.id)).where(Sample.status == status)
            ).scalar()
            stats[status.value] = count

        # Total samples
        total = sum(stats.values())

        # Samples created today
        today = datetime.utcnow().date()
        today_count = db.execute(
            select(func.count(Sample.id))
            .where(func.date(Sample.created_at) == today)
        ).scalar()

        return {
            'total': total,
            'by_status': stats,
            'created_today': today_count,
            'in_progress': stats.get('in_test', 0) + stats.get('assigned', 0),
            'completed': stats.get('completed', 0) + stats.get('analyzed', 0) + stats.get('reported', 0)
        }
