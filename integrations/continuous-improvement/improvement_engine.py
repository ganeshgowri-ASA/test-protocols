"""
Improvement Engine
Continuous improvement tracking, KPI monitoring, and trend analysis
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
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class ImprovementType(Enum):
    """Types of improvements"""
    PROCESS = "process"
    QUALITY = "quality"
    EFFICIENCY = "efficiency"
    COST = "cost"
    SAFETY = "safety"
    DOCUMENTATION = "documentation"


class ImprovementStatus(Enum):
    """Improvement initiative status"""
    PROPOSED = "proposed"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    REJECTED = "rejected"
    CLOSED = "closed"


class TrendDirection(Enum):
    """Trend direction"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"


@dataclass
class ImprovementInitiative:
    """Improvement initiative record"""
    initiative_id: str
    title: str
    description: str
    improvement_type: ImprovementType
    status: ImprovementStatus
    proposed_by: str
    proposed_date: datetime
    current_state: str
    desired_state: str
    benefits: List[str] = field(default_factory=list)
    estimated_cost: float = 0.0
    estimated_effort_hours: float = 0.0
    roi_months: Optional[float] = None
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    implementation_start: Optional[datetime] = None
    implementation_end: Optional[datetime] = None
    actual_cost: float = 0.0
    actual_effort_hours: float = 0.0
    success_metrics: Dict[str, Any] = field(default_factory=dict)
    lessons_learned: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'initiative_id': self.initiative_id,
            'title': self.title,
            'description': self.description,
            'improvement_type': self.improvement_type.value,
            'status': self.status.value,
            'proposed_by': self.proposed_by,
            'proposed_date': self.proposed_date.isoformat(),
            'current_state': self.current_state,
            'desired_state': self.desired_state,
            'benefits': self.benefits,
            'estimated_cost': self.estimated_cost,
            'estimated_effort_hours': self.estimated_effort_hours,
            'roi_months': self.roi_months,
            'approved_by': self.approved_by,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'implementation_start': self.implementation_start.isoformat() if self.implementation_start else None,
            'implementation_end': self.implementation_end.isoformat() if self.implementation_end else None,
            'actual_cost': self.actual_cost,
            'actual_effort_hours': self.actual_effort_hours,
            'success_metrics': self.success_metrics,
            'lessons_learned': self.lessons_learned,
            'metadata': self.metadata
        }


@dataclass
class KPI:
    """Key Performance Indicator"""
    kpi_id: str
    name: str
    description: str
    category: str
    unit: str
    target_value: float
    target_operator: str  # >=, <=, ==
    current_value: float
    measurement_frequency: str  # daily, weekly, monthly
    data_source: str
    owner: str
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_meeting_target(self) -> bool:
        """Check if current value meets target"""
        if self.target_operator == ">=":
            return self.current_value >= self.target_value
        elif self.target_operator == "<=":
            return self.current_value <= self.target_value
        elif self.target_operator == "==":
            return abs(self.current_value - self.target_value) < 0.01
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'kpi_id': self.kpi_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'unit': self.unit,
            'target_value': self.target_value,
            'target_operator': self.target_operator,
            'current_value': self.current_value,
            'measurement_frequency': self.measurement_frequency,
            'data_source': self.data_source,
            'owner': self.owner,
            'active': self.active,
            'metadata': self.metadata
        }


@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    kpi_id: str
    analysis_date: datetime
    trend_direction: TrendDirection
    trend_strength: float  # 0-1
    data_points: int
    mean_value: float
    std_deviation: float
    change_rate: float  # Per period
    forecast_next_period: float
    confidence: float  # 0-1
    insights: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'kpi_id': self.kpi_id,
            'analysis_date': self.analysis_date.isoformat(),
            'trend_direction': self.trend_direction.value,
            'trend_strength': self.trend_strength,
            'data_points': self.data_points,
            'mean_value': self.mean_value,
            'std_deviation': self.std_deviation,
            'change_rate': self.change_rate,
            'forecast_next_period': self.forecast_next_period,
            'confidence': self.confidence,
            'insights': self.insights
        }


