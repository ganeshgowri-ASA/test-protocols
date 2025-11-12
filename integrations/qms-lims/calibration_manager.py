"""
Calibration Manager
Equipment calibration tracking, due date management, and certificate storage
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


class CalibrationStatus(Enum):
    """Calibration status"""
    CURRENT = "current"
    DUE_SOON = "due_soon"
    OVERDUE = "overdue"
    IN_CALIBRATION = "in_calibration"
    FAILED = "failed"


class EquipmentStatus(Enum):
    """Equipment operational status"""
    OPERATIONAL = "operational"
    OUT_OF_SERVICE = "out_of_service"
    IN_CALIBRATION = "in_calibration"
    UNDER_REPAIR = "under_repair"
    RETIRED = "retired"


@dataclass
class Equipment:
    """Equipment record"""
    equipment_id: str
    asset_number: str
    name: str
    manufacturer: str
    model: str
    serial_number: str
    location: str
    department: str
    purchase_date: datetime
    status: EquipmentStatus
    calibration_interval_days: int = 365
    last_calibration_date: Optional[datetime] = None
    next_calibration_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'equipment_id': self.equipment_id,
            'asset_number': self.asset_number,
            'name': self.name,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'serial_number': self.serial_number,
            'location': self.location,
            'department': self.department,
            'purchase_date': self.purchase_date.isoformat(),
            'status': self.status.value,
            'calibration_interval_days': self.calibration_interval_days,
            'last_calibration_date': self.last_calibration_date.isoformat() if self.last_calibration_date else None,
            'next_calibration_date': self.next_calibration_date.isoformat() if self.next_calibration_date else None,
            'metadata': self.metadata
        }


@dataclass
class CalibrationRecord:
    """Calibration record"""
    calibration_id: str
    equipment_id: str
    calibration_date: datetime
    calibration_due_date: datetime
    performed_by: str
    calibration_lab: str
    certificate_number: str
    certificate_path: str
    status: str  # pass, fail, conditional
    results: Dict[str, Any] = field(default_factory=dict)
    deviations: List[str] = field(default_factory=list)
    standards_used: List[str] = field(default_factory=list)
    environmental_conditions: Dict[str, Any] = field(default_factory=dict)
    next_calibration_date: datetime = None
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'calibration_id': self.calibration_id,
            'equipment_id': self.equipment_id,
            'calibration_date': self.calibration_date.isoformat(),
            'calibration_due_date': self.calibration_due_date.isoformat(),
            'performed_by': self.performed_by,
            'calibration_lab': self.calibration_lab,
            'certificate_number': self.certificate_number,
            'certificate_path': self.certificate_path,
            'status': self.status,
            'results': self.results,
            'deviations': self.deviations,
            'standards_used': self.standards_used,
            'environmental_conditions': self.environmental_conditions,
            'next_calibration_date': self.next_calibration_date.isoformat() if self.next_calibration_date else None,
            'notes': self.notes,
            'metadata': self.metadata
        }


class CalibrationManager:
    """
    Comprehensive calibration management system
    """

    def __init__(self, db_path: str = "calibration.db"):
        """Initialize calibration manager"""
        self.db_path = db_path
        self._initialize_database()
        logger.info(f"CalibrationManager initialized with database: {db_path}")

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
                CREATE TABLE IF NOT EXISTS equipment (
                    equipment_id TEXT PRIMARY KEY,
                    asset_number TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    manufacturer TEXT,
                    model TEXT,
                    serial_number TEXT,
                    location TEXT,
                    department TEXT,
                    purchase_date TEXT,
                    status TEXT NOT NULL,
                    calibration_interval_days INTEGER DEFAULT 365,
                    last_calibration_date TEXT,
                    next_calibration_date TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calibration_records (
                    calibration_id TEXT PRIMARY KEY,
                    equipment_id TEXT NOT NULL,
                    calibration_date TEXT NOT NULL,
                    calibration_due_date TEXT NOT NULL,
                    performed_by TEXT NOT NULL,
                    calibration_lab TEXT,
                    certificate_number TEXT,
                    certificate_path TEXT,
                    status TEXT NOT NULL,
                    results TEXT,
                    deviations TEXT,
                    standards_used TEXT,
                    environmental_conditions TEXT,
                    next_calibration_date TEXT,
                    notes TEXT,
                    metadata TEXT,
                    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calibration_alerts (
                    alert_id TEXT PRIMARY KEY,
                    equipment_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    alert_date TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    days_until_due INTEGER,
                    acknowledged INTEGER DEFAULT 0,
                    acknowledged_by TEXT,
                    acknowledged_date TEXT,
                    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_equip_status ON equipment(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cal_next_date ON equipment(next_calibration_date)")

            logger.info("Calibration database schema initialized")

    def register_equipment(
        self,
        asset_number: str,
        name: str,
        manufacturer: str,
        model: str,
        serial_number: str,
        location: str,
        department: str,
        calibration_interval_days: int = 365,
        metadata: Optional[Dict] = None
    ) -> Equipment:
        """Register new equipment"""
        equipment = Equipment(
            equipment_id=str(uuid.uuid4()),
            asset_number=asset_number,
            name=name,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number,
            location=location,
            department=department,
            purchase_date=datetime.now(timezone.utc),
            status=EquipmentStatus.OPERATIONAL,
            calibration_interval_days=calibration_interval_days,
            last_calibration_date=None,
            next_calibration_date=datetime.now(timezone.utc) + timedelta(days=calibration_interval_days),
            metadata=metadata or {}
        )

        self._store_equipment(equipment)
        logger.info(f"Registered equipment: {equipment.asset_number}")
        return equipment

    def _store_equipment(self, equipment: Equipment):
        """Store equipment in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO equipment
                (equipment_id, asset_number, name, manufacturer, model, serial_number,
                 location, department, purchase_date, status, calibration_interval_days,
                 last_calibration_date, next_calibration_date, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                equipment.equipment_id,
                equipment.asset_number,
                equipment.name,
                equipment.manufacturer,
                equipment.model,
                equipment.serial_number,
                equipment.location,
                equipment.department,
                equipment.purchase_date.isoformat(),
                equipment.status.value,
                equipment.calibration_interval_days,
                equipment.last_calibration_date.isoformat() if equipment.last_calibration_date else None,
                equipment.next_calibration_date.isoformat() if equipment.next_calibration_date else None,
                json.dumps(equipment.metadata)
            ))

    def record_calibration(
        self,
        equipment_id: str,
        performed_by: str,
        calibration_lab: str,
        certificate_number: str,
        certificate_path: str,
        status: str,
        results: Optional[Dict] = None,
        deviations: Optional[List[str]] = None,
        notes: str = "",
        metadata: Optional[Dict] = None
    ) -> CalibrationRecord:
        """Record calibration"""
        equipment = self.get_equipment(equipment_id)
        if not equipment:
            raise ValueError(f"Equipment not found: {equipment_id}")

        calibration_date = datetime.now(timezone.utc)
        next_cal_date = calibration_date + timedelta(days=equipment.calibration_interval_days)

        record = CalibrationRecord(
            calibration_id=str(uuid.uuid4()),
            equipment_id=equipment_id,
            calibration_date=calibration_date,
            calibration_due_date=equipment.next_calibration_date or calibration_date,
            performed_by=performed_by,
            calibration_lab=calibration_lab,
            certificate_number=certificate_number,
            certificate_path=certificate_path,
            status=status,
            results=results or {},
            deviations=deviations or [],
            standards_used=[],
            environmental_conditions={},
            next_calibration_date=next_cal_date,
            notes=notes,
            metadata=metadata or {}
        )

        self._store_calibration(record)

        # Update equipment
        equipment.last_calibration_date = calibration_date
        equipment.next_calibration_date = next_cal_date
        self._store_equipment(equipment)

        logger.info(f"Recorded calibration: {record.calibration_id}")
        return record

    def _store_calibration(self, record: CalibrationRecord):
        """Store calibration record"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO calibration_records
                (calibration_id, equipment_id, calibration_date, calibration_due_date,
                 performed_by, calibration_lab, certificate_number, certificate_path,
                 status, results, deviations, standards_used, environmental_conditions,
                 next_calibration_date, notes, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.calibration_id,
                record.equipment_id,
                record.calibration_date.isoformat(),
                record.calibration_due_date.isoformat(),
                record.performed_by,
                record.calibration_lab,
                record.certificate_number,
                record.certificate_path,
                record.status,
                json.dumps(record.results),
                json.dumps(record.deviations),
                json.dumps(record.standards_used),
                json.dumps(record.environmental_conditions),
                record.next_calibration_date.isoformat() if record.next_calibration_date else None,
                record.notes,
                json.dumps(record.metadata)
            ))

    def check_calibration_status(self, equipment_id: str) -> CalibrationStatus:
        """Check equipment calibration status"""
        equipment = self.get_equipment(equipment_id)
        if not equipment or not equipment.next_calibration_date:
            return CalibrationStatus.OVERDUE

        days_until_due = (equipment.next_calibration_date - datetime.now(timezone.utc)).days

        if days_until_due < 0:
            return CalibrationStatus.OVERDUE
        elif days_until_due <= 30:
            return CalibrationStatus.DUE_SOON
        else:
            return CalibrationStatus.CURRENT

    def get_due_calibrations(self, days_ahead: int = 30) -> List[Equipment]:
        """Get equipment with calibrations due"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            threshold_date = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).isoformat()

            cursor.execute("""
                SELECT * FROM equipment
                WHERE next_calibration_date <= ?
                AND status != 'retired'
                ORDER BY next_calibration_date ASC
            """, (threshold_date,))

            equipment_list = []
            for row in cursor.fetchall():
                equipment_list.append(Equipment(
                    equipment_id=row['equipment_id'],
                    asset_number=row['asset_number'],
                    name=row['name'],
                    manufacturer=row['manufacturer'],
                    model=row['model'],
                    serial_number=row['serial_number'],
                    location=row['location'],
                    department=row['department'],
                    purchase_date=datetime.fromisoformat(row['purchase_date']),
                    status=EquipmentStatus(row['status']),
                    calibration_interval_days=row['calibration_interval_days'],
                    last_calibration_date=datetime.fromisoformat(row['last_calibration_date']) if row['last_calibration_date'] else None,
                    next_calibration_date=datetime.fromisoformat(row['next_calibration_date']) if row['next_calibration_date'] else None,
                    metadata=json.loads(row['metadata'])
                ))

            return equipment_list

    def get_equipment(self, equipment_id: str) -> Optional[Equipment]:
        """Get equipment by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM equipment WHERE equipment_id = ?", (equipment_id,))
            row = cursor.fetchone()

            if row:
                return Equipment(
                    equipment_id=row['equipment_id'],
                    asset_number=row['asset_number'],
                    name=row['name'],
                    manufacturer=row['manufacturer'],
                    model=row['model'],
                    serial_number=row['serial_number'],
                    location=row['location'],
                    department=row['department'],
                    purchase_date=datetime.fromisoformat(row['purchase_date']),
                    status=EquipmentStatus(row['status']),
                    calibration_interval_days=row['calibration_interval_days'],
                    last_calibration_date=datetime.fromisoformat(row['last_calibration_date']) if row['last_calibration_date'] else None,
                    next_calibration_date=datetime.fromisoformat(row['next_calibration_date']) if row['next_calibration_date'] else None,
                    metadata=json.loads(row['metadata'])
                )
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get calibration statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            cursor.execute("SELECT COUNT(*) as count FROM equipment WHERE status != 'retired'")
            stats['total_equipment'] = cursor.fetchone()['count']

            cursor.execute("""
                SELECT COUNT(*) as count FROM equipment
                WHERE next_calibration_date <= ? AND status != 'retired'
            """, (datetime.now(timezone.utc).isoformat(),))
            stats['overdue_calibrations'] = cursor.fetchone()['count']

            cursor.execute("""
                SELECT COUNT(*) as count FROM equipment
                WHERE next_calibration_date BETWEEN ? AND ?
                AND status != 'retired'
            """, (
                datetime.now(timezone.utc).isoformat(),
                (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
            ))
            stats['due_soon'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM calibration_records")
            stats['total_calibrations'] = cursor.fetchone()['count']

            return stats


if __name__ == "__main__":
    cal_mgr = CalibrationManager()

    equipment = cal_mgr.register_equipment(
        asset_number="TC-2000",
        name="Thermal Chamber",
        manufacturer="TestEquip Inc",
        model="TC-2000",
        serial_number="TC2000-12345",
        location="Lab A",
        department="Testing",
        calibration_interval_days=365
    )

    print(f"Registered equipment: {equipment.asset_number}")

    record = cal_mgr.record_calibration(
        equipment_id=equipment.equipment_id,
        performed_by="Cal Tech 001",
        calibration_lab="Certified Cal Lab",
        certificate_number="CAL-2025-001",
        certificate_path="/certs/cal-2025-001.pdf",
        status="pass",
        results={'temperature_accuracy': 0.5, 'humidity_accuracy': 2.0}
    )

    print(f"Calibration status: {cal_mgr.check_calibration_status(equipment.equipment_id).value}")
