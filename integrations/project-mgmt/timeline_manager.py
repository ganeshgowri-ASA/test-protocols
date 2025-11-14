"""
Timeline Manager
Timeline tracking, critical path analysis, and delay prediction
"""

import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import sqlite3
from contextlib import contextmanager
import numpy as np

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    DELAYED = "delayed"


class DelayReason(Enum):
    """Reasons for delays"""
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    DEPENDENCY_DELAYED = "dependency_delayed"
    SCOPE_CHANGE = "scope_change"
    TECHNICAL_ISSUE = "technical_issue"
    WEATHER = "weather"
    PERSONNEL = "personnel"
    EQUIPMENT_FAILURE = "equipment_failure"
    OTHER = "other"


@dataclass
class Task:
    """Project task"""
    task_id: str
    name: str
    description: str
    project_id: str
    planned_start: datetime
    planned_end: datetime
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    duration_days: float
    status: TaskStatus
    dependencies: List[str] = field(default_factory=list)  # task_ids
    assigned_to: List[str] = field(default_factory=list)
    completion_percentage: float = 0.0
    is_milestone: bool = False
    is_critical: bool = False
    slack_days: float = 0.0  # Float for critical path
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'task_id': self.task_id,
            'name': self.name,
            'description': self.description,
            'project_id': self.project_id,
            'planned_start': self.planned_start.isoformat(),
            'planned_end': self.planned_end.isoformat(),
            'actual_start': self.actual_start.isoformat() if self.actual_start else None,
            'actual_end': self.actual_end.isoformat() if self.actual_end else None,
            'duration_days': self.duration_days,
            'status': self.status.value,
            'dependencies': self.dependencies,
            'assigned_to': self.assigned_to,
            'completion_percentage': self.completion_percentage,
            'is_milestone': self.is_milestone,
            'is_critical': self.is_critical,
            'slack_days': self.slack_days,
            'metadata': self.metadata
        }


@dataclass
class DelayRecord:
    """Delay tracking record"""
    delay_id: str
    task_id: str
    reason: DelayReason
    delay_days: float
    reported_date: datetime
    description: str
    impact_assessment: str
    mitigation_actions: List[str] = field(default_factory=list)
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'delay_id': self.delay_id,
            'task_id': self.task_id,
            'reason': self.reason.value,
            'delay_days': self.delay_days,
            'reported_date': self.reported_date.isoformat(),
            'description': self.description,
            'impact_assessment': self.impact_assessment,
            'mitigation_actions': self.mitigation_actions,
            'resolved': self.resolved
        }


@dataclass
class CriticalPath:
    """Critical path analysis result"""
    path_id: str
    project_id: str
    tasks: List[str]  # task_ids in order
    total_duration_days: float
    calculated_at: datetime
    project_end_date: datetime
    slack_available: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'path_id': self.path_id,
            'project_id': self.project_id,
            'tasks': self.tasks,
            'total_duration_days': self.total_duration_days,
            'calculated_at': self.calculated_at.isoformat(),
            'project_end_date': self.project_end_date.isoformat(),
            'slack_available': self.slack_available
        }


