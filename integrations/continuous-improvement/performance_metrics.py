"""
Performance Metrics
Performance metrics calculation, benchmarking, and goal tracking
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

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric types"""
    THROUGHPUT = "throughput"
    QUALITY = "quality"
    EFFICIENCY = "efficiency"
    COST = "cost"
    TIME = "time"
    UTILIZATION = "utilization"
    COMPLIANCE = "compliance"


class AggregationMethod(Enum):
    """Aggregation methods"""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    MEDIAN = "median"


@dataclass
class Metric:
    """Performance metric definition"""
    metric_id: str
    name: str
    description: str
    metric_type: MetricType
    unit: str
    aggregation_method: AggregationMethod
    formula: str
    data_sources: List[str] = field(default_factory=list)
    calculation_frequency: str = "daily"
    owner: str = ""
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric_id': self.metric_id,
            'name': self.name,
            'description': self.description,
            'metric_type': self.metric_type.value,
            'unit': self.unit,
            'aggregation_method': self.aggregation_method.value,
            'formula': self.formula,
            'data_sources': self.data_sources,
            'calculation_frequency': self.calculation_frequency,
            'owner': self.owner,
            'active': self.active,
            'metadata': self.metadata
        }


@dataclass
class Goal:
    """Performance goal"""
    goal_id: str
    metric_id: str
    target_value: float
    threshold_min: Optional[float]
    threshold_max: Optional[float]
    start_date: datetime
    end_date: datetime
    baseline_value: float
    current_value: float
    progress_percentage: float
    status: str  # on_track, at_risk, behind
    owner: str
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'goal_id': self.goal_id,
            'metric_id': self.metric_id,
            'target_value': self.target_value,
            'threshold_min': self.threshold_min,
            'threshold_max': self.threshold_max,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'baseline_value': self.baseline_value,
            'current_value': self.current_value,
            'progress_percentage': self.progress_percentage,
            'status': self.status,
            'owner': self.owner,
            'description': self.description,
            'metadata': self.metadata
        }


@dataclass
class Benchmark:
    """Performance benchmark"""
    benchmark_id: str
    metric_id: str
    benchmark_type: str  # internal, industry, best_practice
    benchmark_value: float
    source: str
    date_established: datetime
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'benchmark_id': self.benchmark_id,
            'metric_id': self.metric_id,
            'benchmark_type': self.benchmark_type,
            'benchmark_value': self.benchmark_value,
            'source': self.source,
            'date_established': self.date_established.isoformat(),
            'notes': self.notes,
            'metadata': self.metadata
        }


