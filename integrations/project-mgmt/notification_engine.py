"""
Notification Engine
Automated notifications for milestones, deadlines, and alerts (email, SMS, webhook support)
"""

import json
import uuid
import smtplib
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import sqlite3
from contextlib import contextmanager
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification types"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    PUSH = "push"


class Priority(Enum):
    """Notification priority"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EventType(Enum):
    """Event types that trigger notifications"""
    MILESTONE_DUE = "milestone_due"
    MILESTONE_COMPLETED = "milestone_completed"
    DEADLINE_APPROACHING = "deadline_approaching"
    DEADLINE_MISSED = "deadline_missed"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    PROJECT_STATUS_CHANGE = "project_status_change"
    DELAY_REPORTED = "delay_reported"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    APPROVAL_REQUIRED = "approval_required"
    ALERT_TRIGGERED = "alert_triggered"
    SYSTEM_NOTIFICATION = "system_notification"


@dataclass
class NotificationTemplate:
    """Notification template"""
    template_id: str
    name: str
    event_type: EventType
    notification_type: NotificationType
    subject_template: str
    body_template: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def render(self, context: Dict[str, Any]) -> Tuple[str, str]:
        """
        Render template with context

        Args:
            context: Template context variables

        Returns:
            Tuple of (subject, body)
        """
        subject = self.subject_template
        body = self.body_template

        for key, value in context.items():
            placeholder = f"{{{key}}}"
            subject = subject.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))

        return subject, body


@dataclass
class Notification:
    """Notification instance"""
    notification_id: str
    notification_type: NotificationType
    event_type: EventType
    priority: Priority
    recipient: str  # email, phone, user_id, etc.
    subject: str
    message: str
    scheduled_at: datetime
    sent_at: Optional[datetime]
    status: str  # pending, sent, failed, cancelled
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'notification_id': self.notification_id,
            'notification_type': self.notification_type.value,
            'event_type': self.event_type.value,
            'priority': self.priority.value,
            'recipient': self.recipient,
            'subject': self.subject,
            'message': self.message,
            'scheduled_at': self.scheduled_at.isoformat(),
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'status': self.status,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'metadata': self.metadata,
            'error_message': self.error_message
        }


@dataclass
class NotificationRule:
    """Notification rule/subscription"""
    rule_id: str
    user_id: str
    event_types: List[EventType]
    notification_types: List[NotificationType]
    filters: Dict[str, Any] = field(default_factory=dict)
    active: bool = True
    quiet_hours_start: Optional[int] = None  # Hour 0-23
    quiet_hours_end: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'rule_id': self.rule_id,
            'user_id': self.user_id,
            'event_types': [et.value for et in self.event_types],
            'notification_types': [nt.value for nt in self.notification_types],
            'filters': self.filters,
            'active': self.active,
            'quiet_hours_start': self.quiet_hours_start,
            'quiet_hours_end': self.quiet_hours_end
        }


class NotificationEngine:
    """
    Comprehensive notification engine supporting multiple channels
    """

    def __init__(
        self,
        db_path: str = "notifications.db",
        config: Optional[Dict] = None
    ):
        """
        Initialize notification engine

        Args:
            db_path: Path to SQLite database
            config: Configuration dictionary
        """
        self.db_path = db_path
        self.config = config or {}
        self._initialize_database()
        self._load_templates()
        self._running = False
        self._worker_thread = None
        logger.info(f"NotificationEngine initialized with database: {db_path}")

    @contextmanager
    def _get_connection(self):
        """Get database connection context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _initialize_database(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Notifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    notification_id TEXT PRIMARY KEY,
                    notification_type TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    subject TEXT,
                    message TEXT NOT NULL,
                    scheduled_at TEXT NOT NULL,
                    sent_at TEXT,
                    status TEXT NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    metadata TEXT,
                    error_message TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Notification templates
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_templates (
                    template_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    notification_type TEXT NOT NULL,
                    subject_template TEXT,
                    body_template TEXT NOT NULL,
                    metadata TEXT
                )
            """)

            # Notification rules (user subscriptions)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_rules (
                    rule_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    event_types TEXT NOT NULL,
                    notification_types TEXT NOT NULL,
                    filters TEXT,
                    active INTEGER DEFAULT 1,
                    quiet_hours_start INTEGER,
                    quiet_hours_end INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Notification log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_log (
                    log_id TEXT PRIMARY KEY,
                    notification_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    details TEXT,
                    FOREIGN KEY (notification_id) REFERENCES notifications(notification_id)
                )
            """)

            # Delivery statistics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS delivery_stats (
                    stat_id TEXT PRIMARY KEY,
                    notification_type TEXT NOT NULL,
                    date TEXT NOT NULL,
                    sent_count INTEGER DEFAULT 0,
                    failed_count INTEGER DEFAULT 0,
                    avg_delivery_time_ms REAL DEFAULT 0
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notif_status ON notifications(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notif_scheduled ON notifications(scheduled_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notif_recipient ON notifications(recipient)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rule_user ON notification_rules(user_id)")

            logger.info("Notification engine database schema initialized")

    def _load_templates(self):
        """Load default notification templates"""
        default_templates = [
            {
                'name': 'milestone_due_email',
                'event_type': EventType.MILESTONE_DUE,
                'notification_type': NotificationType.EMAIL,
                'subject': 'Milestone Due: {milestone_name}',
                'body': '''Dear {recipient_name},

This is a reminder that milestone "{milestone_name}" is due on {due_date}.

Project: {project_name}
Description: {description}

Please ensure all deliverables are completed on time.

Best regards,
Project Management System'''
            },
            {
                'name': 'deadline_missed_email',
                'event_type': EventType.DEADLINE_MISSED,
                'notification_type': NotificationType.EMAIL,
                'subject': 'URGENT: Deadline Missed - {task_name}',
                'body': '''URGENT NOTIFICATION

Task "{task_name}" has missed its deadline of {deadline}.

Project: {project_name}
Current Status: {status}

Immediate action required. Please update the task status and report any delays.

Best regards,
Project Management System'''
            },
            {
                'name': 'task_assigned_email',
                'event_type': EventType.TASK_ASSIGNED,
                'notification_type': NotificationType.EMAIL,
                'subject': 'New Task Assigned: {task_name}',
                'body': '''Hello {recipient_name},

You have been assigned a new task:

Task: {task_name}
Project: {project_name}
Due Date: {due_date}
Priority: {priority}

Description:
{description}

Please review and acknowledge this assignment.

Best regards,
Project Management System'''
            }
        ]

        for template_data in default_templates:
            template_id = str(uuid.uuid4())
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO notification_templates
                    (template_id, name, event_type, notification_type, subject_template, body_template, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    template_id,
                    template_data['name'],
                    template_data['event_type'].value,
                    template_data['notification_type'].value,
                    template_data['subject'],
                    template_data['body'],
                    json.dumps({})
                ))

    def create_notification(
        self,
        event_type: EventType,
        notification_type: NotificationType,
        recipient: str,
        context: Dict[str, Any],
        priority: Priority = Priority.NORMAL,
        scheduled_at: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> Notification:
        """
        Create a notification

        Args:
            event_type: Event type
            notification_type: Notification type
            recipient: Recipient identifier
            context: Template context
            priority: Priority level
            scheduled_at: When to send (None = now)
            metadata: Additional metadata

        Returns:
            Notification object
        """
        # Get template
        template = self._get_template(event_type, notification_type)

        if template:
            subject, message = template.render(context)
        else:
            subject = context.get('subject', f'{event_type.value} notification')
            message = context.get('message', 'Notification')

        notification = Notification(
            notification_id=str(uuid.uuid4()),
            notification_type=notification_type,
            event_type=event_type,
            priority=priority,
            recipient=recipient,
            subject=subject,
            message=message,
            scheduled_at=scheduled_at or datetime.now(timezone.utc),
            sent_at=None,
            status='pending',
            retry_count=0,
            max_retries=3,
            metadata=metadata or {},
            error_message=None
        )

        self._store_notification(notification)
        logger.info(f"Created notification: {notification.notification_id}")
        return notification

    def _get_template(
        self,
        event_type: EventType,
        notification_type: NotificationType
    ) -> Optional[NotificationTemplate]:
        """Get notification template"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM notification_templates
                WHERE event_type = ? AND notification_type = ?
                LIMIT 1
            """, (event_type.value, notification_type.value))

            row = cursor.fetchone()
            if row:
                return NotificationTemplate(
                    template_id=row['template_id'],
                    name=row['name'],
                    event_type=EventType(row['event_type']),
                    notification_type=NotificationType(row['notification_type']),
                    subject_template=row['subject_template'] or '',
                    body_template=row['body_template'],
                    metadata=json.loads(row['metadata'])
                )
        return None

    def _store_notification(self, notification: Notification):
        """Store notification in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO notifications
                (notification_id, notification_type, event_type, priority, recipient,
                 subject, message, scheduled_at, sent_at, status, retry_count,
                 max_retries, metadata, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                notification.notification_id,
                notification.notification_type.value,
                notification.event_type.value,
                notification.priority.value,
                notification.recipient,
                notification.subject,
                notification.message,
                notification.scheduled_at.isoformat(),
                notification.sent_at.isoformat() if notification.sent_at else None,
                notification.status,
                notification.retry_count,
                notification.max_retries,
                json.dumps(notification.metadata),
                notification.error_message
            ))

    def send_notification(self, notification_id: str) -> bool:
        """
        Send a notification

        Args:
            notification_id: Notification ID

        Returns:
            Success status
        """
        notification = self._get_notification(notification_id)
        if not notification:
            logger.error(f"Notification not found: {notification_id}")
            return False

        try:
            start_time = datetime.now(timezone.utc)

            if notification.notification_type == NotificationType.EMAIL:
                success = self._send_email(notification)
            elif notification.notification_type == NotificationType.SMS:
                success = self._send_sms(notification)
            elif notification.notification_type == NotificationType.WEBHOOK:
                success = self._send_webhook(notification)
            elif notification.notification_type == NotificationType.IN_APP:
                success = self._send_in_app(notification)
            else:
                logger.warning(f"Unsupported notification type: {notification.notification_type}")
                success = False

            end_time = datetime.now(timezone.utc)
            delivery_time_ms = (end_time - start_time).total_seconds() * 1000

            if success:
                notification.status = 'sent'
                notification.sent_at = datetime.now(timezone.utc)
                self._store_notification(notification)
                self._log_action(notification_id, 'sent', {'delivery_time_ms': delivery_time_ms})
                logger.info(f"Notification sent successfully: {notification_id}")
                return True
            else:
                notification.retry_count += 1
                if notification.retry_count >= notification.max_retries:
                    notification.status = 'failed'
                else:
                    notification.status = 'pending'
                self._store_notification(notification)
                return False

        except Exception as e:
            logger.error(f"Error sending notification {notification_id}: {e}")
            notification.status = 'failed'
            notification.error_message = str(e)
            self._store_notification(notification)
            return False

    def _send_email(self, notification: Notification) -> bool:
        """Send email notification"""
        try:
            # Email configuration
            smtp_host = self.config.get('smtp_host', 'localhost')
            smtp_port = self.config.get('smtp_port', 587)
            smtp_user = self.config.get('smtp_user', '')
            smtp_password = self.config.get('smtp_password', '')
            from_email = self.config.get('from_email', 'noreply@example.com')

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = notification.subject
            msg['From'] = from_email
            msg['To'] = notification.recipient

            # Add body
            text_part = MIMEText(notification.message, 'plain')
            msg.attach(text_part)

            # Send email
            if self.config.get('smtp_enabled', False):
                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    server.starttls()
                    if smtp_user and smtp_password:
                        server.login(smtp_user, smtp_password)
                    server.send_message(msg)
                return True
            else:
                # Simulate sending for testing
                logger.info(f"[SIMULATED] Email sent to {notification.recipient}: {notification.subject}")
                return True

        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False

    def _send_sms(self, notification: Notification) -> bool:
        """Send SMS notification"""
        try:
            # SMS API configuration
            sms_api_url = self.config.get('sms_api_url', '')
            sms_api_key = self.config.get('sms_api_key', '')

            if not sms_api_url:
                logger.info(f"[SIMULATED] SMS sent to {notification.recipient}: {notification.message}")
                return True

            # Send via API
            response = requests.post(
                sms_api_url,
                headers={'Authorization': f'Bearer {sms_api_key}'},
                json={
                    'to': notification.recipient,
                    'message': notification.message
                },
                timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            return False

    def _send_webhook(self, notification: Notification) -> bool:
        """Send webhook notification"""
        try:
            webhook_url = notification.metadata.get('webhook_url', '')

            if not webhook_url:
                logger.warning("No webhook URL provided")
                return False

            payload = {
                'notification_id': notification.notification_id,
                'event_type': notification.event_type.value,
                'priority': notification.priority.value,
                'subject': notification.subject,
                'message': notification.message,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'metadata': notification.metadata
            }

            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )

            return response.status_code in [200, 201, 202]

        except Exception as e:
            logger.error(f"Webhook sending failed: {e}")
            return False

    def _send_in_app(self, notification: Notification) -> bool:
        """Send in-app notification"""
        # Store in database for user to retrieve
        logger.info(f"In-app notification created for {notification.recipient}")
        return True

    def _get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notifications WHERE notification_id = ?", (notification_id,))
            row = cursor.fetchone()

            if row:
                return Notification(
                    notification_id=row['notification_id'],
                    notification_type=NotificationType(row['notification_type']),
                    event_type=EventType(row['event_type']),
                    priority=Priority(row['priority']),
                    recipient=row['recipient'],
                    subject=row['subject'] or '',
                    message=row['message'],
                    scheduled_at=datetime.fromisoformat(row['scheduled_at']),
                    sent_at=datetime.fromisoformat(row['sent_at']) if row['sent_at'] else None,
                    status=row['status'],
                    retry_count=row['retry_count'],
                    max_retries=row['max_retries'],
                    metadata=json.loads(row['metadata']),
                    error_message=row['error_message']
                )
        return None

    def _log_action(self, notification_id: str, action: str, details: Optional[Dict] = None):
        """Log notification action"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notification_log
                (log_id, notification_id, action, timestamp, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                notification_id,
                action,
                datetime.now(timezone.utc).isoformat(),
                json.dumps(details or {})
            ))

    def start_worker(self):
        """Start background worker to process pending notifications"""
        if self._running:
            logger.warning("Worker already running")
            return

        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        logger.info("Notification worker started")

    def stop_worker(self):
        """Stop background worker"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        logger.info("Notification worker stopped")

    def _worker_loop(self):
        """Background worker loop"""
        while self._running:
            try:
                # Get pending notifications
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT notification_id FROM notifications
                        WHERE status = 'pending'
                        AND scheduled_at <= ?
                        ORDER BY priority DESC, scheduled_at ASC
                        LIMIT 10
                    """, (datetime.now(timezone.utc).isoformat(),))

                    for row in cursor.fetchall():
                        self.send_notification(row['notification_id'])

                time.sleep(5)  # Check every 5 seconds

            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                time.sleep(10)

    def get_statistics(self) -> Dict[str, Any]:
        """Get notification engine statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Total notifications
            cursor.execute("SELECT COUNT(*) as count FROM notifications")
            stats['total_notifications'] = cursor.fetchone()['count']

            # By status
            cursor.execute("SELECT status, COUNT(*) as count FROM notifications GROUP BY status")
            stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}

            # By type
            cursor.execute("SELECT notification_type, COUNT(*) as count FROM notifications GROUP BY notification_type")
            stats['by_type'] = {row['notification_type']: row['count'] for row in cursor.fetchall()}

            # Success rate
            cursor.execute("""
                SELECT
                    COUNT(CASE WHEN status = 'sent' THEN 1 END) * 100.0 / COUNT(*) as success_rate
                FROM notifications
            """)
            stats['success_rate'] = cursor.fetchone()['success_rate'] or 0

            return stats


if __name__ == "__main__":
    # Example usage
    engine = NotificationEngine(config={
        'smtp_enabled': False,  # Disable for testing
        'from_email': 'noreply@example.com'
    })

    # Create milestone due notification
    notification = engine.create_notification(
        event_type=EventType.MILESTONE_DUE,
        notification_type=NotificationType.EMAIL,
        recipient='engineer@example.com',
        context={
            'recipient_name': 'John Doe',
            'milestone_name': 'Phase 1 Completion',
            'due_date': '2025-12-01',
            'project_name': 'PVTP Testing Campaign',
            'description': 'Complete all thermal cycling tests'
        },
        priority=Priority.HIGH
    )

    # Send notification
    success = engine.send_notification(notification.notification_id)
    print(f"Notification sent: {success}")

    # Get statistics
    stats = engine.get_statistics()
    print(f"Statistics: {json.dumps(stats, indent=2)}")
