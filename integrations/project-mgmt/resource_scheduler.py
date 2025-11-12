"""
Resource Scheduler
Lab equipment scheduling, personnel allocation, and material management
"""

import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import sqlite3
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Resource types"""
    PERSONNEL = "personnel"
    EQUIPMENT = "equipment"
    MATERIAL = "material"
    FACILITY = "facility"
    SOFTWARE = "software"


class ResourceStatus(Enum):
    """Resource availability status"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"
    RETIRED = "retired"


class BookingStatus(Enum):
    """Booking status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_USE = "in_use"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Resource:
    """Resource definition"""
    resource_id: str
    name: str
    resource_type: ResourceType
    status: ResourceStatus
    location: str
    capacity: float
    unit: str
    cost_per_hour: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    maintenance_schedule: List[Dict] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'resource_id': self.resource_id,
            'name': self.name,
            'resource_type': self.resource_type.value,
            'status': self.status.value,
            'location': self.location,
            'capacity': self.capacity,
            'unit': self.unit,
            'cost_per_hour': self.cost_per_hour,
            'metadata': self.metadata,
            'maintenance_schedule': self.maintenance_schedule,
            'certifications': self.certifications
        }


@dataclass
class Booking:
    """Resource booking"""
    booking_id: str
    resource_id: str
    project_id: str
    booked_by: str
    start_time: datetime
    end_time: datetime
    duration_hours: float
    status: BookingStatus
    purpose: str
    priority: int  # 1-10, 10 highest
    cost: float
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'booking_id': self.booking_id,
            'resource_id': self.resource_id,
            'project_id': self.project_id,
            'booked_by': self.booked_by,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_hours': self.duration_hours,
            'status': self.status.value,
            'purpose': self.purpose,
            'priority': self.priority,
            'cost': self.cost,
            'notes': self.notes,
            'metadata': self.metadata
        }


@dataclass
class PersonnelResource:
    """Personnel resource with skills and availability"""
    user_id: str
    name: str
    role: str
    skills: List[str]
    certifications: List[str]
    availability_percentage: float  # 0-100%
    hourly_rate: float
    department: str
    max_concurrent_projects: int = 3

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'role': self.role,
            'skills': self.skills,
            'certifications': self.certifications,
            'availability_percentage': self.availability_percentage,
            'hourly_rate': self.hourly_rate,
            'department': self.department,
            'max_concurrent_projects': self.max_concurrent_projects
        }


class ResourceScheduler:
    """
    Comprehensive resource scheduling and management system
    """

    def __init__(self, db_path: str = "resource_scheduler.db"):
        """
        Initialize resource scheduler

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._initialize_database()
        logger.info(f"ResourceScheduler initialized with database: {db_path}")

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

            # Resources table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resources (
                    resource_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    location TEXT,
                    capacity REAL DEFAULT 1,
                    unit TEXT DEFAULT 'unit',
                    cost_per_hour REAL DEFAULT 0,
                    metadata TEXT,
                    maintenance_schedule TEXT,
                    certifications TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Bookings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    booking_id TEXT PRIMARY KEY,
                    resource_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    booked_by TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    duration_hours REAL NOT NULL,
                    status TEXT NOT NULL,
                    purpose TEXT,
                    priority INTEGER DEFAULT 5,
                    cost REAL DEFAULT 0,
                    notes TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
                )
            """)

            # Personnel table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personnel (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    skills TEXT,
                    certifications TEXT,
                    availability_percentage REAL DEFAULT 100,
                    hourly_rate REAL DEFAULT 0,
                    department TEXT,
                    max_concurrent_projects INTEGER DEFAULT 3,
                    metadata TEXT
                )
            """)

            # Resource utilization metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS utilization_metrics (
                    metric_id TEXT PRIMARY KEY,
                    resource_id TEXT NOT NULL,
                    period_start TEXT NOT NULL,
                    period_end TEXT NOT NULL,
                    total_hours_available REAL,
                    total_hours_booked REAL,
                    total_hours_used REAL,
                    utilization_percentage REAL,
                    revenue_generated REAL,
                    FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
                )
            """)

            # Conflicts and warnings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS booking_conflicts (
                    conflict_id TEXT PRIMARY KEY,
                    booking_id_1 TEXT NOT NULL,
                    booking_id_2 TEXT NOT NULL,
                    conflict_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    resolved INTEGER DEFAULT 0,
                    resolved_at TEXT,
                    FOREIGN KEY (booking_id_1) REFERENCES bookings(booking_id),
                    FOREIGN KEY (booking_id_2) REFERENCES bookings(booking_id)
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_resource_type ON resources(resource_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_resource_status ON resources(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_booking_time ON bookings(start_time, end_time)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_booking_resource ON bookings(resource_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_booking_project ON bookings(project_id)")

            logger.info("Resource scheduler database schema initialized")

    def add_resource(
        self,
        name: str,
        resource_type: ResourceType,
        location: str = "",
        capacity: float = 1.0,
        unit: str = "unit",
        cost_per_hour: float = 0.0,
        metadata: Optional[Dict] = None,
        certifications: Optional[List[str]] = None
    ) -> Resource:
        """
        Add a new resource

        Args:
            name: Resource name
            resource_type: Type of resource
            location: Physical location
            capacity: Resource capacity
            unit: Unit of measurement
            cost_per_hour: Cost per hour
            metadata: Additional metadata
            certifications: Required certifications

        Returns:
            Resource object
        """
        resource = Resource(
            resource_id=str(uuid.uuid4()),
            name=name,
            resource_type=resource_type,
            status=ResourceStatus.AVAILABLE,
            location=location,
            capacity=capacity,
            unit=unit,
            cost_per_hour=cost_per_hour,
            metadata=metadata or {},
            maintenance_schedule=[],
            certifications=certifications or []
        )

        self._store_resource(resource)
        logger.info(f"Added resource: {resource.resource_id}")
        return resource

    def _store_resource(self, resource: Resource):
        """Store resource in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO resources
                (resource_id, name, resource_type, status, location, capacity, unit,
                 cost_per_hour, metadata, maintenance_schedule, certifications)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resource.resource_id,
                resource.name,
                resource.resource_type.value,
                resource.status.value,
                resource.location,
                resource.capacity,
                resource.unit,
                resource.cost_per_hour,
                json.dumps(resource.metadata),
                json.dumps(resource.maintenance_schedule),
                json.dumps(resource.certifications)
            ))

    def create_booking(
        self,
        resource_id: str,
        project_id: str,
        booked_by: str,
        start_time: datetime,
        end_time: datetime,
        purpose: str,
        priority: int = 5,
        notes: str = "",
        metadata: Optional[Dict] = None
    ) -> Optional[Booking]:
        """
        Create a resource booking

        Args:
            resource_id: Resource ID
            project_id: Project ID
            booked_by: User ID who booked
            start_time: Booking start time
            end_time: Booking end time
            purpose: Purpose of booking
            priority: Priority level (1-10)
            notes: Additional notes
            metadata: Additional metadata

        Returns:
            Booking object or None if conflicts exist
        """
        # Check availability
        if not self.check_availability(resource_id, start_time, end_time):
            logger.warning(f"Resource {resource_id} not available for requested time")
            return None

        # Calculate duration and cost
        duration_hours = (end_time - start_time).total_seconds() / 3600
        resource = self.get_resource(resource_id)
        cost = duration_hours * resource.cost_per_hour if resource else 0.0

        booking = Booking(
            booking_id=str(uuid.uuid4()),
            resource_id=resource_id,
            project_id=project_id,
            booked_by=booked_by,
            start_time=start_time,
            end_time=end_time,
            duration_hours=duration_hours,
            status=BookingStatus.CONFIRMED,
            purpose=purpose,
            priority=priority,
            cost=cost,
            notes=notes,
            metadata=metadata or {}
        )

        self._store_booking(booking)
        logger.info(f"Created booking: {booking.booking_id}")
        return booking

    def _store_booking(self, booking: Booking):
        """Store booking in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO bookings
                (booking_id, resource_id, project_id, booked_by, start_time, end_time,
                 duration_hours, status, purpose, priority, cost, notes, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                booking.booking_id,
                booking.resource_id,
                booking.project_id,
                booking.booked_by,
                booking.start_time.isoformat(),
                booking.end_time.isoformat(),
                booking.duration_hours,
                booking.status.value,
                booking.purpose,
                booking.priority,
                booking.cost,
                booking.notes,
                json.dumps(booking.metadata)
            ))

    def check_availability(
        self,
        resource_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """
        Check if resource is available for given time period

        Args:
            resource_id: Resource ID
            start_time: Start time
            end_time: End time

        Returns:
            True if available, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Check for overlapping bookings
            cursor.execute("""
                SELECT COUNT(*) as count FROM bookings
                WHERE resource_id = ?
                AND status NOT IN ('cancelled', 'completed')
                AND (
                    (start_time <= ? AND end_time >= ?)
                    OR (start_time <= ? AND end_time >= ?)
                    OR (start_time >= ? AND end_time <= ?)
                )
            """, (
                resource_id,
                start_time.isoformat(), start_time.isoformat(),
                end_time.isoformat(), end_time.isoformat(),
                start_time.isoformat(), end_time.isoformat()
            ))

            count = cursor.fetchone()['count']
            return count == 0

    def get_resource_schedule(
        self,
        resource_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Booking]:
        """
        Get resource schedule for date range

        Args:
            resource_id: Resource ID
            start_date: Start date
            end_date: End date

        Returns:
            List of bookings
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM bookings
                WHERE resource_id = ?
                AND start_time >= ?
                AND end_time <= ?
                ORDER BY start_time ASC
            """, (resource_id, start_date.isoformat(), end_date.isoformat()))

            bookings = []
            for row in cursor.fetchall():
                bookings.append(Booking(
                    booking_id=row['booking_id'],
                    resource_id=row['resource_id'],
                    project_id=row['project_id'],
                    booked_by=row['booked_by'],
                    start_time=datetime.fromisoformat(row['start_time']),
                    end_time=datetime.fromisoformat(row['end_time']),
                    duration_hours=row['duration_hours'],
                    status=BookingStatus(row['status']),
                    purpose=row['purpose'],
                    priority=row['priority'],
                    cost=row['cost'],
                    notes=row['notes'] or "",
                    metadata=json.loads(row['metadata'])
                ))

            return bookings

    def add_personnel(
        self,
        name: str,
        role: str,
        skills: List[str],
        certifications: Optional[List[str]] = None,
        hourly_rate: float = 0.0,
        department: str = "",
        availability_percentage: float = 100.0
    ) -> PersonnelResource:
        """
        Add personnel resource

        Args:
            name: Person's name
            role: Job role
            skills: List of skills
            certifications: List of certifications
            hourly_rate: Hourly rate
            department: Department
            availability_percentage: Availability percentage

        Returns:
            PersonnelResource object
        """
        personnel = PersonnelResource(
            user_id=str(uuid.uuid4()),
            name=name,
            role=role,
            skills=skills,
            certifications=certifications or [],
            availability_percentage=availability_percentage,
            hourly_rate=hourly_rate,
            department=department
        )

        self._store_personnel(personnel)
        logger.info(f"Added personnel: {personnel.user_id}")
        return personnel

    def _store_personnel(self, personnel: PersonnelResource):
        """Store personnel in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO personnel
                (user_id, name, role, skills, certifications, availability_percentage,
                 hourly_rate, department, max_concurrent_projects, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                personnel.user_id,
                personnel.name,
                personnel.role,
                json.dumps(personnel.skills),
                json.dumps(personnel.certifications),
                personnel.availability_percentage,
                personnel.hourly_rate,
                personnel.department,
                personnel.max_concurrent_projects,
                json.dumps({})
            ))

    def find_available_personnel(
        self,
        required_skills: List[str],
        start_time: datetime,
        end_time: datetime,
        certifications: Optional[List[str]] = None
    ) -> List[PersonnelResource]:
        """
        Find available personnel with required skills

        Args:
            required_skills: Required skills
            start_time: Availability start
            end_time: Availability end
            certifications: Required certifications

        Returns:
            List of available personnel
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM personnel WHERE availability_percentage > 0")

            available = []
            for row in cursor.fetchall():
                skills = json.loads(row['skills'])
                person_certs = json.loads(row['certifications'])

                # Check skills match
                skills_match = all(skill in skills for skill in required_skills)

                # Check certifications if required
                certs_match = True
                if certifications:
                    certs_match = all(cert in person_certs for cert in certifications)

                if skills_match and certs_match:
                    # Check availability for time period
                    cursor.execute("""
                        SELECT COUNT(*) as count FROM bookings b
                        JOIN resources r ON b.resource_id = r.resource_id
                        WHERE r.resource_type = 'personnel'
                        AND r.metadata LIKE ?
                        AND b.status NOT IN ('cancelled', 'completed')
                        AND (
                            (b.start_time <= ? AND b.end_time >= ?)
                            OR (b.start_time <= ? AND b.end_time >= ?)
                            OR (b.start_time >= ? AND b.end_time <= ?)
                        )
                    """, (
                        f'%{row["user_id"]}%',
                        start_time.isoformat(), start_time.isoformat(),
                        end_time.isoformat(), end_time.isoformat(),
                        start_time.isoformat(), end_time.isoformat()
                    ))

                    if cursor.fetchone()['count'] == 0:
                        available.append(PersonnelResource(
                            user_id=row['user_id'],
                            name=row['name'],
                            role=row['role'],
                            skills=skills,
                            certifications=person_certs,
                            availability_percentage=row['availability_percentage'],
                            hourly_rate=row['hourly_rate'],
                            department=row['department'],
                            max_concurrent_projects=row['max_concurrent_projects']
                        ))

            return available

    def calculate_utilization(
        self,
        resource_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate resource utilization for period

        Args:
            resource_id: Resource ID
            start_date: Period start
            end_date: Period end

        Returns:
            Utilization metrics
        """
        total_hours_available = (end_date - start_date).total_seconds() / 3600

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get bookings in period
            cursor.execute("""
                SELECT SUM(duration_hours) as total_booked, SUM(cost) as total_revenue
                FROM bookings
                WHERE resource_id = ?
                AND start_time >= ?
                AND end_time <= ?
                AND status NOT IN ('cancelled')
            """, (resource_id, start_date.isoformat(), end_date.isoformat()))

            row = cursor.fetchone()
            total_booked = row['total_booked'] or 0.0
            total_revenue = row['total_revenue'] or 0.0

            # Calculate completed hours
            cursor.execute("""
                SELECT SUM(duration_hours) as total_used
                FROM bookings
                WHERE resource_id = ?
                AND start_time >= ?
                AND end_time <= ?
                AND status = 'completed'
            """, (resource_id, start_date.isoformat(), end_date.isoformat()))

            row = cursor.fetchone()
            total_used = row['total_used'] or 0.0

            utilization_percentage = (total_booked / total_hours_available * 100) if total_hours_available > 0 else 0

            metrics = {
                'resource_id': resource_id,
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'total_hours_available': total_hours_available,
                'total_hours_booked': total_booked,
                'total_hours_used': total_used,
                'utilization_percentage': utilization_percentage,
                'revenue_generated': total_revenue
            }

            # Store metrics
            cursor.execute("""
                INSERT INTO utilization_metrics
                (metric_id, resource_id, period_start, period_end, total_hours_available,
                 total_hours_booked, total_hours_used, utilization_percentage, revenue_generated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                resource_id,
                start_date.isoformat(),
                end_date.isoformat(),
                total_hours_available,
                total_booked,
                total_used,
                utilization_percentage,
                total_revenue
            ))

            conn.commit()

            return metrics

    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get resource by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resources WHERE resource_id = ?", (resource_id,))
            row = cursor.fetchone()

            if row:
                return Resource(
                    resource_id=row['resource_id'],
                    name=row['name'],
                    resource_type=ResourceType(row['resource_type']),
                    status=ResourceStatus(row['status']),
                    location=row['location'],
                    capacity=row['capacity'],
                    unit=row['unit'],
                    cost_per_hour=row['cost_per_hour'],
                    metadata=json.loads(row['metadata']),
                    maintenance_schedule=json.loads(row['maintenance_schedule']),
                    certifications=json.loads(row['certifications'])
                )
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get resource scheduler statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Total resources
            cursor.execute("SELECT COUNT(*) as count FROM resources")
            stats['total_resources'] = cursor.fetchone()['count']

            # Resources by type
            cursor.execute("SELECT resource_type, COUNT(*) as count FROM resources GROUP BY resource_type")
            stats['resources_by_type'] = {row['resource_type']: row['count'] for row in cursor.fetchall()}

            # Active bookings
            cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status IN ('confirmed', 'in_use')")
            stats['active_bookings'] = cursor.fetchone()['count']

            # Total personnel
            cursor.execute("SELECT COUNT(*) as count FROM personnel")
            stats['total_personnel'] = cursor.fetchone()['count']

            return stats


if __name__ == "__main__":
    # Example usage
    scheduler = ResourceScheduler()

    # Add equipment
    equipment = scheduler.add_resource(
        name="Thermal Chamber TC-2000",
        resource_type=ResourceType.EQUIPMENT,
        location="Lab A",
        cost_per_hour=50.0,
        certifications=["ISO 17025"]
    )

    # Add personnel
    personnel = scheduler.add_personnel(
        name="John Doe",
        role="Test Engineer",
        skills=["thermal_testing", "data_analysis"],
        certifications=["ISO 17025 Certified"],
        hourly_rate=75.0
    )

    # Create booking
    booking = scheduler.create_booking(
        resource_id=equipment.resource_id,
        project_id="PRJ-001",
        booked_by="user123",
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc) + timedelta(hours=8),
        purpose="PVTP-048 Thermal Cycling Test",
        priority=8
    )

    print(f"Created booking: {booking.booking_id if booking else 'Failed'}")

    # Calculate utilization
    utilization = scheduler.calculate_utilization(
        resource_id=equipment.resource_id,
        start_date=datetime.now(timezone.utc) - timedelta(days=30),
        end_date=datetime.now(timezone.utc)
    )

    print(f"Utilization: {json.dumps(utilization, indent=2)}")
