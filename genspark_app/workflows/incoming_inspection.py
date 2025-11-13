"""
Incoming Inspection Workflow

Manages sample reception, inspection, and storage assignment
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date
import logging
from uuid import uuid4
import qrcode
import barcode
from barcode.writer import ImageWriter

logger = logging.getLogger(__name__)


class IncomingInspectionWorkflow:
    """Workflow for incoming sample inspection"""

    def __init__(self, db_session=None):
        """Initialize incoming inspection workflow"""
        self.db_session = db_session
        self.current_sample = None

    def receive_sample(
        self,
        service_request_id: str,
        manufacturer: str,
        model: str,
        serial_number: Optional[str] = None,
        technology: Optional[str] = None,
        rated_power: Optional[float] = None,
        received_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Receive and register a new sample

        Args:
            service_request_id: Associated service request
            manufacturer: Module manufacturer
            model: Module model
            serial_number: Serial number (if available)
            technology: Cell technology (mono-Si, poly-Si, etc.)
            rated_power: Rated power in Watts
            received_by: User ID who received the sample

        Returns:
            Sample object
        """
        try:
            sample_id = self._generate_sample_id()

            sample = {
                'id': str(uuid4()),
                'sample_id': sample_id,
                'service_request_id': service_request_id,
                'manufacturer': manufacturer,
                'model': model,
                'serial_number': serial_number,
                'technology': technology,
                'rated_power': rated_power,
                'reception_date': date.today(),
                'condition': 'good',  # Default, will be updated during inspection
                'photos': [],
                'inspection_notes': '',
                'inspected_by': received_by,
                'inspected_at': datetime.utcnow(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }

            self.current_sample = sample
            logger.info(f"Received sample: {sample_id}")

            return sample

        except Exception as e:
            logger.error(f"Failed to receive sample: {e}")
            return {}

    def perform_visual_inspection(
        self,
        inspection_checklist: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform visual inspection of the sample

        Args:
            inspection_checklist: Dictionary with inspection results

        Returns:
            Inspection results
        """
        try:
            if not self.current_sample:
                logger.error("No active sample for inspection")
                return {}

            inspection_results = {
                'timestamp': datetime.utcnow().isoformat(),
                'glass_condition': inspection_checklist.get('glass_condition', 'good'),
                'frame_condition': inspection_checklist.get('frame_condition', 'good'),
                'junction_box_condition': inspection_checklist.get('junction_box_condition', 'good'),
                'cable_condition': inspection_checklist.get('cable_condition', 'good'),
                'connector_condition': inspection_checklist.get('connector_condition', 'good'),
                'visible_cracks': inspection_checklist.get('visible_cracks', False),
                'visible_delamination': inspection_checklist.get('visible_delamination', False),
                'visible_discoloration': inspection_checklist.get('visible_discoloration', False),
                'physical_damage': inspection_checklist.get('physical_damage', False),
                'overall_condition': self._determine_overall_condition(inspection_checklist)
            }

            self.current_sample['condition'] = inspection_results['overall_condition']
            self.current_sample['inspection_results'] = inspection_results

            logger.info(f"Visual inspection completed for {self.current_sample['sample_id']}")

            return inspection_results

        except Exception as e:
            logger.error(f"Visual inspection failed: {e}")
            return {}

    def measure_dimensions(
        self,
        length: float,
        width: float,
        height: float,
        weight: float
    ) -> bool:
        """
        Record physical dimensions and weight

        Args:
            length: Length in mm
            width: Width in mm
            height: Height in mm
            weight: Weight in kg

        Returns:
            Success status
        """
        try:
            if not self.current_sample:
                return False

            self.current_sample['dimensions_length'] = length
            self.current_sample['dimensions_width'] = width
            self.current_sample['dimensions_height'] = height
            self.current_sample['weight'] = weight

            logger.info(f"Dimensions recorded: {length}x{width}x{height} mm, {weight} kg")

            return True

        except Exception as e:
            logger.error(f"Failed to record dimensions: {e}")
            return False

    def capture_photos(self, photo_paths: List[str]) -> bool:
        """
        Associate photos with the sample

        Args:
            photo_paths: List of photo file paths

        Returns:
            Success status
        """
        try:
            if not self.current_sample:
                return False

            if 'photos' not in self.current_sample:
                self.current_sample['photos'] = []

            for photo_path in photo_paths:
                self.current_sample['photos'].append({
                    'path': photo_path,
                    'timestamp': datetime.utcnow().isoformat(),
                    'description': ''
                })

            logger.info(f"Added {len(photo_paths)} photos to sample")

            return True

        except Exception as e:
            logger.error(f"Failed to capture photos: {e}")
            return False

    def generate_barcode(self) -> str:
        """
        Generate barcode for the sample

        Returns:
            Barcode image path
        """
        try:
            if not self.current_sample:
                return ""

            sample_id = self.current_sample['sample_id']

            # Generate Code 128 barcode
            code128 = barcode.get_barcode_class('code128')
            barcode_obj = code128(sample_id, writer=ImageWriter())

            barcode_path = f"barcodes/{sample_id}"
            barcode_obj.save(barcode_path)

            self.current_sample['barcode'] = f"{barcode_path}.png"

            logger.info(f"Generated barcode for {sample_id}")

            return f"{barcode_path}.png"

        except Exception as e:
            logger.error(f"Failed to generate barcode: {e}")
            return ""

    def generate_qr_code(self) -> str:
        """
        Generate QR code for the sample

        Returns:
            QR code image path
        """
        try:
            if not self.current_sample:
                return ""

            sample_id = self.current_sample['sample_id']

            # Generate QR code with sample information
            qr_data = {
                'sample_id': sample_id,
                'manufacturer': self.current_sample.get('manufacturer'),
                'model': self.current_sample.get('model'),
                'serial_number': self.current_sample.get('serial_number'),
                'reception_date': str(self.current_sample.get('reception_date'))
            }

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(str(qr_data))
            qr.make(fit=True)

            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_path = f"qrcodes/{sample_id}.png"
            qr_img.save(qr_path)

            self.current_sample['qr_code'] = qr_path

            logger.info(f"Generated QR code for {sample_id}")

            return qr_path

        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}")
            return ""

    def assign_storage_location(self, location: str) -> bool:
        """
        Assign storage location to the sample

        Args:
            location: Storage location identifier

        Returns:
            Success status
        """
        try:
            if not self.current_sample:
                return False

            self.current_sample['storage_location'] = location
            logger.info(f"Assigned storage location: {location}")

            return True

        except Exception as e:
            logger.error(f"Failed to assign storage location: {e}")
            return False

    def add_inspection_notes(self, notes: str) -> bool:
        """Add inspection notes"""
        try:
            if not self.current_sample:
                return False

            if 'inspection_notes' not in self.current_sample:
                self.current_sample['inspection_notes'] = ''

            self.current_sample['inspection_notes'] += f"\n[{datetime.utcnow().isoformat()}] {notes}"

            return True

        except Exception as e:
            logger.error(f"Failed to add notes: {e}")
            return False

    def complete_inspection(self) -> Dict[str, Any]:
        """
        Complete the inspection process

        Returns:
            Final sample record
        """
        try:
            if not self.current_sample:
                return {}

            self.current_sample['inspection_complete'] = True
            self.current_sample['updated_at'] = datetime.utcnow()

            logger.info(f"Inspection completed for {self.current_sample['sample_id']}")

            # In production: save to database
            if self.db_session:
                self._persist_sample(self.current_sample)

            return self.current_sample

        except Exception as e:
            logger.error(f"Failed to complete inspection: {e}")
            return {}

    def _generate_sample_id(self) -> str:
        """Generate unique sample ID"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"SMP-{timestamp}"

    def _determine_overall_condition(self, checklist: Dict[str, Any]) -> str:
        """Determine overall condition from checklist"""
        if checklist.get('physical_damage', False):
            return 'damaged'
        elif (checklist.get('visible_cracks', False) or
              checklist.get('visible_delamination', False)):
            return 'fair'
        elif checklist.get('visible_discoloration', False):
            return 'good'
        else:
            return 'excellent'

    def _persist_sample(self, sample: Dict[str, Any]):
        """Persist sample to database"""
        # In production: save using SQLAlchemy
        pass