class TimelineManager:
    """
    Comprehensive timeline management with critical path analysis and delay prediction
    """

    def __init__(self, db_path: str = "timeline.db"):
        """
        Initialize timeline manager

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._initialize_database()
        logger.info(f"TimelineManager initialized with database: {db_path}")

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

            # Tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    project_id TEXT NOT NULL,
                    planned_start TEXT NOT NULL,
                    planned_end TEXT NOT NULL,
                    actual_start TEXT,
                    actual_end TEXT,
                    duration_days REAL NOT NULL,
                    status TEXT NOT NULL,
                    dependencies TEXT,
                    assigned_to TEXT,
                    completion_percentage REAL DEFAULT 0,
                    is_milestone INTEGER DEFAULT 0,
                    is_critical INTEGER DEFAULT 0,
                    slack_days REAL DEFAULT 0,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Delays table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS delays (
                    delay_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    delay_days REAL NOT NULL,
                    reported_date TEXT NOT NULL,
                    description TEXT,
                    impact_assessment TEXT,
                    mitigation_actions TEXT,
                    resolved INTEGER DEFAULT 0,
                    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
                )
            """)

            # Critical paths table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS critical_paths (
                    path_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    tasks TEXT NOT NULL,
                    total_duration_days REAL NOT NULL,
                    calculated_at TEXT NOT NULL,
                    project_end_date TEXT NOT NULL,
                    slack_available REAL DEFAULT 0
                )
            """)

            # Timeline snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS timeline_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    snapshot_date TEXT NOT NULL,
                    planned_completion TEXT NOT NULL,
                    forecasted_completion TEXT NOT NULL,
                    variance_days REAL,
                    confidence_score REAL,
                    snapshot_data TEXT
                )
            """)

            # Baseline timelines
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS baseline_timelines (
                    baseline_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    baseline_date TEXT NOT NULL,
                    baseline_name TEXT,
                    tasks_snapshot TEXT,
                    approved_by TEXT
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_project ON tasks(project_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_dates ON tasks(planned_start, planned_end)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_delay_task ON delays(task_id)")

            logger.info("Timeline manager database schema initialized")

    def create_task(
        self,
        project_id: str,
        name: str,
        description: str,
        planned_start: datetime,
        planned_end: datetime,
        dependencies: Optional[List[str]] = None,
        assigned_to: Optional[List[str]] = None,
        is_milestone: bool = False,
        metadata: Optional[Dict] = None
    ) -> Task:
        """
        Create a new task

        Args:
            project_id: Project ID
            name: Task name
            description: Task description
            planned_start: Planned start date
            planned_end: Planned end date
            dependencies: Dependent task IDs
            assigned_to: Assigned user IDs
            is_milestone: Whether this is a milestone
            metadata: Additional metadata

        Returns:
            Task object
        """
        duration_days = (planned_end - planned_start).total_seconds() / 86400

        task = Task(
            task_id=str(uuid.uuid4()),
            name=name,
            description=description,
            project_id=project_id,
            planned_start=planned_start,
            planned_end=planned_end,
            actual_start=None,
            actual_end=None,
            duration_days=duration_days,
            status=TaskStatus.NOT_STARTED,
            dependencies=dependencies or [],
            assigned_to=assigned_to or [],
            completion_percentage=0.0,
            is_milestone=is_milestone,
            is_critical=False,
            slack_days=0.0,
            metadata=metadata or {}
        )

        self._store_task(task)
        logger.info(f"Created task: {task.task_id}")
        return task

    def _store_task(self, task: Task):
        """Store task in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO tasks
                (task_id, name, description, project_id, planned_start, planned_end,
                 actual_start, actual_end, duration_days, status, dependencies, assigned_to,
                 completion_percentage, is_milestone, is_critical, slack_days, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.task_id,
                task.name,
                task.description,
                task.project_id,
                task.planned_start.isoformat(),
                task.planned_end.isoformat(),
                task.actual_start.isoformat() if task.actual_start else None,
                task.actual_end.isoformat() if task.actual_end else None,
                task.duration_days,
                task.status.value,
                json.dumps(task.dependencies),
                json.dumps(task.assigned_to),
                task.completion_percentage,
                1 if task.is_milestone else 0,
                1 if task.is_critical else 0,
                task.slack_days,
                json.dumps(task.metadata)
            ))

    def calculate_critical_path(self, project_id: str) -> Optional[CriticalPath]:
        """
        Calculate critical path for project using CPM (Critical Path Method)

        Args:
            project_id: Project ID

        Returns:
            CriticalPath object
        """
        tasks = self.get_project_tasks(project_id)
        if not tasks:
            return None

        # Build dependency graph
        task_map = {task.task_id: task for task in tasks}

        # Calculate earliest start/finish times (Forward pass)
        earliest_start = {}
        earliest_finish = {}

        def calculate_earliest(task_id: str) -> float:
            if task_id in earliest_finish:
                return earliest_finish[task_id]

            task = task_map[task_id]

            # If no dependencies, start at 0
            if not task.dependencies:
                earliest_start[task_id] = 0
            else:
                # Start after all dependencies finish
                max_finish = 0
                for dep_id in task.dependencies:
                    if dep_id in task_map:
                        dep_finish = calculate_earliest(dep_id)
                        max_finish = max(max_finish, dep_finish)
                earliest_start[task_id] = max_finish

            earliest_finish[task_id] = earliest_start[task_id] + task.duration_days
            return earliest_finish[task_id]

        # Calculate for all tasks
        for task_id in task_map.keys():
            calculate_earliest(task_id)

        # Find project completion time
        project_duration = max(earliest_finish.values()) if earliest_finish else 0

        # Calculate latest start/finish times (Backward pass)
        latest_start = {}
        latest_finish = {}

        def calculate_latest(task_id: str) -> float:
            if task_id in latest_start:
                return latest_start[task_id]

            task = task_map[task_id]

            # Find all tasks that depend on this one
            dependents = [t for t in tasks if task_id in t.dependencies]

            if not dependents:
                # No dependents, must finish by project end
                latest_finish[task_id] = project_duration
            else:
                # Must finish before earliest dependent starts
                min_start = project_duration
                for dep_task in dependents:
                    dep_start = calculate_latest(dep_task.task_id)
                    min_start = min(min_start, dep_start)
                latest_finish[task_id] = min_start

            latest_start[task_id] = latest_finish[task_id] - task.duration_days
            return latest_start[task_id]

        # Calculate for all tasks
        for task_id in task_map.keys():
            calculate_latest(task_id)

        # Calculate slack and identify critical tasks
        critical_tasks = []

        for task_id, task in task_map.items():
            slack = latest_start[task_id] - earliest_start[task_id]
            task.slack_days = slack

            if slack <= 0.001:  # Nearly zero slack
                task.is_critical = True
                critical_tasks.append(task_id)

            # Update task in database
            self._store_task(task)

        # Build critical path
        project_start_date = min(task.planned_start for task in tasks)
        project_end_date = project_start_date + timedelta(days=project_duration)

        critical_path = CriticalPath(
            path_id=str(uuid.uuid4()),
            project_id=project_id,
            tasks=critical_tasks,
            total_duration_days=project_duration,
            calculated_at=datetime.now(timezone.utc),
            project_end_date=project_end_date,
            slack_available=0.0
        )

        self._store_critical_path(critical_path)
        logger.info(f"Calculated critical path for project {project_id}: {len(critical_tasks)} critical tasks")
        return critical_path

    def _store_critical_path(self, path: CriticalPath):
        """Store critical path in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO critical_paths
                (path_id, project_id, tasks, total_duration_days, calculated_at,
                 project_end_date, slack_available)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                path.path_id,
                path.project_id,
                json.dumps(path.tasks),
                path.total_duration_days,
                path.calculated_at.isoformat(),
                path.project_end_date.isoformat(),
                path.slack_available
            ))

    def report_delay(
        self,
        task_id: str,
        reason: DelayReason,
        delay_days: float,
        description: str,
        impact_assessment: str = "",
        mitigation_actions: Optional[List[str]] = None
    ) -> DelayRecord:
        """
        Report a task delay

        Args:
            task_id: Task ID
            reason: Delay reason
            delay_days: Number of days delayed
            description: Delay description
            impact_assessment: Impact assessment
            mitigation_actions: Mitigation actions

        Returns:
            DelayRecord object
        """
        delay = DelayRecord(
            delay_id=str(uuid.uuid4()),
            task_id=task_id,
            reason=reason,
            delay_days=delay_days,
            reported_date=datetime.now(timezone.utc),
            description=description,
            impact_assessment=impact_assessment,
            mitigation_actions=mitigation_actions or [],
            resolved=False
        )

        self._store_delay(delay)

        # Update task status
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.DELAYED
            task.planned_end = task.planned_end + timedelta(days=delay_days)
            self._store_task(task)

        logger.warning(f"Delay reported for task {task_id}: {delay_days} days")
        return delay

    def _store_delay(self, delay: DelayRecord):
        """Store delay record"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO delays
                (delay_id, task_id, reason, delay_days, reported_date, description,
                 impact_assessment, mitigation_actions, resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                delay.delay_id,
                delay.task_id,
                delay.reason.value,
                delay.delay_days,
                delay.reported_date.isoformat(),
                delay.description,
                delay.impact_assessment,
                json.dumps(delay.mitigation_actions),
                1 if delay.resolved else 0
            ))

    def predict_delays(self, project_id: str) -> Dict[str, Any]:
        """
        Predict potential delays using historical data and current progress

        Args:
            project_id: Project ID

        Returns:
            Delay prediction analysis
        """
        tasks = self.get_project_tasks(project_id)
        predictions = {
            'at_risk_tasks': [],
            'predicted_delays': [],
            'confidence_score': 0.0,
            'recommendations': []
        }

        for task in tasks:
            risk_score = 0.0

            # Check if task has dependencies that are delayed
            delayed_dependencies = 0
            for dep_id in task.dependencies:
                dep = self.get_task(dep_id)
                if dep and dep.status == TaskStatus.DELAYED:
                    delayed_dependencies += 1
                    risk_score += 0.3

            # Check if task is on critical path
            if task.is_critical:
                risk_score += 0.4

            # Check historical delays for similar tasks
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT AVG(delay_days) as avg_delay
                    FROM delays d
                    JOIN tasks t ON d.task_id = t.task_id
                    WHERE t.name LIKE ?
                """, (f"%{task.name[:10]}%",))

                row = cursor.fetchone()
                if row and row['avg_delay']:
                    risk_score += min(row['avg_delay'] / 10, 0.3)

            # Check progress vs time
            if task.status == TaskStatus.IN_PROGRESS and task.actual_start:
                elapsed = (datetime.now(timezone.utc) - task.actual_start).days
                expected_progress = (elapsed / task.duration_days) * 100
                if task.completion_percentage < expected_progress - 10:
                    risk_score += 0.2

            if risk_score > 0.5:
                predictions['at_risk_tasks'].append({
                    'task_id': task.task_id,
                    'task_name': task.name,
                    'risk_score': risk_score,
                    'predicted_delay_days': risk_score * 5,  # Rough estimate
                    'reasons': []
                })

        # Calculate confidence
        predictions['confidence_score'] = 0.75 if len(tasks) > 5 else 0.5

        # Generate recommendations
        if predictions['at_risk_tasks']:
            predictions['recommendations'].append("Increase monitoring of at-risk tasks")
            predictions['recommendations'].append("Consider resource reallocation")

        return predictions

    def create_timeline_snapshot(self, project_id: str) -> str:
        """
        Create a timeline snapshot for future comparison

        Args:
            project_id: Project ID

        Returns:
            Snapshot ID
        """
        tasks = self.get_project_tasks(project_id)

        # Calculate forecasted completion
        critical_path = self.calculate_critical_path(project_id)

        planned_completion = max(task.planned_end for task in tasks) if tasks else datetime.now(timezone.utc)
        forecasted_completion = critical_path.project_end_date if critical_path else planned_completion

        variance_days = (forecasted_completion - planned_completion).days

        snapshot_id = str(uuid.uuid4())

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO timeline_snapshots
                (snapshot_id, project_id, snapshot_date, planned_completion,
                 forecasted_completion, variance_days, confidence_score, snapshot_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot_id,
                project_id,
                datetime.now(timezone.utc).isoformat(),
                planned_completion.isoformat(),
                forecasted_completion.isoformat(),
                variance_days,
                0.8,  # Default confidence
                json.dumps([task.to_dict() for task in tasks])
            ))

        logger.info(f"Created timeline snapshot: {snapshot_id}")
        return snapshot_id

    def get_project_tasks(self, project_id: str) -> List[Task]:
        """Get all tasks for a project"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tasks WHERE project_id = ? ORDER BY planned_start ASC
            """, (project_id,))

            tasks = []
            for row in cursor.fetchall():
                tasks.append(Task(
                    task_id=row['task_id'],
                    name=row['name'],
                    description=row['description'],
                    project_id=row['project_id'],
                    planned_start=datetime.fromisoformat(row['planned_start']),
                    planned_end=datetime.fromisoformat(row['planned_end']),
                    actual_start=datetime.fromisoformat(row['actual_start']) if row['actual_start'] else None,
                    actual_end=datetime.fromisoformat(row['actual_end']) if row['actual_end'] else None,
                    duration_days=row['duration_days'],
                    status=TaskStatus(row['status']),
                    dependencies=json.loads(row['dependencies']),
                    assigned_to=json.loads(row['assigned_to']),
                    completion_percentage=row['completion_percentage'],
                    is_milestone=bool(row['is_milestone']),
                    is_critical=bool(row['is_critical']),
                    slack_days=row['slack_days'],
                    metadata=json.loads(row['metadata'])
                ))

            return tasks

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()

            if row:
                return Task(
                    task_id=row['task_id'],
                    name=row['name'],
                    description=row['description'],
                    project_id=row['project_id'],
                    planned_start=datetime.fromisoformat(row['planned_start']),
                    planned_end=datetime.fromisoformat(row['planned_end']),
                    actual_start=datetime.fromisoformat(row['actual_start']) if row['actual_start'] else None,
                    actual_end=datetime.fromisoformat(row['actual_end']) if row['actual_end'] else None,
                    duration_days=row['duration_days'],
                    status=TaskStatus(row['status']),
                    dependencies=json.loads(row['dependencies']),
                    assigned_to=json.loads(row['assigned_to']),
                    completion_percentage=row['completion_percentage'],
                    is_milestone=bool(row['is_milestone']),
                    is_critical=bool(row['is_critical']),
                    slack_days=row['slack_days'],
                    metadata=json.loads(row['metadata'])
                )
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get timeline manager statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Total tasks
            cursor.execute("SELECT COUNT(*) as count FROM tasks")
            stats['total_tasks'] = cursor.fetchone()['count']

            # Tasks by status
            cursor.execute("SELECT status, COUNT(*) as count FROM tasks GROUP BY status")
            stats['tasks_by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}

            # Critical tasks
            cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE is_critical = 1")
            stats['critical_tasks'] = cursor.fetchone()['count']

            # Total delays
            cursor.execute("SELECT COUNT(*) as count FROM delays")
            stats['total_delays'] = cursor.fetchone()['count']

            # Average delay
            cursor.execute("SELECT AVG(delay_days) as avg FROM delays")
            stats['average_delay_days'] = cursor.fetchone()['avg'] or 0

            return stats


if __name__ == "__main__":
    # Example usage
    tm = TimelineManager()

    # Create tasks
    task1 = tm.create_task(
        project_id="PRJ-001",
        name="Design Phase",
        description="Complete system design",
        planned_start=datetime.now(timezone.utc),
        planned_end=datetime.now(timezone.utc) + timedelta(days=10)
    )

    task2 = tm.create_task(
        project_id="PRJ-001",
        name="Implementation Phase",
        description="Implement system",
        planned_start=datetime.now(timezone.utc) + timedelta(days=10),
        planned_end=datetime.now(timezone.utc) + timedelta(days=30),
        dependencies=[task1.task_id]
    )

    # Calculate critical path
    critical_path = tm.calculate_critical_path("PRJ-001")
    print(f"Critical path calculated: {critical_path.total_duration_days} days")

    # Predict delays
    predictions = tm.predict_delays("PRJ-001")
    print(f"Delay predictions: {json.dumps(predictions, indent=2)}")