class ImprovementEngine:
    """
    Continuous improvement tracking and KPI monitoring system
    """

    def __init__(self, db_path: str = "improvement.db"):
        """Initialize improvement engine"""
        self.db_path = db_path
        self._initialize_database()
        logger.info(f"ImprovementEngine initialized with database: {db_path}")

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
                CREATE TABLE IF NOT EXISTS improvement_initiatives (
                    initiative_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    improvement_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    proposed_by TEXT NOT NULL,
                    proposed_date TEXT NOT NULL,
                    current_state TEXT,
                    desired_state TEXT,
                    benefits TEXT,
                    estimated_cost REAL DEFAULT 0,
                    estimated_effort_hours REAL DEFAULT 0,
                    roi_months REAL,
                    approved_by TEXT,
                    approval_date TEXT,
                    implementation_start TEXT,
                    implementation_end TEXT,
                    actual_cost REAL DEFAULT 0,
                    actual_effort_hours REAL DEFAULT 0,
                    success_metrics TEXT,
                    lessons_learned TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kpis (
                    kpi_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    unit TEXT NOT NULL,
                    target_value REAL NOT NULL,
                    target_operator TEXT NOT NULL,
                    current_value REAL NOT NULL,
                    measurement_frequency TEXT,
                    data_source TEXT,
                    owner TEXT,
                    active INTEGER DEFAULT 1,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kpi_measurements (
                    measurement_id TEXT PRIMARY KEY,
                    kpi_id TEXT NOT NULL,
                    measurement_date TEXT NOT NULL,
                    value REAL NOT NULL,
                    notes TEXT,
                    measured_by TEXT,
                    FOREIGN KEY (kpi_id) REFERENCES kpis(kpi_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trend_analyses (
                    analysis_id TEXT PRIMARY KEY,
                    kpi_id TEXT NOT NULL,
                    analysis_date TEXT NOT NULL,
                    trend_direction TEXT NOT NULL,
                    trend_strength REAL,
                    data_points INTEGER,
                    mean_value REAL,
                    std_deviation REAL,
                    change_rate REAL,
                    forecast_next_period REAL,
                    confidence REAL,
                    insights TEXT,
                    FOREIGN KEY (kpi_id) REFERENCES kpis(kpi_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS improvement_impact (
                    impact_id TEXT PRIMARY KEY,
                    initiative_id TEXT NOT NULL,
                    kpi_id TEXT NOT NULL,
                    baseline_value REAL NOT NULL,
                    post_implementation_value REAL NOT NULL,
                    improvement_percentage REAL,
                    measurement_date TEXT NOT NULL,
                    FOREIGN KEY (initiative_id) REFERENCES improvement_initiatives(initiative_id),
                    FOREIGN KEY (kpi_id) REFERENCES kpis(kpi_id)
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_initiative_status ON improvement_initiatives(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_kpi_category ON kpis(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_measurement_date ON kpi_measurements(measurement_date)")

            logger.info("Improvement engine database schema initialized")

    def propose_improvement(
        self,
        title: str,
        description: str,
        improvement_type: ImprovementType,
        proposed_by: str,
        current_state: str,
        desired_state: str,
        benefits: List[str],
        estimated_cost: float = 0.0,
        estimated_effort_hours: float = 0.0,
        metadata: Optional[Dict] = None
    ) -> ImprovementInitiative:
        """Propose a new improvement initiative"""
        # Calculate ROI if savings are specified
        roi_months = None
        if estimated_cost > 0 and metadata and 'annual_savings' in metadata:
            annual_savings = metadata['annual_savings']
            roi_months = (estimated_cost / annual_savings) * 12 if annual_savings > 0 else None

        initiative = ImprovementInitiative(
            initiative_id=str(uuid.uuid4()),
            title=title,
            description=description,
            improvement_type=improvement_type,
            status=ImprovementStatus.PROPOSED,
            proposed_by=proposed_by,
            proposed_date=datetime.now(timezone.utc),
            current_state=current_state,
            desired_state=desired_state,
            benefits=benefits,
            estimated_cost=estimated_cost,
            estimated_effort_hours=estimated_effort_hours,
            roi_months=roi_months,
            approved_by=None,
            approval_date=None,
            implementation_start=None,
            implementation_end=None,
            actual_cost=0.0,
            actual_effort_hours=0.0,
            success_metrics={},
            lessons_learned="",
            metadata=metadata or {}
        )

        self._store_initiative(initiative)
        logger.info(f"Proposed improvement initiative: {initiative.initiative_id}")
        return initiative

    def _store_initiative(self, initiative: ImprovementInitiative):
        """Store improvement initiative"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO improvement_initiatives
                (initiative_id, title, description, improvement_type, status, proposed_by,
                 proposed_date, current_state, desired_state, benefits, estimated_cost,
                 estimated_effort_hours, roi_months, approved_by, approval_date,
                 implementation_start, implementation_end, actual_cost, actual_effort_hours,
                 success_metrics, lessons_learned, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                initiative.initiative_id,
                initiative.title,
                initiative.description,
                initiative.improvement_type.value,
                initiative.status.value,
                initiative.proposed_by,
                initiative.proposed_date.isoformat(),
                initiative.current_state,
                initiative.desired_state,
                json.dumps(initiative.benefits),
                initiative.estimated_cost,
                initiative.estimated_effort_hours,
                initiative.roi_months,
                initiative.approved_by,
                initiative.approval_date.isoformat() if initiative.approval_date else None,
                initiative.implementation_start.isoformat() if initiative.implementation_start else None,
                initiative.implementation_end.isoformat() if initiative.implementation_end else None,
                initiative.actual_cost,
                initiative.actual_effort_hours,
                json.dumps(initiative.success_metrics),
                initiative.lessons_learned,
                json.dumps(initiative.metadata)
            ))

    def create_kpi(
        self,
        name: str,
        description: str,
        category: str,
        unit: str,
        target_value: float,
        target_operator: str,
        current_value: float,
        measurement_frequency: str,
        data_source: str,
        owner: str,
        metadata: Optional[Dict] = None
    ) -> KPI:
        """Create a new KPI"""
        kpi = KPI(
            kpi_id=str(uuid.uuid4()),
            name=name,
            description=description,
            category=category,
            unit=unit,
            target_value=target_value,
            target_operator=target_operator,
            current_value=current_value,
            measurement_frequency=measurement_frequency,
            data_source=data_source,
            owner=owner,
            active=True,
            metadata=metadata or {}
        )

        self._store_kpi(kpi)
        logger.info(f"Created KPI: {kpi.kpi_id}")
        return kpi

    def _store_kpi(self, kpi: KPI):
        """Store KPI"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO kpis
                (kpi_id, name, description, category, unit, target_value, target_operator,
                 current_value, measurement_frequency, data_source, owner, active, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kpi.kpi_id,
                kpi.name,
                kpi.description,
                kpi.category,
                kpi.unit,
                kpi.target_value,
                kpi.target_operator,
                kpi.current_value,
                kpi.measurement_frequency,
                kpi.data_source,
                kpi.owner,
                1 if kpi.active else 0,
                json.dumps(kpi.metadata)
            ))

    def record_kpi_measurement(
        self,
        kpi_id: str,
        value: float,
        measured_by: str = "",
        notes: str = ""
    ):
        """Record a KPI measurement"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO kpi_measurements
                (measurement_id, kpi_id, measurement_date, value, notes, measured_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                kpi_id,
                datetime.now(timezone.utc).isoformat(),
                value,
                notes,
                measured_by
            ))

            # Update current value in KPI
            cursor.execute("""
                UPDATE kpis SET current_value = ? WHERE kpi_id = ?
            """, (value, kpi_id))

    def analyze_trend(
        self,
        kpi_id: str,
        periods: int = 30
    ) -> TrendAnalysis:
        """Analyze KPI trend"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT value, measurement_date FROM kpi_measurements
                WHERE kpi_id = ?
                ORDER BY measurement_date DESC
                LIMIT ?
            """, (kpi_id, periods))

            measurements = cursor.fetchall()

            if len(measurements) < 3:
                # Not enough data for trend analysis
                return TrendAnalysis(
                    kpi_id=kpi_id,
                    analysis_date=datetime.now(timezone.utc),
                    trend_direction=TrendDirection.STABLE,
                    trend_strength=0.0,
                    data_points=len(measurements),
                    mean_value=measurements[0]['value'] if measurements else 0.0,
                    std_deviation=0.0,
                    change_rate=0.0,
                    forecast_next_period=measurements[0]['value'] if measurements else 0.0,
                    confidence=0.0,
                    insights=["Insufficient data for trend analysis"]
                )

            values = np.array([m['value'] for m in reversed(measurements)])
            mean_value = float(np.mean(values))
            std_deviation = float(np.std(values))

            # Linear regression for trend
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)

            # Determine trend direction
            cv = std_deviation / mean_value if mean_value != 0 else 0

            if abs(slope) < 0.01 * mean_value:
                trend_direction = TrendDirection.STABLE
            elif slope > 0:
                trend_direction = TrendDirection.IMPROVING
            else:
                trend_direction = TrendDirection.DECLINING

            if cv > 0.2:  # High coefficient of variation
                trend_direction = TrendDirection.VOLATILE

            # Forecast next period
            forecast = slope * len(values) + intercept

            # Calculate confidence
            r_squared = 1 - (np.sum((values - (slope * x + intercept)) ** 2) / np.sum((values - mean_value) ** 2))
            confidence = float(max(0, min(1, r_squared)))

            # Generate insights
            insights = []
            if trend_direction == TrendDirection.IMPROVING:
                insights.append(f"Positive trend observed with {slope:.2f} {kpi.unit}/period improvement rate")
            elif trend_direction == TrendDirection.DECLINING:
                insights.append(f"Declining trend with {abs(slope):.2f} {kpi.unit}/period degradation rate")
            elif trend_direction == TrendDirection.VOLATILE:
                insights.append(f"High variability detected (CV: {cv:.2%})")

            analysis = TrendAnalysis(
                kpi_id=kpi_id,
                analysis_date=datetime.now(timezone.utc),
                trend_direction=trend_direction,
                trend_strength=float(abs(slope)),
                data_points=len(values),
                mean_value=mean_value,
                std_deviation=std_deviation,
                change_rate=float(slope),
                forecast_next_period=float(forecast),
                confidence=confidence,
                insights=insights
            )

            self._store_trend_analysis(analysis)
            return analysis

    def _store_trend_analysis(self, analysis: TrendAnalysis):
        """Store trend analysis"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO trend_analyses
                (analysis_id, kpi_id, analysis_date, trend_direction, trend_strength,
                 data_points, mean_value, std_deviation, change_rate, forecast_next_period,
                 confidence, insights)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                analysis.kpi_id,
                analysis.analysis_date.isoformat(),
                analysis.trend_direction.value,
                analysis.trend_strength,
                analysis.data_points,
                analysis.mean_value,
                analysis.std_deviation,
                analysis.change_rate,
                analysis.forecast_next_period,
                analysis.confidence,
                json.dumps(analysis.insights)
            ))

    def get_kpi_dashboard(self) -> Dict[str, Any]:
        """Get KPI dashboard data"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM kpis WHERE active = 1")

            dashboard = {
                'total_kpis': 0,
                'meeting_target': 0,
                'not_meeting_target': 0,
                'kpis_by_category': {},
                'kpis': []
            }

            for row in cursor.fetchall():
                kpi = KPI(
                    kpi_id=row['kpi_id'],
                    name=row['name'],
                    description=row['description'],
                    category=row['category'],
                    unit=row['unit'],
                    target_value=row['target_value'],
                    target_operator=row['target_operator'],
                    current_value=row['current_value'],
                    measurement_frequency=row['measurement_frequency'],
                    data_source=row['data_source'],
                    owner=row['owner'],
                    active=bool(row['active']),
                    metadata=json.loads(row['metadata'])
                )

                dashboard['total_kpis'] += 1
                if kpi.is_meeting_target():
                    dashboard['meeting_target'] += 1
                else:
                    dashboard['not_meeting_target'] += 1

                category = kpi.category
                if category not in dashboard['kpis_by_category']:
                    dashboard['kpis_by_category'][category] = 0
                dashboard['kpis_by_category'][category] += 1

                dashboard['kpis'].append(kpi.to_dict())

            return dashboard

    def get_statistics(self) -> Dict[str, Any]:
        """Get improvement engine statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            cursor.execute("SELECT status, COUNT(*) as count FROM improvement_initiatives GROUP BY status")
            stats['initiatives_by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}

            cursor.execute("SELECT COUNT(*) as count FROM kpis WHERE active = 1")
            stats['active_kpis'] = cursor.fetchone()['count']

            cursor.execute("SELECT SUM(actual_cost) as total FROM improvement_initiatives WHERE status = 'implemented'")
            stats['total_improvement_investment'] = cursor.fetchone()['total'] or 0

            return stats


if __name__ == "__main__":
    engine = ImprovementEngine()

    # Create KPI
    kpi = engine.create_kpi(
        name="Test Completion Rate",
        description="Percentage of tests completed on time",
        category="Quality",
        unit="%",
        target_value=95.0,
        target_operator=">=",
        current_value=92.5,
        measurement_frequency="weekly",
        data_source="LIMS",
        owner="QM001"
    )

    # Record measurements
    for i in range(10):
        engine.record_kpi_measurement(kpi.kpi_id, 92.0 + i * 0.5)

    # Analyze trend
    trend = engine.analyze_trend(kpi.kpi_id)
    print(f"Trend: {trend.trend_direction.value}, Forecast: {trend.forecast_next_period:.2f}")

    # Dashboard
    dashboard = engine.get_kpi_dashboard()
    print(f"KPIs meeting target: {dashboard['meeting_target']}/{dashboard['total_kpis']}")
