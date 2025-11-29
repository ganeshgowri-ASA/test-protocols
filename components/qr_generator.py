"""
QR Code Generator - Generate and manage QR codes for samples and equipment
=========================================================================
"""

import qrcode
import io
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json
import streamlit as st

from config.settings import config, STATIC_DIR
from config.database import get_db
from database.models import QRCode


class QRCodeGenerator:
    """QR Code generation and management"""

    def __init__(self):
        self.qr_storage_path = STATIC_DIR / "qrcodes"
        self.qr_storage_path.mkdir(parents=True, exist_ok=True)

    def generate_qr_code(
        self,
        data: str,
        entity_type: str,
        entity_id: int,
        additional_data: Dict[str, Any] = None,
        save_to_db: bool = True
    ) -> tuple[str, bytes]:
        """
        Generate QR code

        Args:
            data: Data to encode in QR code
            entity_type: Type of entity (sample, equipment, etc.)
            entity_id: ID of entity
            additional_data: Additional data to store
            save_to_db: Whether to save to database

        Returns:
            Tuple of (qr_code_string, image_bytes)
        """
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        # Add data
        qr.add_data(data)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{entity_type}_{entity_id}_{timestamp}.png"
        file_path = self.qr_storage_path / filename

        with open(file_path, 'wb') as f:
            f.write(img_bytes)

        # Save to database
        if save_to_db:
            try:
                with get_db() as db:
                    qr_record = QRCode(
                        qr_code=data,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        data=additional_data,
                        qr_image_path=str(file_path),
                        is_active=True,
                        generated_at=datetime.utcnow()
                    )
                    db.add(qr_record)
                    db.commit()
            except Exception as e:
                print(f"Error saving QR code to database: {e}")

        return data, img_bytes

    def generate_sample_qr_code(
        self,
        sample_id: str,
        service_request_number: str,
        additional_info: Dict[str, Any] = None
    ) -> tuple[str, bytes]:
        """
        Generate QR code for a sample

        Args:
            sample_id: Sample identifier
            service_request_number: Service request number
            additional_info: Additional sample information

        Returns:
            Tuple of (qr_code_string, image_bytes)
        """
        # Construct QR code data
        qr_data = {
            'type': 'sample',
            'sample_id': sample_id,
            'service_request': service_request_number,
            'generated_at': datetime.now().isoformat(),
            'url': f"{config.APP_NAME}/sample/{sample_id}"
        }

        if additional_info:
            qr_data.update(additional_info)

        # Convert to JSON string
        qr_string = json.dumps(qr_data)

        return self.generate_qr_code(
            data=qr_string,
            entity_type='sample',
            entity_id=hash(sample_id),  # Use hash as entity_id
            additional_data=qr_data
        )

    def generate_equipment_qr_code(
        self,
        equipment_code: str,
        equipment_name: str,
        additional_info: Dict[str, Any] = None
    ) -> tuple[str, bytes]:
        """
        Generate QR code for equipment

        Args:
            equipment_code: Equipment code
            equipment_name: Equipment name
            additional_info: Additional equipment information

        Returns:
            Tuple of (qr_code_string, image_bytes)
        """
        qr_data = {
            'type': 'equipment',
            'equipment_code': equipment_code,
            'equipment_name': equipment_name,
            'generated_at': datetime.now().isoformat(),
            'url': f"{config.APP_NAME}/equipment/{equipment_code}"
        }

        if additional_info:
            qr_data.update(additional_info)

        qr_string = json.dumps(qr_data)

        return self.generate_qr_code(
            data=qr_string,
            entity_type='equipment',
            entity_id=hash(equipment_code),
            additional_data=qr_data
        )

    def get_qr_code_image_base64(self, img_bytes: bytes) -> str:
        """
        Convert QR code image bytes to base64 string for display

        Args:
            img_bytes: Image bytes

        Returns:
            Base64 encoded string
        """
        return base64.b64encode(img_bytes).decode()

    def lookup_qr_code(self, qr_code_string: str) -> Optional[Dict[str, Any]]:
        """
        Look up QR code in database

        Args:
            qr_code_string: QR code data string

        Returns:
            QR code information dictionary or None
        """
        try:
            with get_db() as db:
                qr_record = db.query(QRCode).filter(
                    QRCode.qr_code == qr_code_string,
                    QRCode.is_active == True
                ).first()

                if qr_record:
                    # Update scan tracking
                    qr_record.last_scanned_at = datetime.utcnow()
                    qr_record.scan_count = (qr_record.scan_count or 0) + 1

                    if not qr_record.first_scanned_at:
                        qr_record.first_scanned_at = datetime.utcnow()

                    db.commit()

                    return {
                        'id': qr_record.id,
                        'entity_type': qr_record.entity_type,
                        'entity_id': qr_record.entity_id,
                        'data': qr_record.data,
                        'scan_count': qr_record.scan_count,
                        'generated_at': qr_record.generated_at
                    }

        except Exception as e:
            print(f"Error looking up QR code: {e}")

        return None


