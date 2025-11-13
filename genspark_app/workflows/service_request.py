"""
Service Request Workflow

Manages the initial customer service request and quote generation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)


class ServiceRequestWorkflow:
    """Workflow for managing service requests"""

    def __init__(self, db_session=None):
        """
        Initialize service request workflow

        Args:
            db_session: Database session for persistence
        """
        self.db_session = db_session
        self.current_request = None

    def create_request(
        self,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        customer_company: Optional[str] = None,
        customer_address: Optional[str] = None,
        required_date: Optional[date] = None,
        priority: str = 'normal',
        notes: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new service request

        Args:
            customer_name: Customer name
            customer_email: Customer email
            customer_phone: Customer phone
            customer_company: Customer company (optional)
            customer_address: Customer address (optional)
            required_date: Required completion date (optional)
            priority: Priority level (low, normal, high, urgent)
            notes: Additional notes (optional)
            created_by: User ID who created the request

        Returns:
            Service request object
        """
        try:
            request_number = self._generate_request_number()

            service_request = {
                'id': str(uuid4()),
                'request_number': request_number,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'customer_phone': customer_phone,
                'customer_company': customer_company,
                'customer_address': customer_address,
                'request_date': date.today(),
                'required_date': required_date,
                'status': 'pending',
                'priority': priority,
                'notes': notes,
                'created_by': created_by,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'protocols': []
            }

            self.current_request = service_request
            logger.info(f"Created service request: {request_number}")

            # In production: save to database
            if self.db_session:
                self._persist_request(service_request)

            return service_request

        except Exception as e:
            logger.error(f"Failed to create service request: {e}")
            return {}

    def add_protocol(
        self,
        protocol_id: str,
        protocol_name: str,
        quantity: int = 1,
        unit_price: Optional[float] = None
    ) -> bool:
        """
        Add a protocol to the service request

        Args:
            protocol_id: Protocol identifier (e.g., 'STC-001')
            protocol_name: Protocol name
            quantity: Number of tests
            unit_price: Price per test (optional)

        Returns:
            Success status
        """
        try:
            if not self.current_request:
                logger.error("No active service request")
                return False

            protocol_item = {
                'protocol_id': protocol_id,
                'protocol_name': protocol_name,
                'quantity': quantity,
                'unit_price': unit_price or self._get_protocol_price(protocol_id),
                'total_price': (unit_price or self._get_protocol_price(protocol_id)) * quantity
            }

            self.current_request['protocols'].append(protocol_item)
            logger.info(f"Added protocol {protocol_id} to service request")

            return True

        except Exception as e:
            logger.error(f"Failed to add protocol: {e}")
            return False

    def remove_protocol(self, protocol_id: str) -> bool:
        """Remove a protocol from the service request"""
        try:
            if not self.current_request:
                return False

            self.current_request['protocols'] = [
                p for p in self.current_request['protocols']
                if p['protocol_id'] != protocol_id
            ]

            logger.info(f"Removed protocol {protocol_id} from service request")
            return True

        except Exception as e:
            logger.error(f"Failed to remove protocol: {e}")
            return False

    def calculate_quote(self) -> Dict[str, Any]:
        """
        Calculate quote for the service request

        Returns:
            Quote details with breakdown
        """
        try:
            if not self.current_request:
                logger.error("No active service request")
                return {}

            protocols = self.current_request.get('protocols', [])

            subtotal = sum(item['total_price'] for item in protocols)
            tax_rate = 0.10  # 10% tax (configurable)
            tax = subtotal * tax_rate
            total = subtotal + tax

            quote = {
                'request_number': self.current_request['request_number'],
                'quote_date': datetime.utcnow().isoformat(),
                'protocols': protocols,
                'subtotal': subtotal,
                'tax_rate': tax_rate,
                'tax': tax,
                'total': total,
                'currency': 'USD',
                'validity_days': 30
            }

            self.current_request['total_quote'] = total
            self.current_request['status'] = 'quoted'

            logger.info(f"Generated quote: ${total:.2f}")
            return quote

        except Exception as e:
            logger.error(f"Failed to calculate quote: {e}")
            return {}

    def approve_request(self, approved_by: str) -> bool:
        """
        Approve the service request

        Args:
            approved_by: User ID who approved the request

        Returns:
            Success status
        """
        try:
            if not self.current_request:
                return False

            self.current_request['status'] = 'approved'
            self.current_request['approved_by'] = approved_by
            self.current_request['approved_at'] = datetime.utcnow()
            self.current_request['updated_at'] = datetime.utcnow()

            logger.info(f"Approved service request: {self.current_request['request_number']}")

            # In production: update database
            if self.db_session:
                self._persist_request(self.current_request)

            return True

        except Exception as e:
            logger.error(f"Failed to approve request: {e}")
            return False

    def reject_request(self, rejected_by: str, reason: str) -> bool:
        """
        Reject the service request

        Args:
            rejected_by: User ID who rejected the request
            reason: Rejection reason

        Returns:
            Success status
        """
        try:
            if not self.current_request:
                return False

            self.current_request['status'] = 'cancelled'
            self.current_request['rejected_by'] = rejected_by
            self.current_request['rejection_reason'] = reason
            self.current_request['updated_at'] = datetime.utcnow()

            logger.info(f"Rejected service request: {self.current_request['request_number']}")

            # In production: update database
            if self.db_session:
                self._persist_request(self.current_request)

            return True

        except Exception as e:
            logger.error(f"Failed to reject request: {e}")
            return False

    def get_request_summary(self) -> Dict[str, Any]:
        """Get summary of current service request"""
        if not self.current_request:
            return {}

        return {
            'request_number': self.current_request.get('request_number'),
            'customer': self.current_request.get('customer_name'),
            'status': self.current_request.get('status'),
            'protocols_count': len(self.current_request.get('protocols', [])),
            'total_quote': self.current_request.get('total_quote'),
            'created_at': self.current_request.get('created_at')
        }

    def _generate_request_number(self) -> str:
        """Generate unique request number"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"SR-{timestamp}"

    def _get_protocol_price(self, protocol_id: str) -> float:
        """Get protocol price (placeholder - should come from database/config)"""
        # Price lookup table (in production, this would be from database)
        price_table = {
            'STC-001': 500.0,
            'NOCT-001': 750.0,
            'LID-001': 1200.0,
            'PID-001': 1500.0,
            'TC-001': 3000.0,
            'DH-001': 5000.0,
            # ... add all 54 protocols
        }
        return price_table.get(protocol_id, 1000.0)  # Default $1000

    def _persist_request(self, service_request: Dict[str, Any]):
        """Persist service request to database"""
        # In production: save to database using SQLAlchemy
        pass
