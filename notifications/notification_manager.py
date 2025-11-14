"""
Notification system for real-time alerts and warnings
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from models.protocol import Protocol, Equipment, Notification, ProtocolStatus, QCResult
import uuid


class NotificationManager:
    """Manage notifications and alerts"""

    def __init__(self, enable_notifications: bool = True):
        self.enable_notifications = enable_notifications
        self.notifications: List[Notification] = []

    def check_and_generate_notifications(self,
                                        protocols: List[Protocol],
                                        equipment: List[Equipment]) -> List[Notification]:
        """Check conditions and generate notifications"""

        if not self.enable_notifications:
            return []

        new_notifications = []

        # Check for QC failures
        new_notifications.extend(self._check_qc_failures(protocols))

        # Check for overdue protocols
        new_notifications.extend(self._check_overdue_protocols(protocols))

        # Check for equipment calibration
        new_notifications.extend(self._check_equipment_calibration(equipment))

        # Check for equipment offline
        new_notifications.extend(self._check_equipment_status(equipment))

        # Check for protocol completion
        new_notifications.extend(self._check_protocol_completion(protocols))

        self.notifications.extend(new_notifications)

        return new_notifications

    def _check_qc_failures(self, protocols: List[Protocol]) -> List[Notification]:
        """Check for QC failures"""
        notifications = []

        for protocol in protocols:
            if protocol.qc_result == QCResult.FAIL and protocol.status == ProtocolStatus.COMPLETED:
                # Check if notification already exists for this protocol
                if not any(n.related_entity_id == protocol.protocol_id for n in self.notifications):
                    notifications.append(Notification(
                        notification_id=str(uuid.uuid4()),
                        notification_type='alert',
                        title='QC Failure Detected',
                        message=f'Protocol {protocol.protocol_id} ({protocol.protocol_name}) failed QC check. NC Number: {protocol.nc_number}',
                        created_at=datetime.now(),
                        priority='high',
                        related_entity_id=protocol.protocol_id,
                        action_url=f'/protocol/{protocol.protocol_id}'
                    ))

        return notifications

    def _check_overdue_protocols(self, protocols: List[Protocol]) -> List[Notification]:
        """Check for overdue protocols"""
        notifications = []

        for protocol in protocols:
            if protocol.is_overdue:
                # Check if notification already exists
                if not any(n.related_entity_id == protocol.protocol_id and 'overdue' in n.message.lower() for n in self.notifications):
                    hours_overdue = (datetime.now() - protocol.start_time).total_seconds() / 3600 - 48

                    notifications.append(Notification(
                        notification_id=str(uuid.uuid4()),
                        notification_type='warning',
                        title='Protocol Overdue',
                        message=f'Protocol {protocol.protocol_id} is overdue by {hours_overdue:.1f} hours. Expected completion: 48 hours.',
                        created_at=datetime.now(),
                        priority='high',
                        related_entity_id=protocol.protocol_id,
                        action_url=f'/protocol/{protocol.protocol_id}'
                    ))

        return notifications

    def _check_equipment_calibration(self, equipment: List[Equipment]) -> List[Notification]:
        """Check for equipment calibration due"""
        notifications = []

        for eq in equipment:
            if eq.calibration_due_soon:
                # Check if notification already exists
                if not any(n.related_entity_id == eq.equipment_id and 'calibration' in n.message.lower() for n in self.notifications):
                    days_until = (eq.next_calibration - datetime.now()).days if eq.next_calibration else 0

                    notifications.append(Notification(
                        notification_id=str(uuid.uuid4()),
                        notification_type='warning',
                        title='Equipment Calibration Due',
                        message=f'Equipment {eq.equipment_name} ({eq.equipment_id}) requires calibration in {days_until} days.',
                        created_at=datetime.now(),
                        priority='normal',
                        related_entity_id=eq.equipment_id,
                        action_url=f'/equipment/{eq.equipment_id}'
                    ))

        return notifications

    def _check_equipment_status(self, equipment: List[Equipment]) -> List[Notification]:
        """Check equipment status"""
        notifications = []

        for eq in equipment:
            if eq.status == 'offline':
                # Check if notification already exists
                if not any(n.related_entity_id == eq.equipment_id and 'offline' in n.message.lower() for n in self.notifications):
                    notifications.append(Notification(
                        notification_id=str(uuid.uuid4()),
                        notification_type='alert',
                        title='Equipment Offline',
                        message=f'Equipment {eq.equipment_name} ({eq.equipment_id}) is currently offline.',
                        created_at=datetime.now(),
                        priority='critical',
                        related_entity_id=eq.equipment_id,
                        action_url=f'/equipment/{eq.equipment_id}'
                    ))

        return notifications

    def _check_protocol_completion(self, protocols: List[Protocol]) -> List[Notification]:
        """Check for recently completed protocols"""
        notifications = []

        # Only notify for protocols completed in last hour
        recent_cutoff = datetime.now() - timedelta(hours=1)

        for protocol in protocols:
            if (protocol.status == ProtocolStatus.COMPLETED and
                protocol.end_time and
                protocol.end_time > recent_cutoff and
                protocol.qc_result == QCResult.PASS):

                # Check if notification already exists
                if not any(n.related_entity_id == protocol.protocol_id and 'completed' in n.message.lower() for n in self.notifications):
                    notifications.append(Notification(
                        notification_id=str(uuid.uuid4()),
                        notification_type='success',
                        title='Protocol Completed',
                        message=f'Protocol {protocol.protocol_id} ({protocol.protocol_name}) completed successfully and passed QC.',
                        created_at=datetime.now(),
                        priority='normal',
                        related_entity_id=protocol.protocol_id,
                        action_url=f'/protocol/{protocol.protocol_id}'
                    ))

        return notifications

    def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        for notif in self.notifications:
            if notif.notification_id == notification_id:
                notif.read = True
                return True
        return False

    def mark_all_as_read(self) -> int:
        """Mark all notifications as read"""
        count = 0
        for notif in self.notifications:
            if not notif.read:
                notif.read = True
                count += 1
        return count

    def get_unread_count(self) -> int:
        """Get count of unread notifications"""
        return len([n for n in self.notifications if not n.read])

    def get_notifications_by_type(self, notification_type: str) -> List[Notification]:
        """Get notifications by type"""
        return [n for n in self.notifications if n.notification_type == notification_type]

    def get_notifications_by_priority(self, priority: str) -> List[Notification]:
        """Get notifications by priority"""
        return [n for n in self.notifications if n.priority == priority]

    def clear_old_notifications(self, days: int = 30) -> int:
        """Clear notifications older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        original_count = len(self.notifications)

        self.notifications = [
            n for n in self.notifications
            if n.created_at > cutoff_date
        ]

        return original_count - len(self.notifications)

    def get_notification_summary(self) -> Dict[str, int]:
        """Get summary of notifications"""
        return {
            'total': len(self.notifications),
            'unread': self.get_unread_count(),
            'alerts': len(self.get_notifications_by_type('alert')),
            'warnings': len(self.get_notifications_by_type('warning')),
            'info': len(self.get_notifications_by_type('info')),
            'success': len(self.get_notifications_by_type('success')),
            'critical': len(self.get_notifications_by_priority('critical')),
            'high': len(self.get_notifications_by_priority('high'))
        }

    def send_email_notification(self, notification: Notification, recipients: List[str]) -> bool:
        """Send notification via email (mock implementation)"""
        # In production, this would integrate with SMTP server
        print(f"Sending email to {recipients}: {notification.title}")
        return True

    def send_webhook_notification(self, notification: Notification, webhook_url: str) -> bool:
        """Send notification via webhook (mock implementation)"""
        # In production, this would make HTTP POST request
        print(f"Sending webhook to {webhook_url}: {notification.title}")
        return True

    def configure_notification_preferences(self,
                                          user_id: str,
                                          preferences: Dict[str, Any]) -> bool:
        """Configure user notification preferences"""
        # In production, this would save to database
        return True