# Global QR generator instance
_qr_generator = None


def get_qr_generator() -> QRCodeGenerator:
    """Get global QR generator instance"""
    global _qr_generator

    if _qr_generator is None:
        _qr_generator = QRCodeGenerator()

    return _qr_generator


def render_qr_code_display(img_bytes: bytes, caption: str = "QR Code"):
    """
    Render QR code in Streamlit

    Args:
        img_bytes: QR code image bytes
        caption: Caption for the image
    """
    st.image(img_bytes, caption=caption, width=300)


def render_qr_code_generator_ui(
    entity_type: str,
    entity_id: str,
    entity_name: str
):
    """
    Render QR code generator UI

    Args:
        entity_type: Type of entity (sample, equipment)
        entity_id: Entity identifier
        entity_name: Entity name/label
    """
    st.markdown("### 📱 QR Code Generator")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.text_input("Entity ID", value=entity_id, disabled=True)
        st.text_input("Entity Name", value=entity_name, disabled=True)

        if st.button("Generate QR Code", type="primary"):
            generator = get_qr_generator()

            if entity_type == "sample":
                qr_string, img_bytes = generator.generate_sample_qr_code(
                    sample_id=entity_id,
                    service_request_number="SR-DEMO",
                    additional_info={'name': entity_name}
                )
            elif entity_type == "equipment":
                qr_string, img_bytes = generator.generate_equipment_qr_code(
                    equipment_code=entity_id,
                    equipment_name=entity_name
                )
            else:
                st.error("Invalid entity type")
                return

            # Store in session state
            st.session_state.generated_qr = {
                'string': qr_string,
                'image': img_bytes
            }

            st.success("QR Code generated successfully!")
            st.rerun()

    with col2:
        if 'generated_qr' in st.session_state:
            render_qr_code_display(
                st.session_state.generated_qr['image'],
                caption=f"{entity_type.title()} QR Code"
            )

            # Download button
            st.download_button(
                label="📥 Download QR Code",
                data=st.session_state.generated_qr['image'],
                file_name=f"{entity_type}_{entity_id}_qr.png",
                mime="image/png"
            )


def render_qr_scanner_ui():
    """
    Render QR code scanner UI

    Note: Actual scanning requires camera access via additional libraries
    This is a placeholder for manual QR code lookup
    """
    st.markdown("### 📷 QR Code Scanner")

    st.info("📱 Scan QR code with your device camera or enter QR code data manually")

    qr_input = st.text_area(
        "QR Code Data",
        placeholder="Paste QR code data here...",
        height=100
    )

    if st.button("Look Up QR Code"):
        if qr_input:
            generator = get_qr_generator()
            result = generator.lookup_qr_code(qr_input)

            if result:
                st.success("✅ QR Code found!")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Entity Type:**")
                    st.text(result['entity_type'].title())

                    st.markdown("**Entity ID:**")
                    st.text(result['entity_id'])

                with col2:
                    st.markdown("**Scan Count:**")
                    st.text(result['scan_count'])

                    st.markdown("**Generated:**")
                    st.text(result['generated_at'].strftime("%Y-%m-%d %H:%M"))

                if result['data']:
                    st.markdown("**Additional Data:**")
                    st.json(result['data'])

            else:
                st.error("❌ QR Code not found in database")
        else:
            st.warning("Please enter QR code data")


def create_qr_code_with_logo(
    data: str,
    logo_path: Optional[Path] = None
) -> bytes:
    """
    Create QR code with embedded logo

    Args:
        data: Data to encode
        logo_path: Path to logo image (optional)

    Returns:
        QR code image bytes
    """
    from PIL import Image

    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for logo
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Add logo if provided
    if logo_path and logo_path.exists():
        logo = Image.open(logo_path)

        # Calculate logo size (10% of QR code)
        qr_width, qr_height = img.size
        logo_size = int(qr_width * 0.1)

        # Resize logo
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        # Calculate position (center)
        logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)

        # Paste logo
        img.paste(logo, logo_pos)

    # Convert to bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')

    return img_buffer.getvalue()
