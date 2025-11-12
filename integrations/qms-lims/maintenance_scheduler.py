"""
Maintenance Scheduler
Preventive maintenance scheduling, work order management, and equipment history
"""

import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
import sqlite3
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class MaintenanceType(Enum):
    """Maintenance type"""
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    PREDICTIVE = "predictive"
    EMERGENCY = "emergency"


class WorkOrderStatus(Enum):
    """Work order status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class MaintenancePriority(Enum):
    """Maintenance priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MaintenanceSchedule:
    """Maintenance schedule"""
    schedule_id: str
    equipment_id: str
    maintenance_type: MaintenanceType
    frequency_days: int
    description: str
    procedures: List[str] = field(default_factory=list)
    estimated_duration_hours: float = 1.0
    required_skills: List[str] = field(default_factory=list)
    required_parts: List[Dict] = field(default_factory=list)
    active: bool = True
    last_performed: Optional[datetime] = None
    next_due: datetime = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'schedule_id': self.schedule_id,
            'equipment_id': self.equipment_id,
            'maintenance_type': self.maintenance_type.value,
            'frequency_days': self.frequency_days,
            'description': self.description,
            'procedures': self.procedures,
            'estimated_duration_hours': self.estimated_duration_hours,
            'required_skills': self.required_skills,
            'required_parts': self.required_parts,
            'active': self.active,
            'last_performed': self.last_performed.isoformat() if self.last_performed else None,
            'next_due': self.next_due.isoformat() if self.next_due else None,
            'metadata': self.metadata
        }


@dataclass
class WorkOrder:
    """Maintenance work order"""
    work_order_id: str
    work_order_number: str
    equipment_id: str
    maintenance_type: MaintenanceType
    priority: MaintenancePriority
    status: WorkOrderStatus
    title: str
    description: str
    scheduled_date: datetime
    scheduled_duration_hours: float
    assigned_to: List[str] = field(default_factory=list)
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    work_performed: str = ""
    parts_used: List[Dict] = field(default_factory=list)
    labor_hours: float = 0.0
    cost: float = 0.0
    created_by: str = ""
    created_date: datetime = None
    completed_by: Optional[str] = None
    completion_notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'work_order_id': self.work_order_id,
            'work_order_number': self.work_order_number,
            'equipment_id': self.equipment_id,
            'maintenance_type': self.maintenance_type.value,
            'priority': self.priority.value,
            'status': self.status.value,
            'title': self.title,
            'description': self.description,
            'scheduled_date': self.scheduled_date.isoformat(),
            'scheduled_duration_hours': self.scheduled_duration_hours,
            'assigned_to': self.assigned_to,
            'actual_start': self.actual_start.isoformat() if self.actual_start else None,
            'actual_end': self.actual_end.isoformat() if self.actual_end else None,
            'work_performed': self.work_performed,
            'parts_used': self.parts_used,
            'labor_hours': self.labor_hours,
            'cost': self.cost,
            'created_by': self.created_by,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'completed_by': self.completed_by,
            'completion_notes': self.completion_notes,
            'metadata': self.metadata
        }


