"""
Sample Receipt Module - QR Code Generation & Tracking
======================================================
Create comprehensive sample receipt system with QR code generation
for tracking samples throughout the testing lifecycle.
"""

import streamlit as st
from datetime import datetime
import sys
import json
import io
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from components.navigation import render_header, render_sidebar_navigation
from components.qr_generator import get_qr_generator
from components.sample_management import generate_sample_id
from database import (
    Sample, SampleReceipt, ServiceRequest, RequestStatus, 
    SampleStatus, SampleStatusHistory, User
)
from sqlalchemy import select, desc, and_, or_, func
from sqlalchemy.orm import load_only
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import inch

# Page configuration
setup_page_config(page_title="Sample Receipt & QR Tracking", page_icon="📦")

# Render navigation
render_header("Sample Receipt & QR Tracking", "Generate QR codes and track samples")
render_sidebar_navigation()


def main():
    """Main sample receipt page with QR code generation"""

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs([
        "📦 Receive Sample", 
        "🔍 View Samples", 
        "📝 Chain of Custody"
    ])

    with tab1:
        render_receive_sample_form()

    with tab2:
        render_view_samples()

    with tab3:
        render_chain_of_custody()


def render_receive_sample_form():
    """Render form to receive and register new samples with QR code generation"""
    
    st.markdown("### 📦 Receive New Sample")
    st.markdown("Record sample details and generate unique QR codes for tracking")

    # Get active service requests
    with get_db() as db:
        service_requests = db.execute(
            select(ServiceRequest)
            .where(ServiceRequest.status.in_([
                RequestStatus.SUBMITTED, 
                RequestStatus.APPROVED,
                RequestStatus.IN_PROGRESS
            ]))
            .order_by(desc(ServiceRequest.created_at))
        ).scalars().all()

        sr_options = {
            f"{sr.request_number} - {sr.client_name}": sr 
            for sr in service_requests
        }

    with st.form("receive_sample_form"):
        # Service Request Selection
        st.markdown("#### 🔗 Link to Service Request")
        
        selected_sr = st.selectbox(
            "Service Request *",
            options=["-- Select Service Request --"] + list(sr_options.keys()),
            help="Link this sample to an existing service request"
        )

        if selected_sr and selected_sr != "-- Select Service Request --":
            sr = sr_options[selected_sr]
            st.info(f"**Client:** {sr.client_name} | **Request:** {sr.request_number}")

        st.divider()

        # Sample Details
        st.markdown("#### 📋 Sample Details")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sample_type = st.selectbox(
                "Sample Type *",
                options=["Module", "Cell", "Material", "Component", "Other"],
                help="Type of sample being received"
            )
            
            quantity = st.number_input(
                "Quantity *",
                min_value=1,
                max_value=100,
                value=1,
                help="Number of samples"
            )

        with col2:
            manufacturer = st.text_input(
                "Manufacturer *",
                placeholder="e.g., SunPower, LG, etc.",
                help="Sample manufacturer"
            )
            
            model = st.text_input(
                "Model/Part Number *",
                placeholder="e.g., SPR-MAX3-400",
                help="Model or part number"
            )

        with col3:
            serial_number = st.text_input(
                "Serial Number(s)",
                placeholder="e.g., SN123456",
                help="Serial number(s), comma-separated if multiple"
            )
            
            batch_number = st.text_input(
                "Batch/Lot Number",
                placeholder="e.g., BATCH-2024-001"
            )

        st.divider()

        # Physical Condition Assessment
        st.markdown("#### ✅ Condition Assessment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            storage_location = st.text_input(
                "Storage Location *",
                placeholder="e.g., Rack A-1, Shelf B-3",
                help="Where sample will be stored"
            )
            
            condition = st.selectbox(
                "Physical Condition *",
                options=["Good", "Fair", "Damaged", "Unknown"],
                help="Initial condition of sample"
            )

        with col2:
            received_by = st.text_input(
                "Received By *",
                value="Technician",  # In production, get from session
                help="Name of person receiving the sample"
            )
            
            received_date = st.date_input(
                "Receipt Date *",
                value=datetime.now().date()
            )

        # Condition Notes
        condition_notes = st.text_area(
            "Condition Notes",
            placeholder="Describe any visible damage, packaging condition, etc.",
            height=100
        )

        st.divider()

        # Photo Upload
        st.markdown("#### 📷 Sample Photos")
        
        sample_photos = st.file_uploader(
            "Upload sample photos (optional)",
            accept_multiple_files=True,
            type=['jpg', 'jpeg', 'png'],
            help="Upload photos documenting sample condition"
        )

        # Additional Notes
        notes = st.text_area(
            "Additional Notes",
            placeholder="Any other relevant information...",
            height=80
        )

        st.divider()

        # Form submission
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.caption("* Required fields")
        
        with col3:
            submit = st.form_submit_button(
                "📦 Register Sample & Generate QR Code", 
                type="primary",
                use_container_width=True
            )

        # Process form submission
        if submit:
            # Validate required fields
            if selected_sr == "-- Select Service Request --":
                st.error("❌ Please select a Service Request")
                return
            
            if not all([sample_type, manufacturer, model, storage_location, received_by]):
                st.error("❌ Please fill all required fields")
                return

            try:
                # Generate unique Sample ID
                sample_id = generate_sample_id()
                
                # Generate QR code in format SR-YYYYMMDD-XXXX
                date_str = datetime.now().strftime('%Y%m%d')
                
                # Get sequence number for today
                with get_db() as db:
                    today_samples = db.execute(
                        select(func.count(Sample.id))
                        .where(func.date(Sample.created_at) == datetime.now().date())
                    ).scalar()
                    
                    seq_num = (today_samples or 0) + 1
                
                qr_code_text = f"SR-{date_str}-{seq_num:04d}"
                
                # Prepare QR data
                qr_data = {
                    'sample_id': sample_id,
                    'qr_code': qr_code_text,
                    'service_request_id': sr_options[selected_sr].id,
                    'service_request_number': sr_options[selected_sr].request_number,
                    'client_name': sr_options[selected_sr].client_name,
                    'sample_type': sample_type,
                    'manufacturer': manufacturer,
                    'model': model,
                    'received_date': received_date.isoformat()
                }
                
                # Generate QR code image
                qr_generator = get_qr_generator()
                qr_string, qr_img_bytes = qr_generator.generate_qr_code(
                    data=json.dumps(qr_data),
                    entity_type='sample',
                    entity_id=hash(sample_id),
                    additional_data=qr_data,
                    save_to_db=True
                )
                
                # Save QR code image
                qr_dir = Path("static/qrcodes")
                qr_dir.mkdir(parents=True, exist_ok=True)
                qr_image_path = qr_dir / f"{qr_code_text}.png"
                
                with open(qr_image_path, 'wb') as f:
                    f.write(qr_img_bytes)
                
                # Save sample photos
                photo_paths = []
                if sample_photos:
                    photos_dir = Path("static/sample_photos")
                    photos_dir.mkdir(parents=True, exist_ok=True)
                    
                    for photo in sample_photos:
                        photo_path = photos_dir / f"{sample_id}_{photo.name}"
                        with open(photo_path, "wb") as f:
                            f.write(photo.getvalue())
                        photo_paths.append(str(photo_path))
                
                # Parse serial numbers
                serial_numbers_list = [s.strip() for s in serial_number.split(',') if s.strip()] if serial_number else []
                
                # Create sample record
                # Note: received_date is stored via created_at and in notes
                new_sample = Sample(
                    sample_id=sample_id,
                    qr_code=qr_code_text,
                    qr_code_image_path=str(qr_image_path),
                    qr_data=qr_data,
                    service_request_id=sr_options[selected_sr].id,
                    sample_type=sample_type,
                    manufacturer=manufacturer,
                    model_number=model,
                    serial_number=serial_numbers_list[0] if serial_numbers_list else None,
                    batch_number=batch_number,
                    status=SampleStatus.RECEIVED,
                    storage_location=storage_location,
                    current_location=storage_location,
                    notes=f"Condition: {condition}\nReceived: {received_date}\n{condition_notes}\n{notes}".strip(),
                    photos=photo_paths if photo_paths else None,
                    created_at=datetime.utcnow()
                )
                
                with get_db() as db:
                    db.add(new_sample)
                    db.flush()  # Get the ID
                    
                    # Create initial custody log entry
                    custody_entry = SampleStatusHistory(
                        sample_id=new_sample.id,
                        previous_status=None,
                        new_status=SampleStatus.RECEIVED.value,
                        new_location=storage_location,
                        changed_by_name=received_by,
                        change_source='manual',
                        reason='Initial receipt',
                        notes=f"Sample received from {sr_options[selected_sr].client_name}",
                        change_metadata=qr_data,
                        changed_at=datetime.utcnow()
                    )
                    db.add(custody_entry)
                    db.commit()
                    
                    # Store in session for display
                    st.session_state.last_sample = {
                        'sample_id': sample_id,
                        'qr_code': qr_code_text,
                        'qr_image': qr_img_bytes,
                        'service_request': sr_options[selected_sr].request_number
                    }
                
                st.success(f"✅ Sample registered successfully!")
                st.balloons()
                
                # Display QR code
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### 📋 Sample Information")
                    st.markdown(f"**Sample ID:** `{sample_id}`")
                    st.markdown(f"**QR Code:** `{qr_code_text}`")
                    st.markdown(f"**Type:** {sample_type}")
                    st.markdown(f"**Manufacturer:** {manufacturer}")
                    st.markdown(f"**Model:** {model}")
                    st.markdown(f"**Storage:** {storage_location}")
                
                with col2:
                    st.markdown("### 🏷️ QR Code Label")
                    st.image(qr_img_bytes, width=250)
                    
                    # Download QR code
                    st.download_button(
                        label="📥 Download QR Code",
                        data=qr_img_bytes,
                        file_name=f"{qr_code_text}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                    
                    # Generate PDF label
                    pdf_bytes = generate_qr_label_pdf(
                        sample_id=sample_id,
                        qr_code=qr_code_text,
                        qr_img_bytes=qr_img_bytes,
                        sample_type=sample_type,
                        manufacturer=manufacturer,
                        model=model
                    )
                    
                    st.download_button(
                        label="🖨️ Download PDF Label",
                        data=pdf_bytes,
                        file_name=f"{qr_code_text}_label.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                # Next steps
                with st.expander("📝 Next Steps"):
                    st.markdown("""
                    1. ✅ Sample registered with QR code
                    2. 📦 Store sample in designated location
                    3. 🏷️ Print and attach QR label to sample
                    4. 🔍 Sample is now trackable via QR code
                    5. ➡️ Proceed to Sample Allocation when ready
                    """)
                
            except Exception as e:
                st.error(f"❌ Error registering sample: {str(e)}")
                import traceback
                st.code(traceback.format_exc())


def generate_qr_label_pdf(sample_id, qr_code, qr_img_bytes, sample_type, manufacturer, model):
    """Generate printable PDF label with QR code"""
    
    buffer = io.BytesIO()
    
    # Create PDF (4x2 inch label)
    c = pdf_canvas.Canvas(buffer, pagesize=(4*inch, 2*inch))
    
    # Title
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.25*inch, 1.7*inch, "Sample Tracking Label")
    
    # QR Code
    # Save QR image to temp file for reportlab
    from PIL import Image
    qr_img = Image.open(io.BytesIO(qr_img_bytes))
    temp_qr_path = Path("/tmp") / f"{qr_code}_temp.png"
    qr_img.save(temp_qr_path)
    
    c.drawImage(str(temp_qr_path), 0.25*inch, 0.4*inch, width=1.2*inch, height=1.2*inch)
    
    # Sample info
    c.setFont("Helvetica", 9)
    y_pos = 1.4*inch
    c.drawString(1.6*inch, y_pos, f"QR: {qr_code}")
    y_pos -= 0.2*inch
    c.drawString(1.6*inch, y_pos, f"Sample: {sample_id}")
    y_pos -= 0.2*inch
    c.drawString(1.6*inch, y_pos, f"Type: {sample_type}")
    y_pos -= 0.2*inch
    c.setFont("Helvetica", 8)
    c.drawString(1.6*inch, y_pos, f"Mfg: {manufacturer[:20]}")
    y_pos -= 0.15*inch
    c.drawString(1.6*inch, y_pos, f"Model: {model[:20]}")
    
    # Footer
    c.setFont("Helvetica", 7)
    c.drawString(0.25*inch, 0.2*inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    c.save()
    
    # Clean up temp file
    if temp_qr_path.exists():
        temp_qr_path.unlink()
    
    return buffer.getvalue()


def render_view_samples():
    """Render sample tracking dashboard with search and filters"""
    
    st.markdown("### 🔍 Sample Tracking Dashboard")
    
    # Quick stats
    with get_db() as db:
        total_samples = db.execute(select(func.count(Sample.id))).scalar()
        today_samples = db.execute(
            select(func.count(Sample.id))
            .where(func.date(Sample.created_at) == datetime.now().date())
        ).scalar()
        pending_allocation = db.execute(
            select(func.count(Sample.id))
            .where(Sample.status == SampleStatus.RECEIVED)
        ).scalar()
        in_storage = db.execute(
            select(func.count(Sample.id))
            .where(Sample.status.in_([SampleStatus.RECEIVED, SampleStatus.INSPECTED]))
        ).scalar()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Samples", total_samples)
    col2.metric("Received Today", today_samples)
    col3.metric("Pending Allocation", pending_allocation)
    col4.metric("In Storage", in_storage)
    
    st.divider()
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        date_from = st.date_input(
            "Date From",
            value=None,
            help="Filter samples from this date"
        )
    
    with col2:
        date_to = st.date_input(
            "Date To",
            value=None,
            help="Filter samples until this date"
        )
    
    with col3:
        status_filter = st.selectbox(
            "Status",
            options=["All"] + [s.value for s in SampleStatus],
            help="Filter by sample status"
        )
    
    with col4:
        search_term = st.text_input(
            "Search",
            placeholder="QR code, Sample ID, or Client",
            help="Search samples"
        )
    
    # Get samples
    with get_db() as db:
        query = select(Sample).order_by(desc(Sample.created_at))
        
        # Apply filters
        conditions = []
        if date_from:
            conditions.append(func.date(Sample.created_at) >= date_from)
        if date_to:
            conditions.append(func.date(Sample.created_at) <= date_to)
        if status_filter != "All":
            conditions.append(Sample.status == status_filter)
        if search_term:
            conditions.append(
                or_(
                    Sample.qr_code.ilike(f"%{search_term}%"),
                    Sample.sample_id.ilike(f"%{search_term}%"),
                    Sample.manufacturer.ilike(f"%{search_term}%")
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        samples = db.execute(query.limit(50)).scalars().all()
        
        if not samples:
            st.info("No samples found")
            return
        
        st.markdown(f"### 📦 Found {len(samples)} sample(s)")
        
        # Display samples
        for sample in samples:
            # Status badge
            status_colors = {
                'received': '🟢',
                'inspected': '🔵',
                'allocated': '🟡',
                'in_test': '🟠',
                'completed': '✅',
                'rejected': '🔴'
            }
            status_badge = status_colors.get(sample.status.value if hasattr(sample.status, 'value') else sample.status, '⚪')
            
            with st.expander(
                f"{status_badge} {sample.qr_code} - {sample.sample_id} ({sample.sample_type})",
                expanded=False
            ):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown("#### 📋 Sample Details")
                    st.markdown(f"**Sample ID:** {sample.sample_id}")
                    st.markdown(f"**QR Code:** {sample.qr_code}")
                    st.markdown(f"**Type:** {sample.sample_type}")
                    st.markdown(f"**Manufacturer:** {sample.manufacturer}")
                    st.markdown(f"**Model:** {sample.model_number}")
                    if sample.serial_number:
                        st.markdown(f"**Serial:** {sample.serial_number}")
                    if sample.batch_number:
                        st.markdown(f"**Batch:** {sample.batch_number}")
                
                with col2:
                    st.markdown("#### 📍 Location & Status")
                    st.markdown(f"**Status:** {sample.status.value if hasattr(sample.status, 'value') else sample.status}")
                    st.markdown(f"**Storage:** {sample.storage_location or 'N/A'}")
                    st.markdown(f"**Current Location:** {sample.current_location or sample.storage_location or 'N/A'}")
                    st.markdown(f"**Received:** {sample.created_at.strftime('%Y-%m-%d %H:%M') if sample.created_at else 'N/A'}")
                
                with col3:
                    st.markdown("#### 🏷️ QR Code")
                    if sample.qr_code_image_path and Path(sample.qr_code_image_path).exists():
                        st.image(sample.qr_code_image_path, width=150)
                    else:
                        st.info("QR image not available")
                    
                    # Download QR
                    if sample.qr_code_image_path and Path(sample.qr_code_image_path).exists():
                        with open(sample.qr_code_image_path, 'rb') as f:
                            qr_bytes = f.read()
                        st.download_button(
                            label="📥 Download",
                            data=qr_bytes,
                            file_name=f"{sample.qr_code}.png",
                            mime="image/png",
                            key=f"dl_{sample.id}",
                            use_container_width=True
                        )
                
                # Notes
                if sample.notes:
                    st.markdown("**Notes:**")
                    st.text(sample.notes)
                
                # Photos
                if sample.photos:
                    st.markdown("**Photos:**")
                    photo_cols = st.columns(min(len(sample.photos), 4))
                    for idx, photo_path in enumerate(sample.photos[:4]):
                        if Path(photo_path).exists():
                            with photo_cols[idx]:
                                st.image(photo_path, width=120)


def render_chain_of_custody():
    """Render chain of custody tracking"""
    
    st.markdown("### 📝 Chain of Custody")
    st.markdown("Track sample movement and handling history")
    
    # Sample selection
    with get_db() as db:
        samples = db.execute(
            select(Sample)
            .options(load_only(
                Sample.id,
                Sample.sample_id,
                Sample.project_id,
                Sample.service_request_id,
                Sample.receipt_id,
                Sample.sample_type,
                Sample.manufacturer,
                Sample.model_number,
                Sample.serial_number,
                Sample.batch_number,
                Sample.qr_code,
                Sample.qr_code_image_path,
                Sample.status,
                Sample.current_location,
                Sample.storage_location,
                Sample.created_at,
                Sample.updated_at
            ))
            .order_by(Sample.created_at.desc())
            .limit(100)
        ).scalars().all()

        sample_options = {
            f"{s.qr_code} - {s.sample_id} ({s.sample_type})": s
            for s in samples
        }
    
    if not sample_options:
        st.info("No samples found")
        return
    
    selected_sample = st.selectbox(
        "Select Sample",
        options=["-- Select Sample --"] + list(sample_options.keys()),
        help="Choose a sample to view custody history"
    )
    
    if selected_sample and selected_sample != "-- Select Sample --":
        sample = sample_options[selected_sample]
        
        # Sample info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Sample ID", sample.sample_id)
            st.metric("QR Code", sample.qr_code)
        
        with col2:
            st.metric("Current Status", sample.status.value if hasattr(sample.status, 'value') else sample.status)
            st.metric("Current Location", sample.current_location or "Unknown")
        
        with col3:
            st.metric("Sample Type", sample.sample_type)
            st.metric("Manufacturer", sample.manufacturer)
        
        st.divider()
        
        # Add custody event
        with st.expander("➕ Add Custody Event", expanded=False):
            with st.form("add_custody_event"):
                col1, col2 = st.columns(2)
                
                with col1:
                    action = st.selectbox(
                        "Action",
                        options=["Moved", "Status Changed", "Allocated", "Tested", "Inspected", "Other"]
                    )
                    
                    new_location = st.text_input(
                        "New Location",
                        value=sample.current_location or ""
                    )
                
                with col2:
                    new_status = st.selectbox(
                        "New Status",
                        options=[s.value for s in SampleStatus],
                        index=[s.value for s in SampleStatus].index(sample.status.value if hasattr(sample.status, 'value') else sample.status)
                    )
                    
                    handled_by = st.text_input(
                        "Handled By",
                        value="Technician"
                    )
                
                notes = st.text_area(
                    "Notes",
                    placeholder="Describe the action taken..."
                )
                
                if st.form_submit_button("📝 Record Custody Event", type="primary"):
                    try:
                        with get_db() as db:
                            # Get current sample state
                            current_sample = db.execute(
                                select(Sample).where(Sample.id == sample.id)
                            ).scalar_one()
                            
                            # Create custody log entry
                            custody_entry = SampleStatusHistory(
                                sample_id=current_sample.id,
                                previous_status=current_sample.status.value if hasattr(current_sample.status, 'value') else current_sample.status,
                                new_status=new_status,
                                previous_location=current_sample.current_location,
                                new_location=new_location,
                                changed_by_name=handled_by,
                                change_source='manual',
                                reason=action,
                                notes=notes,
                                changed_at=datetime.utcnow()
                            )
                            db.add(custody_entry)
                            
                            # Update sample
                            current_sample.status = new_status
                            current_sample.current_location = new_location
                            current_sample.updated_at = datetime.utcnow()
                            
                            db.commit()
                            
                            st.success("✅ Custody event recorded!")
                            st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        st.divider()
        
        # Custody history timeline
        st.markdown("### 📜 Custody History Timeline")
        
        with get_db() as db:
            history = db.execute(
                select(SampleStatusHistory)
                .where(SampleStatusHistory.sample_id == sample.id)
                .order_by(desc(SampleStatusHistory.changed_at))
            ).scalars().all()
            
            if not history:
                st.info("No custody history available")
            else:
                for entry in history:
                    with st.container():
                        col1, col2 = st.columns([1, 4])
                        
                        with col1:
                            st.markdown(f"**{entry.changed_at.strftime('%Y-%m-%d')}**")
                            st.caption(entry.changed_at.strftime('%H:%M:%S'))
                        
                        with col2:
                            # Action badge
                            if entry.reason:
                                st.markdown(f"**🔹 {entry.reason}**")
                            
                            # Status change
                            if entry.previous_status != entry.new_status:
                                st.markdown(f"Status: `{entry.previous_status}` → `{entry.new_status}`")
                            
                            # Location change
                            if entry.previous_location != entry.new_location:
                                st.markdown(f"Location: `{entry.previous_location or 'Unknown'}` → `{entry.new_location or 'Unknown'}`")
                            
                            # Handler
                            if entry.changed_by_name:
                                st.caption(f"👤 Handled by: {entry.changed_by_name}")
                            
                            # Notes
                            if entry.notes:
                                st.caption(f"📝 {entry.notes}")
                        
                        st.divider()


if __name__ == "__main__":
    main()