class PerformanceMetrics:
    """Performance metrics calculation and tracking system"""

    def __init__(self, db_path: str = "performance_metrics.db"):
        self.db_path = db_path
        self._initialize_database()
        logger.info(f"PerformanceMetrics initialized with database: {db_path}")

    @contextmanager
    def _get_connection(self):
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
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    metric_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    metric_type TEXT NOT NULL,
                    unit TEXT NOT NULL,
                    aggregation_method TEXT NOT NULL,
                    formula TEXT,
                    data_sources TEXT,
                    calculation_frequency TEXT,
                    owner TEXT,
                    active INTEGER DEFAULT 1,
                    metadata TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metric_values (
                    value_id TEXT PRIMARY KEY,
                    metric_id TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    period_start TEXT,
                    period_end TEXT,
                    calculated_by TEXT,
                    metadata TEXT,
                    FOREIGN KEY (metric_id) REFERENCES metrics(metric_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    goal_id TEXT PRIMARY KEY,
                    metric_id TEXT NOT NULL,
                    target_value REAL NOT NULL,
                    threshold_min REAL,
                    threshold_max REAL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    baseline_value REAL,
                    current_value REAL,
                    progress_percentage REAL,
                    status TEXT,
                    owner TEXT,
                    description TEXT,
                    metadata TEXT,
                    FOREIGN KEY (metric_id) REFERENCES metrics(metric_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS benchmarks (
                    benchmark_id TEXT PRIMARY KEY,
                    metric_id TEXT NOT NULL,
                    benchmark_type TEXT NOT NULL,
                    benchmark_value REAL NOT NULL,
                    source TEXT,
                    date_established TEXT NOT NULL,
                    notes TEXT,
                    metadata TEXT,
                    FOREIGN KEY (metric_id) REFERENCES metrics(metric_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_scorecards (
                    scorecard_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    period_start TEXT NOT NULL,
                    period_end TEXT NOT NULL,
                    metrics TEXT,
                    overall_score REAL,
                    generated_at TEXT NOT NULL,
                    generated_by TEXT
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metric_type ON metrics(metric_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_value_timestamp ON metric_values(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_goal_status ON goals(status)")

            logger.info("Performance metrics database schema initialized")

    def define_metric(
        self,
        name: str,
        description: str,
        metric_type: MetricType,
        unit: str,
        aggregation_method: AggregationMethod,
        formula: str = "",
        data_sources: Optional[List[str]] = None,
        calculation_frequency: str = "daily",
        owner: str = "",
        metadata: Optional[Dict] = None
    ) -> Metric:
        """Define a new performance metric"""
        metric = Metric(
            metric_id=str(uuid.uuid4()),
            name=name,
            description=description,
            metric_type=metric_type,
            unit=unit,
            aggregation_method=aggregation_method,
            formula=formula,
            data_sources=data_sources or [],
            calculation_frequency=calculation_frequency,
            owner=owner,
            active=True,
            metadata=metadata or {}
        )

        self._store_metric(metric)
        logger.info(f"Defined metric: {metric.name}")
        return metric

    def _store_metric(self, metric: Metric):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO metrics
                (metric_id, name, description, metric_type, unit, aggregation_method,
                 formula, data_sources, calculation_frequency, owner, active, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.metric_id,
                metric.name,
                metric.description,
                metric.metric_type.value,
                metric.unit,
                metric.aggregation_method.value,
                metric.formula,
                json.dumps(metric.data_sources),
                metric.calculation_frequency,
                metric.owner,
                1 if metric.active else 0,
                json.dumps(metric.metadata)
            ))

    def record_metric_value(
        self,
        metric_id: str,
        value: float,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        calculated_by: str = "",
        metadata: Optional[Dict] = None
    ):
        """Record a metric value"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO metric_values
                (value_id, metric_id, value, timestamp, period_start, period_end,
                 calculated_by, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                metric_id,
                value,
                datetime.now(timezone.utc).isoformat(),
                period_start.isoformat() if period_start else None,
                period_end.isoformat() if period_end else None,
                calculated_by,
                json.dumps(metadata or {})
            ))

    def create_goal(
        self,
        metric_id: str,
        target_value: float,
        start_date: datetime,
        end_date: datetime,
        owner: str,
        description: str = "",
        threshold_min: Optional[float] = None,
        threshold_max: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> Goal:
        """Create a performance goal"""
        # Get current value
        current_value = self._get_latest_metric_value(metric_id)
        baseline_value = current_value

        goal = Goal(
            goal_id=str(uuid.uuid4()),
            metric_id=metric_id,
            target_value=target_value,
            threshold_min=threshold_min,
            threshold_max=threshold_max,
            start_date=start_date,
            end_date=end_date,
            baseline_value=baseline_value,
            current_value=current_value,
            progress_percentage=0.0,
            status="on_track",
            owner=owner,
            description=description,
            metadata=metadata or {}
        )

        self._store_goal(goal)
        logger.info(f"Created goal: {goal.goal_id}")
        return goal

    def _store_goal(self, goal: Goal):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO goals
                (goal_id, metric_id, target_value, threshold_min, threshold_max,
                 start_date, end_date, baseline_value, current_value, progress_percentage,
                 status, owner, description, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                goal.goal_id,
                goal.metric_id,
                goal.target_value,
                goal.threshold_min,
                goal.threshold_max,
                goal.start_date.isoformat(),
                goal.end_date.isoformat(),
                goal.baseline_value,
                goal.current_value,
                goal.progress_percentage,
                goal.status,
                goal.owner,
                goal.description,
                json.dumps(goal.metadata)
            ))

    def update_goal_progress(self, goal_id: str):
        """Update goal progress"""
        goal = self.get_goal(goal_id)
        if not goal:
            return

        # Get current value
        current_value = self._get_latest_metric_value(goal.metric_id)
        goal.current_value = current_value

        # Calculate progress
        if goal.target_value != goal.baseline_value:
            goal.progress_percentage = (
                (current_value - goal.baseline_value) /
                (goal.target_value - goal.baseline_value) * 100
            )
        else:
            goal.progress_percentage = 100.0 if current_value >= goal.target_value else 0.0

        # Update status
        if goal.progress_percentage >= 100:
            goal.status = "achieved"
        elif goal.progress_percentage >= 75:
            goal.status = "on_track"
        elif goal.progress_percentage >= 50:
            goal.status = "at_risk"
        else:
            goal.status = "behind"

        self._store_goal(goal)

    def create_benchmark(
        self,
        metric_id: str,
        benchmark_type: str,
        benchmark_value: float,
        source: str,
        notes: str = "",
        metadata: Optional[Dict] = None
    ) -> Benchmark:
        """Create a benchmark"""
        benchmark = Benchmark(
            benchmark_id=str(uuid.uuid4()),
            metric_id=metric_id,
            benchmark_type=benchmark_type,
            benchmark_value=benchmark_value,
            source=source,
            date_established=datetime.now(timezone.utc),
            notes=notes,
            metadata=metadata or {}
        )

        self._store_benchmark(benchmark)
        logger.info(f"Created benchmark: {benchmark.benchmark_id}")
        return benchmark

    def _store_benchmark(self, benchmark: Benchmark):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO benchmarks
                (benchmark_id, metric_id, benchmark_type, benchmark_value, source,
                 date_established, notes, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                benchmark.benchmark_id,
                benchmark.metric_id,
                benchmark.benchmark_type,
                benchmark.benchmark_value,
                benchmark.source,
                benchmark.date_established.isoformat(),
                benchmark.notes,
                json.dumps(benchmark.metadata)
            ))

    def generate_scorecard(
        self,
        name: str,
        metric_ids: List[str],
        period_start: datetime,
        period_end: datetime,
        generated_by: str = ""
    ) -> Dict[str, Any]:
        """Generate performance scorecard"""
        scorecard = {
            'scorecard_id': str(uuid.uuid4()),
            'name': name,
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat(),
            'metrics': [],
            'overall_score': 0.0,
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'generated_by': generated_by
        }

        scores = []

        for metric_id in metric_ids:
            metric = self.get_metric(metric_id)
            if not metric:
                continue

            # Get metric values in period
            values = self._get_metric_values_in_period(
                metric_id, period_start, period_end
            )

            if not values:
                continue

            # Calculate metric score
            avg_value = np.mean(values)

            # Get goal for this metric
            goal = self._get_active_goal_for_metric(metric_id)

            metric_score = {
                'metric_id': metric_id,
                'metric_name': metric.name,
                'average_value': float(avg_value),
                'unit': metric.unit,
                'data_points': len(values),
                'goal_target': goal.target_value if goal else None,
                'goal_progress': goal.progress_percentage if goal else None,
                'score': 0.0
            }

            # Calculate score (0-100)
            if goal:
                if goal.progress_percentage >= 100:
                    metric_score['score'] = 100.0
                else:
                    metric_score['score'] = min(100.0, goal.progress_percentage)

                scores.append(metric_score['score'])

            scorecard['metrics'].append(metric_score)

        # Calculate overall score
        if scores:
            scorecard['overall_score'] = float(np.mean(scores))

        # Store scorecard
        self._store_scorecard(scorecard)

        return scorecard

    def _store_scorecard(self, scorecard: Dict):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO performance_scorecards
                (scorecard_id, name, description, period_start, period_end, metrics,
                 overall_score, generated_at, generated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scorecard['scorecard_id'],
                scorecard['name'],
                "",
                scorecard['period_start'],
                scorecard['period_end'],
                json.dumps(scorecard['metrics']),
                scorecard['overall_score'],
                scorecard['generated_at'],
                scorecard['generated_by']
            ))

    def _get_latest_metric_value(self, metric_id: str) -> float:
        """Get latest metric value"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT value FROM metric_values
                WHERE metric_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (metric_id,))

            row = cursor.fetchone()
            return row['value'] if row else 0.0

    def _get_metric_values_in_period(
        self,
        metric_id: str,
        start: datetime,
        end: datetime
    ) -> List[float]:
        """Get metric values in period"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT value FROM metric_values
                WHERE metric_id = ?
                AND timestamp >= ?
                AND timestamp <= ?
                ORDER BY timestamp ASC
            """, (metric_id, start.isoformat(), end.isoformat()))

            return [row['value'] for row in cursor.fetchall()]

    def _get_active_goal_for_metric(self, metric_id: str) -> Optional[Goal]:
        """Get active goal for metric"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM goals
                WHERE metric_id = ?
                AND status != 'achieved'
                ORDER BY end_date DESC
                LIMIT 1
            """, (metric_id,))

            row = cursor.fetchone()
            if row:
                return Goal(
                    goal_id=row['goal_id'],
                    metric_id=row['metric_id'],
                    target_value=row['target_value'],
                    threshold_min=row['threshold_min'],
                    threshold_max=row['threshold_max'],
                    start_date=datetime.fromisoformat(row['start_date']),
                    end_date=datetime.fromisoformat(row['end_date']),
                    baseline_value=row['baseline_value'],
                    current_value=row['current_value'],
                    progress_percentage=row['progress_percentage'],
                    status=row['status'],
                    owner=row['owner'],
                    description=row['description'],
                    metadata=json.loads(row['metadata'])
                )
        return None

    def get_metric(self, metric_id: str) -> Optional[Metric]:
        """Get metric by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM metrics WHERE metric_id = ?", (metric_id,))
            row = cursor.fetchone()

            if row:
                return Metric(
                    metric_id=row['metric_id'],
                    name=row['name'],
                    description=row['description'],
                    metric_type=MetricType(row['metric_type']),
                    unit=row['unit'],
                    aggregation_method=AggregationMethod(row['aggregation_method']),
                    formula=row['formula'],
                    data_sources=json.loads(row['data_sources']),
                    calculation_frequency=row['calculation_frequency'],
                    owner=row['owner'],
                    active=bool(row['active']),
                    metadata=json.loads(row['metadata'])
                )
        return None

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get goal by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM goals WHERE goal_id = ?", (goal_id,))
            row = cursor.fetchone()

            if row:
                return Goal(
                    goal_id=row['goal_id'],
                    metric_id=row['metric_id'],
                    target_value=row['target_value'],
                    threshold_min=row['threshold_min'],
                    threshold_max=row['threshold_max'],
                    start_date=datetime.fromisoformat(row['start_date']),
                    end_date=datetime.fromisoformat(row['end_date']),
                    baseline_value=row['baseline_value'],
                    current_value=row['current_value'],
                    progress_percentage=row['progress_percentage'],
                    status=row['status'],
                    owner=row['owner'],
                    description=row['description'],
                    metadata=json.loads(row['metadata'])
                )
        return None


if __name__ == "__main__":
    pm = PerformanceMetrics()

    # Define metric
    metric = pm.define_metric(
        name="Test Throughput",
        description="Number of tests completed per day",
        metric_type=MetricType.THROUGHPUT,
        unit="tests/day",
        aggregation_method=AggregationMethod.SUM,
        owner="ops001"
    )

    # Record values
    for i in range(10):
        pm.record_metric_value(metric.metric_id, 15 + i * 0.5)

    # Create goal
    goal = pm.create_goal(
        metric_id=metric.metric_id,
        target_value=25.0,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=90),
        owner="ops001",
        description="Increase throughput to 25 tests/day"
    )

    # Generate scorecard
    scorecard = pm.generate_scorecard(
        name="Q1 2025 Performance",
        metric_ids=[metric.metric_id],
        period_start=datetime.now(timezone.utc) - timedelta(days=30),
        period_end=datetime.now(timezone.utc),
        generated_by="manager001"
    )

    print(f"Overall score: {scorecard['overall_score']:.1f}%")