class MaintenanceScheduler:
    """
    Comprehensive maintenance scheduling and work order management
    """

    def __init__(self, db_path: str = "maintenance.db"):
        """Initialize maintenance scheduler"""
        self.db_path = db_path
        self._initialize_database()
        logger.info(f"MaintenanceScheduler initialized with database: {db_path}")

    @contextmanager
    def _get_connection(self):
        """Get database connection"""
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

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maintenance_schedules (
                    schedule_id TEXT PRIMARY KEY,
                    equipment_id TEXT NOT NULL,
                    maintenance_type TEXT NOT NULL,
                    frequency_days INTEGER NOT NULL,
                    description TEXT,
                    procedures TEXT,
                    estimated_duration_hours REAL,
                    required_skills TEXT,
                    required_parts TEXT,
                    active INTEGER DEFAULT 1,
                    last_performed TEXT,
                    next_due TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS work_orders (
                    work_order_id TEXT PRIMARY KEY,
                    work_order_number TEXT UNIQUE NOT NULL,
                    equipment_id TEXT NOT NULL,
                    maintenance_type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    scheduled_date TEXT NOT NULL,
                    scheduled_duration_hours REAL,
                    assigned_to TEXT,
                    actual_start TEXT,
                    actual_end TEXT,
                    work_performed TEXT,
                    parts_used TEXT,
                    labor_hours REAL DEFAULT 0,
                    cost REAL DEFAULT 0,
                    created_by TEXT,
                    created_date TEXT,
                    completed_by TEXT,
                    completion_notes TEXT,
                    metadata TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maintenance_history (
                    history_id TEXT PRIMARY KEY,
                    equipment_id TEXT NOT NULL,
                    work_order_id TEXT,
                    maintenance_date TEXT NOT NULL,
                    maintenance_type TEXT NOT NULL,
                    description TEXT,
                    performed_by TEXT,
                    duration_hours REAL,
                    downtime_hours REAL,
                    cost REAL,
                    notes TEXT,
                    FOREIGN KEY (work_order_id) REFERENCES work_orders(work_order_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipment_downtime (
                    downtime_id TEXT PRIMARY KEY,
                    equipment_id TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_hours REAL,
                    reason TEXT,
                    impact_assessment TEXT,
                    work_order_id TEXT,
                    FOREIGN KEY (work_order_id) REFERENCES work_orders(work_order_id)
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_wo_status ON work_orders(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_schedule_next_due ON maintenance_schedules(next_due)")

            logger.info("Maintenance scheduler database schema initialized")

    def create_maintenance_schedule(
        self,
        equipment_id: str,
        maintenance_type: MaintenanceType,
        frequency_days: int,
        description: str,
        procedures: Optional[List[str]] = None,
        estimated_duration_hours: float = 1.0,
        required_skills: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> MaintenanceSchedule:
        """Create maintenance schedule"""
        schedule = MaintenanceSchedule(
            schedule_id=str(uuid.uuid4()),
            equipment_id=equipment_id,
            maintenance_type=maintenance_type,
            frequency_days=frequency_days,
            description=description,
            procedures=procedures or [],
            estimated_duration_hours=estimated_duration_hours,
            required_skills=required_skills or [],
            required_parts=[],
            active=True,
            last_performed=None,
            next_due=datetime.now(timezone.utc) + timedelta(days=frequency_days),
            metadata=metadata or {}
        )

        self._store_schedule(schedule)
        logger.info(f"Created maintenance schedule: {schedule.schedule_id}")
        return schedule

    def _store_schedule(self, schedule: MaintenanceSchedule):
        """Store maintenance schedule"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO maintenance_schedules
                (schedule_id, equipment_id, maintenance_type, frequency_days, description,
                 procedures, estimated_duration_hours, required_skills, required_parts,
                 active, last_performed, next_due, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                schedule.schedule_id,
                schedule.equipment_id,
                schedule.maintenance_type.value,
                schedule.frequency_days,
                schedule.description,
                json.dumps(schedule.procedures),
                schedule.estimated_duration_hours,
                json.dumps(schedule.required_skills),
                json.dumps(schedule.required_parts),
                1 if schedule.active else 0,
                schedule.last_performed.isoformat() if schedule.last_performed else None,
                schedule.next_due.isoformat() if schedule.next_due else None,
                json.dumps(schedule.metadata)
            ))

    def create_work_order(
        self,
        equipment_id: str,
        maintenance_type: MaintenanceType,
        priority: MaintenancePriority,
        title: str,
        description: str,
        scheduled_date: datetime,
        scheduled_duration_hours: float = 1.0,
        assigned_to: Optional[List[str]] = None,
        created_by: str = "",
        metadata: Optional[Dict] = None
    ) -> WorkOrder:
        """Create work order"""
        work_order_number = self._generate_work_order_number()

        work_order = WorkOrder(
            work_order_id=str(uuid.uuid4()),
            work_order_number=work_order_number,
            equipment_id=equipment_id,
            maintenance_type=maintenance_type,
            priority=priority,
            status=WorkOrderStatus.PENDING,
            title=title,
            description=description,
            scheduled_date=scheduled_date,
            scheduled_duration_hours=scheduled_duration_hours,
            assigned_to=assigned_to or [],
            actual_start=None,
            actual_end=None,
            work_performed="",
            parts_used=[],
            labor_hours=0.0,
            cost=0.0,
            created_by=created_by,
            created_date=datetime.now(timezone.utc),
            completed_by=None,
            completion_notes="",
            metadata=metadata or {}
        )

        self._store_work_order(work_order)
        logger.info(f"Created work order: {work_order.work_order_number}")
        return work_order

    def _generate_work_order_number(self) -> str:
        """Generate unique work order number"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM work_orders")
            count = cursor.fetchone()['count']

        year = datetime.now().year
        return f"WO-{year}-{count + 1:05d}"

    def _store_work_order(self, work_order: WorkOrder):
        """Store work order"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO work_orders
                (work_order_id, work_order_number, equipment_id, maintenance_type, priority,
                 status, title, description, scheduled_date, scheduled_duration_hours,
                 assigned_to, actual_start, actual_end, work_performed, parts_used,
                 labor_hours, cost, created_by, created_date, completed_by, completion_notes, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                work_order.work_order_id,
                work_order.work_order_number,
                work_order.equipment_id,
                work_order.maintenance_type.value,
                work_order.priority.value,
                work_order.status.value,
                work_order.title,
                work_order.description,
                work_order.scheduled_date.isoformat(),
                work_order.scheduled_duration_hours,
                json.dumps(work_order.assigned_to),
                work_order.actual_start.isoformat() if work_order.actual_start else None,
                work_order.actual_end.isoformat() if work_order.actual_end else None,
                work_order.work_performed,
                json.dumps(work_order.parts_used),
                work_order.labor_hours,
                work_order.cost,
                work_order.created_by,
                work_order.created_date.isoformat() if work_order.created_date else None,
                work_order.completed_by,
                work_order.completion_notes,
                json.dumps(work_order.metadata)
            ))

    def complete_work_order(
        self,
        work_order_id: str,
        completed_by: str,
        work_performed: str,
        labor_hours: float,
        cost: float,
        parts_used: Optional[List[Dict]] = None,
        completion_notes: str = ""
    ):
        """Complete work order"""
        work_order = self.get_work_order(work_order_id)
        if not work_order:
            raise ValueError(f"Work order not found: {work_order_id}")

        work_order.status = WorkOrderStatus.COMPLETED
        work_order.actual_end = datetime.now(timezone.utc)
        work_order.work_performed = work_performed
        work_order.labor_hours = labor_hours
        work_order.cost = cost
        work_order.parts_used = parts_used or []
        work_order.completed_by = completed_by
        work_order.completion_notes = completion_notes

        if not work_order.actual_start:
            work_order.actual_start = work_order.actual_end - timedelta(hours=labor_hours)

        self._store_work_order(work_order)

        # Update maintenance schedule if linked
        self._update_schedule_after_maintenance(work_order.equipment_id)

        # Record maintenance history
        self._record_maintenance_history(work_order)

        logger.info(f"Completed work order: {work_order.work_order_number}")

    def _update_schedule_after_maintenance(self, equipment_id: str):
        """Update maintenance schedules after maintenance"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM maintenance_schedules
                WHERE equipment_id = ? AND active = 1
            """, (equipment_id,))

            for row in cursor.fetchall():
                last_performed = datetime.now(timezone.utc)
                frequency_days = row['frequency_days']
                next_due = last_performed + timedelta(days=frequency_days)

                cursor.execute("""
                    UPDATE maintenance_schedules
                    SET last_performed = ?, next_due = ?
                    WHERE schedule_id = ?
                """, (last_performed.isoformat(), next_due.isoformat(), row['schedule_id']))

    def _record_maintenance_history(self, work_order: WorkOrder):
        """Record maintenance history"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO maintenance_history
                (history_id, equipment_id, work_order_id, maintenance_date, maintenance_type,
                 description, performed_by, duration_hours, downtime_hours, cost, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                work_order.equipment_id,
                work_order.work_order_id,
                work_order.actual_end.isoformat() if work_order.actual_end else datetime.now(timezone.utc).isoformat(),
                work_order.maintenance_type.value,
                work_order.title,
                work_order.completed_by,
                work_order.labor_hours,
                0.0,  # Calculate actual downtime if needed
                work_order.cost,
                work_order.completion_notes
            ))

    def get_due_maintenance(self, days_ahead: int = 7) -> List[MaintenanceSchedule]:
        """Get maintenance due in next N days"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            threshold_date = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).isoformat()

            cursor.execute("""
                SELECT * FROM maintenance_schedules
                WHERE next_due <= ? AND active = 1
                ORDER BY next_due ASC
            """, (threshold_date,))

            schedules = []
            for row in cursor.fetchall():
                schedules.append(MaintenanceSchedule(
                    schedule_id=row['schedule_id'],
                    equipment_id=row['equipment_id'],
                    maintenance_type=MaintenanceType(row['maintenance_type']),
                    frequency_days=row['frequency_days'],
                    description=row['description'],
                    procedures=json.loads(row['procedures']),
                    estimated_duration_hours=row['estimated_duration_hours'],
                    required_skills=json.loads(row['required_skills']),
                    required_parts=json.loads(row['required_parts']),
                    active=bool(row['active']),
                    last_performed=datetime.fromisoformat(row['last_performed']) if row['last_performed'] else None,
                    next_due=datetime.fromisoformat(row['next_due']) if row['next_due'] else None,
                    metadata=json.loads(row['metadata'])
                ))

            return schedules

    def get_work_order(self, work_order_id: str) -> Optional[WorkOrder]:
        """Get work order by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM work_orders WHERE work_order_id = ?", (work_order_id,))
            row = cursor.fetchone()

            if row:
                return WorkOrder(
                    work_order_id=row['work_order_id'],
                    work_order_number=row['work_order_number'],
                    equipment_id=row['equipment_id'],
                    maintenance_type=MaintenanceType(row['maintenance_type']),
                    priority=MaintenancePriority(row['priority']),
                    status=WorkOrderStatus(row['status']),
                    title=row['title'],
                    description=row['description'],
                    scheduled_date=datetime.fromisoformat(row['scheduled_date']),
                    scheduled_duration_hours=row['scheduled_duration_hours'],
                    assigned_to=json.loads(row['assigned_to']),
                    actual_start=datetime.fromisoformat(row['actual_start']) if row['actual_start'] else None,
                    actual_end=datetime.fromisoformat(row['actual_end']) if row['actual_end'] else None,
                    work_performed=row['work_performed'],
                    parts_used=json.loads(row['parts_used']),
                    labor_hours=row['labor_hours'],
                    cost=row['cost'],
                    created_by=row['created_by'],
                    created_date=datetime.fromisoformat(row['created_date']) if row['created_date'] else None,
                    completed_by=row['completed_by'],
                    completion_notes=row['completion_notes'],
                    metadata=json.loads(row['metadata'])
                )
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get maintenance statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            cursor.execute("SELECT COUNT(*) as count FROM maintenance_schedules WHERE active = 1")
            stats['active_schedules'] = cursor.fetchone()['count']

            cursor.execute("SELECT status, COUNT(*) as count FROM work_orders GROUP BY status")
            stats['work_orders_by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}

            cursor.execute("SELECT SUM(cost) as total FROM work_orders WHERE status = 'completed'")
            stats['total_maintenance_cost'] = cursor.fetchone()['total'] or 0

            cursor.execute("SELECT SUM(labor_hours) as total FROM work_orders WHERE status = 'completed'")
            stats['total_labor_hours'] = cursor.fetchone()['total'] or 0

            return stats


if __name__ == "__main__":
    scheduler = MaintenanceScheduler()

    schedule = scheduler.create_maintenance_schedule(
        equipment_id="EQ-001",
        maintenance_type=MaintenanceType.PREVENTIVE,
        frequency_days=90,
        description="Quarterly preventive maintenance",
        procedures=["Clean filters", "Lubricate moving parts", "Check sensors"],
        estimated_duration_hours=2.0
    )

    print(f"Created schedule: {schedule.schedule_id}")

    work_order = scheduler.create_work_order(
        equipment_id="EQ-001",
        maintenance_type=MaintenanceType.PREVENTIVE,
        priority=MaintenancePriority.MEDIUM,
        title="Quarterly PM for Thermal Chamber",
        description="Perform quarterly preventive maintenance",
        scheduled_date=datetime.now(timezone.utc) + timedelta(days=1),
        created_by="maint001"
    )

    print(f"Created work order: {work_order.work_order_number}")
