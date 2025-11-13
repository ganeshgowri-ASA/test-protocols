"""
Equipment Booking Workflow

Manages equipment scheduling, booking, and resource allocation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)


class EquipmentBookingWorkflow:
    """Workflow for equipment booking and scheduling"""

    def __init__(self, db_session=None):
        """Initialize equipment booking workflow"""
        self.db_session = db_session
        self.current_booking = None

    def check_availability(
        self,
        equipment_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """
        Check equipment availability for a time period

        Args:
            equipment_id: Equipment identifier
            start_time: Requested start time
            end_time: Requested end time

        Returns:
            Availability information
        """
        try:
            # In production: query database for existing bookings
            existing_bookings = self._get_existing_bookings(equipment_id, start_time, end_time)

            is_available = len(existing_bookings) == 0

            availability = {
                'equipment_id': equipment_id,
                'requested_start': start_time.isoformat(),
                'requested_end': end_time.isoformat(),
                'is_available': is_available,
                'conflicts': existing_bookings,
                'next_available_slot': self._find_next_available(equipment_id, start_time) if not is_available else None
            }

            return availability

        except Exception as e:
            logger.error(f"Failed to check availability: {e}")
            return {'is_available': False, 'error': str(e)}

    def create_booking(
        self,
        equipment_id: str,
        test_execution_id: str,
        start_time: datetime,
        end_time: datetime,
        booked_by: str,
        purpose: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create equipment booking

        Args:
            equipment_id: Equipment identifier
            test_execution_id: Associated test execution
            start_time: Booking start time
            end_time: Booking end time
            booked_by: User ID who made the booking
            purpose: Purpose of booking
            notes: Additional notes

        Returns:
            Booking object
        """
        try:
            # Check availability first
            availability = self.check_availability(equipment_id, start_time, end_time)
            if not availability['is_available']:
                logger.warning(f"Equipment {equipment_id} not available for requested time")
                return {'error': 'Equipment not available', 'conflicts': availability['conflicts']}

            booking = {
                'id': str(uuid4()),
                'equipment_id': equipment_id,
                'test_execution_id': test_execution_id,
                'start_time': start_time,
                'end_time': end_time,
                'booked_by': booked_by,
                'status': 'scheduled',
                'purpose': purpose,
                'notes': notes,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }

            self.current_booking = booking
            logger.info(f"Created booking for equipment {equipment_id}")

            # In production: save to database
            if self.db_session:
                self._persist_booking(booking)

            return booking

        except Exception as e:
            logger.error(f"Failed to create booking: {e}")
            return {'error': str(e)}

    def update_booking(
        self,
        booking_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update existing booking

        Args:
            booking_id: Booking identifier
            start_time: New start time (optional)
            end_time: New end time (optional)
            status: New status (optional)
            notes: Additional notes (optional)

        Returns:
            Success status
        """
        try:
            booking = self._get_booking(booking_id)
            if not booking:
                logger.error(f"Booking not found: {booking_id}")
                return False

            # If times are being changed, check for conflicts
            if start_time or end_time:
                new_start = start_time or booking['start_time']
                new_end = end_time or booking['end_time']

                availability = self.check_availability(
                    booking['equipment_id'],
                    new_start,
                    new_end
                )

                # Exclude current booking from conflict check
                conflicts = [c for c in availability.get('conflicts', []) if c['id'] != booking_id]

                if conflicts:
                    logger.warning("Booking update would create conflicts")
                    return False

                booking['start_time'] = new_start
                booking['end_time'] = new_end

            if status:
                booking['status'] = status

            if notes:
                if 'notes' not in booking:
                    booking['notes'] = ''
                booking['notes'] += f"\n[{datetime.utcnow().isoformat()}] {notes}"

            booking['updated_at'] = datetime.utcnow()

            logger.info(f"Updated booking: {booking_id}")

            # In production: update database
            if self.db_session:
                self._persist_booking(booking)

            return True

        except Exception as e:
            logger.error(f"Failed to update booking: {e}")
            return False

    def cancel_booking(self, booking_id: str, reason: str) -> bool:
        """
        Cancel an existing booking

        Args:
            booking_id: Booking identifier
            reason: Cancellation reason

        Returns:
            Success status
        """
        try:
            return self.update_booking(
                booking_id,
                status='cancelled',
                notes=f"Cancelled: {reason}"
            )

        except Exception as e:
            logger.error(f"Failed to cancel booking: {e}")
            return False

    def start_booking(self, booking_id: str) -> bool:
        """Mark booking as in progress"""
        try:
            return self.update_booking(booking_id, status='in_progress')

        except Exception as e:
            logger.error(f"Failed to start booking: {e}")
            return False

    def complete_booking(self, booking_id: str) -> bool:
        """Mark booking as completed"""
        try:
            return self.update_booking(booking_id, status='completed')

        except Exception as e:
            logger.error(f"Failed to complete booking: {e}")
            return False

    def get_equipment_schedule(
        self,
        equipment_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get equipment schedule for a date range

        Args:
            equipment_id: Equipment identifier
            start_date: Start date for schedule
            end_date: End date for schedule

        Returns:
            List of bookings
        """
        try:
            bookings = self._get_existing_bookings(equipment_id, start_date, end_date)

            schedule = {
                'equipment_id': equipment_id,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'bookings': bookings,
                'available_slots': self._calculate_available_slots(equipment_id, start_date, end_date)
            }

            return schedule

        except Exception as e:
            logger.error(f"Failed to get schedule: {e}")
            return []

    def check_maintenance_schedule(self, equipment_id: str) -> Dict[str, Any]:
        """
        Check equipment maintenance schedule

        Args:
            equipment_id: Equipment identifier

        Returns:
            Maintenance information
        """
        try:
            # In production: query equipment maintenance records
            equipment_info = self._get_equipment_info(equipment_id)

            maintenance_info = {
                'equipment_id': equipment_id,
                'last_maintenance': equipment_info.get('last_maintenance_date'),
                'next_maintenance_due': equipment_info.get('next_maintenance_date'),
                'maintenance_interval': equipment_info.get('maintenance_interval'),
                'is_due_for_maintenance': self._is_maintenance_due(equipment_info),
                'days_until_maintenance': self._days_until_maintenance(equipment_info)
            }

            return maintenance_info

        except Exception as e:
            logger.error(f"Failed to check maintenance schedule: {e}")
            return {}

    def check_calibration_status(self, equipment_id: str) -> Dict[str, Any]:
        """
        Check equipment calibration status

        Args:
            equipment_id: Equipment identifier

        Returns:
            Calibration information
        """
        try:
            equipment_info = self._get_equipment_info(equipment_id)

            calibration_info = {
                'equipment_id': equipment_id,
                'last_calibration': equipment_info.get('last_calibration_date'),
                'calibration_due_date': equipment_info.get('calibration_due_date'),
                'calibration_interval': equipment_info.get('calibration_interval'),
                'is_calibration_valid': self._is_calibration_valid(equipment_info),
                'days_until_due': self._days_until_calibration_due(equipment_info)
            }

            return calibration_info

        except Exception as e:
            logger.error(f"Failed to check calibration status: {e}")
            return {}

    def _get_existing_bookings(
        self,
        equipment_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Get existing bookings for equipment in time range"""
        # In production: query database
        # Placeholder implementation
        return []

    def _find_next_available(self, equipment_id: str, after_time: datetime) -> Optional[datetime]:
        """Find next available time slot"""
        # In production: calculate based on existing bookings
        return after_time + timedelta(hours=2)

    def _calculate_available_slots(
        self,
        equipment_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Calculate available time slots"""
        # In production: calculate based on working hours and existing bookings
        return []

    def _get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Get booking by ID"""
        # In production: query database
        return self.current_booking if self.current_booking and self.current_booking.get('id') == booking_id else None

    def _get_equipment_info(self, equipment_id: str) -> Dict[str, Any]:
        """Get equipment information"""
        # In production: query database
        return {}

    def _is_maintenance_due(self, equipment_info: Dict[str, Any]) -> bool:
        """Check if maintenance is due"""
        due_date = equipment_info.get('next_maintenance_date')
        if not due_date:
            return False
        return datetime.now() >= due_date

    def _days_until_maintenance(self, equipment_info: Dict[str, Any]) -> Optional[int]:
        """Calculate days until maintenance due"""
        due_date = equipment_info.get('next_maintenance_date')
        if not due_date:
            return None
        delta = due_date - datetime.now()
        return delta.days

    def _is_calibration_valid(self, equipment_info: Dict[str, Any]) -> bool:
        """Check if calibration is still valid"""
        due_date = equipment_info.get('calibration_due_date')
        if not due_date:
            return False
        return datetime.now() < due_date

    def _days_until_calibration_due(self, equipment_info: Dict[str, Any]) -> Optional[int]:
        """Calculate days until calibration due"""
        due_date = equipment_info.get('calibration_due_date')
        if not due_date:
            return None
        delta = due_date - datetime.now()
        return delta.days

    def _persist_booking(self, booking: Dict[str, Any]):
        """Persist booking to database"""
        # In production: save using SQLAlchemy
        pass
