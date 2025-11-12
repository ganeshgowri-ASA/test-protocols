"""
Project Manager
Project lifecycle management, milestone tracking, resource allocation, and Gantt chart generation
"""

import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import sqlite3
from contextlib import contextmanager
import plotly.figure_factory as ff
import pandas as pd

logger = logging.getLogger(__name__)


class ProjectStatus(Enum):
    """Project status"""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"


class MilestoneStatus(Enum):
    """Milestone status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    AT_RISK = "at_risk"


class Priority(Enum):
    """Priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Milestone:
    """Project milestone"""
    milestone_id: str
    name: str
    description: str
    due_date: datetime
    completion_date: Optional[datetime]
    status: MilestoneStatus
    dependencies: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    assigned_to: List[str] = field(default_factory=list)
    completion_percentage: float = 0.0
    priority: Priority = Priority.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'milestone_id': self.milestone_id,
            'name': self.name,
            'description': self.description,
            'due_date': self.due_date.isoformat(),
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'status': self.status.value,
            'dependencies': self.dependencies,
            'deliverables': self.deliverables,
            'assigned_to': self.assigned_to,
            'completion_percentage': self.completion_percentage,
            'priority': self.priority.value,
            'metadata': self.metadata
        }


@dataclass
class Project:
    """Project definition"""
    project_id: str
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    actual_end_date: Optional[datetime]
    status: ProjectStatus
    manager_id: str
    team_members: List[str]
    budget: float
    actual_cost: float
    milestones: List[str]  # milestone IDs
    protocols: List[str]  # protocol IDs
    progress_percentage: float = 0.0
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'actual_end_date': self.actual_end_date.isoformat() if self.actual_end_date else None,
            'status': self.status.value,
            'manager_id': self.manager_id,
            'team_members': self.team_members,
            'budget': self.budget,
            'actual_cost': self.actual_cost,
            'milestones': self.milestones,
            'protocols': self.protocols,
            'progress_percentage': self.progress_percentage,
            'risk_score': self.risk_score,
            'metadata': self.metadata
        }


@dataclass
class ResourceAllocation:
    """Resource allocation record"""
    allocation_id: str
    project_id: str
    resource_type: str  # personnel, equipment, material
    resource_id: str
    allocated_from: datetime
    allocated_to: datetime
    allocation_percentage: float  # 0-100%
    cost_per_unit: float
    quantity: float
    total_cost: float
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'allocation_id': self.allocation_id,
            'project_id': self.project_id,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'allocated_from': self.allocated_from.isoformat(),
            'allocated_to': self.allocated_to.isoformat(),
            'allocation_percentage': self.allocation_percentage,
            'cost_per_unit': self.cost_per_unit,
            'quantity': self.quantity,
            'total_cost': self.total_cost,
            'notes': self.notes
        }


class ProjectManager:
    """
    Comprehensive project management system
    """

    def __init__(self, db_path: str = "projects.db"):
        """
        Initialize project manager

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._initialize_database()
        logger.info(f"ProjectManager initialized with database: {db_path}")

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

            # Projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    actual_end_date TEXT,
                    status TEXT NOT NULL,
                    manager_id TEXT NOT NULL,
                    team_members TEXT,
                    budget REAL DEFAULT 0,
                    actual_cost REAL DEFAULT 0,
                    milestones TEXT,
                    protocols TEXT,
                    progress_percentage REAL DEFAULT 0,
                    risk_score REAL DEFAULT 0,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Milestones table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS milestones (
                    milestone_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT NOT NULL,
                    completion_date TEXT,
                    status TEXT NOT NULL,
                    dependencies TEXT,
                    deliverables TEXT,
                    assigned_to TEXT,
                    completion_percentage REAL DEFAULT 0,
                    priority TEXT DEFAULT 'medium',
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                )
            """)

            # Resource allocations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resource_allocations (
                    allocation_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    allocated_from TEXT NOT NULL,
                    allocated_to TEXT NOT NULL,
                    allocation_percentage REAL DEFAULT 100,
                    cost_per_unit REAL DEFAULT 0,
                    quantity REAL DEFAULT 1,
                    total_cost REAL DEFAULT 0,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                )
            """)

            # Project activities log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_activities (
                    activity_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    description TEXT,
                    performed_by TEXT,
                    performed_at TEXT NOT NULL,
                    details TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                )
            """)

            # Risk register
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_register (
                    risk_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    risk_description TEXT NOT NULL,
                    probability REAL NOT NULL,
                    impact REAL NOT NULL,
                    risk_score REAL NOT NULL,
                    mitigation_strategy TEXT,
                    owner TEXT,
                    status TEXT DEFAULT 'open',
                    identified_date TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_status ON projects(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_manager ON projects(manager_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_milestone_status ON milestones(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_milestone_due_date ON milestones(due_date)")

            logger.info("Project management database schema initialized")

    def create_project(
        self,
        name: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        manager_id: str,
        budget: float = 0.0,
        protocols: Optional[List[str]] = None,
        team_members: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> Project:
        """
        Create a new project

        Args:
            name: Project name
            description: Project description
            start_date: Project start date
            end_date: Project end date
            manager_id: Project manager user ID
            budget: Project budget
            protocols: Associated protocol IDs
            team_members: Team member IDs
            metadata: Additional metadata

        Returns:
            Project object
        """
        project = Project(
            project_id=str(uuid.uuid4()),
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            actual_end_date=None,
            status=ProjectStatus.PLANNING,
            manager_id=manager_id,
            team_members=team_members or [],
            budget=budget,
            actual_cost=0.0,
            milestones=[],
            protocols=protocols or [],
            progress_percentage=0.0,
            risk_score=0.0,
            metadata=metadata or {}
        )

        self._store_project(project)

        # Log activity
        self._log_activity(
            project_id=project.project_id,
            activity_type="project_created",
            description=f"Project '{name}' created",
            performed_by=manager_id
        )

        logger.info(f"Created project: {project.project_id}")
        return project

    def _store_project(self, project: Project):
        """Store project in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO projects
                (project_id, name, description, start_date, end_date, actual_end_date,
                 status, manager_id, team_members, budget, actual_cost, milestones,
                 protocols, progress_percentage, risk_score, metadata, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project.project_id,
                project.name,
                project.description,
                project.start_date.isoformat(),
                project.end_date.isoformat(),
                project.actual_end_date.isoformat() if project.actual_end_date else None,
                project.status.value,
                project.manager_id,
                json.dumps(project.team_members),
                project.budget,
                project.actual_cost,
                json.dumps(project.milestones),
                json.dumps(project.protocols),
                project.progress_percentage,
                project.risk_score,
                json.dumps(project.metadata),
                datetime.now(timezone.utc).isoformat()
            ))

    def create_milestone(
        self,
        project_id: str,
        name: str,
        description: str,
        due_date: datetime,
        dependencies: Optional[List[str]] = None,
        deliverables: Optional[List[str]] = None,
        assigned_to: Optional[List[str]] = None,
        priority: Priority = Priority.MEDIUM,
        metadata: Optional[Dict] = None
    ) -> Milestone:
        """
        Create a project milestone

        Args:
            project_id: Project ID
            name: Milestone name
            description: Milestone description
            due_date: Due date
            dependencies: Dependent milestone IDs
            deliverables: Deliverable descriptions
            assigned_to: Assigned user IDs
            priority: Priority level
            metadata: Additional metadata

        Returns:
            Milestone object
        """
        milestone = Milestone(
            milestone_id=str(uuid.uuid4()),
            name=name,
            description=description,
            due_date=due_date,
            completion_date=None,
            status=MilestoneStatus.NOT_STARTED,
            dependencies=dependencies or [],
            deliverables=deliverables or [],
            assigned_to=assigned_to or [],
            completion_percentage=0.0,
            priority=priority,
            metadata=metadata or {}
        )

        self._store_milestone(project_id, milestone)

        # Update project milestone list
        project = self.get_project(project_id)
        if project:
            project.milestones.append(milestone.milestone_id)
            self._store_project(project)

        # Log activity
        self._log_activity(
            project_id=project_id,
            activity_type="milestone_created",
            description=f"Milestone '{name}' created",
            performed_by=project.manager_id if project else ""
        )

        logger.info(f"Created milestone: {milestone.milestone_id}")
        return milestone

    def _store_milestone(self, project_id: str, milestone: Milestone):
        """Store milestone in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO milestones
                (milestone_id, project_id, name, description, due_date, completion_date,
                 status, dependencies, deliverables, assigned_to, completion_percentage,
                 priority, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                milestone.milestone_id,
                project_id,
                milestone.name,
                milestone.description,
                milestone.due_date.isoformat(),
                milestone.completion_date.isoformat() if milestone.completion_date else None,
                milestone.status.value,
                json.dumps(milestone.dependencies),
                json.dumps(milestone.deliverables),
                json.dumps(milestone.assigned_to),
                milestone.completion_percentage,
                milestone.priority.value,
                json.dumps(milestone.metadata)
            ))

    def update_milestone_progress(
        self,
        milestone_id: str,
        completion_percentage: float,
        notes: Optional[str] = None
    ):
        """
        Update milestone progress

        Args:
            milestone_id: Milestone ID
            completion_percentage: Completion percentage (0-100)
            notes: Progress notes
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get current milestone
            cursor.execute("SELECT * FROM milestones WHERE milestone_id = ?", (milestone_id,))
            row = cursor.fetchone()

            if row:
                # Update status based on completion
                if completion_percentage >= 100:
                    status = MilestoneStatus.COMPLETED
                    completion_date = datetime.now(timezone.utc).isoformat()
                elif completion_percentage > 0:
                    status = MilestoneStatus.IN_PROGRESS
                    completion_date = None
                else:
                    status = MilestoneStatus.NOT_STARTED
                    completion_date = None

                # Check if overdue
                if datetime.fromisoformat(row['due_date']) < datetime.now(timezone.utc) and completion_percentage < 100:
                    status = MilestoneStatus.OVERDUE

                cursor.execute("""
                    UPDATE milestones
                    SET completion_percentage = ?,
                        status = ?,
                        completion_date = ?
                    WHERE milestone_id = ?
                """, (completion_percentage, status.value, completion_date, milestone_id))

                # Update project progress
                self._update_project_progress(row['project_id'])

                # Log activity
                self._log_activity(
                    project_id=row['project_id'],
                    activity_type="milestone_progress_updated",
                    description=f"Milestone progress updated to {completion_percentage}%",
                    performed_by="",
                    details={'milestone_id': milestone_id, 'notes': notes}
                )

    def _update_project_progress(self, project_id: str):
        """Recalculate and update project progress"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get all milestones for project
            cursor.execute("""
                SELECT completion_percentage FROM milestones WHERE project_id = ?
            """, (project_id,))

            rows = cursor.fetchall()
            if rows:
                total_progress = sum(row['completion_percentage'] for row in rows)
                avg_progress = total_progress / len(rows)

                # Update project
                cursor.execute("""
                    UPDATE projects SET progress_percentage = ? WHERE project_id = ?
                """, (avg_progress, project_id))

    def allocate_resource(
        self,
        project_id: str,
        resource_type: str,
        resource_id: str,
        allocated_from: datetime,
        allocated_to: datetime,
        allocation_percentage: float = 100.0,
        cost_per_unit: float = 0.0,
        quantity: float = 1.0,
        notes: str = ""
    ) -> ResourceAllocation:
        """
        Allocate resource to project

        Args:
            project_id: Project ID
            resource_type: Type (personnel, equipment, material)
            resource_id: Resource identifier
            allocated_from: Allocation start
            allocated_to: Allocation end
            allocation_percentage: Allocation percentage
            cost_per_unit: Cost per unit
            quantity: Quantity
            notes: Additional notes

        Returns:
            ResourceAllocation object
        """
        total_cost = cost_per_unit * quantity

        allocation = ResourceAllocation(
            allocation_id=str(uuid.uuid4()),
            project_id=project_id,
            resource_type=resource_type,
            resource_id=resource_id,
            allocated_from=allocated_from,
            allocated_to=allocated_to,
            allocation_percentage=allocation_percentage,
            cost_per_unit=cost_per_unit,
            quantity=quantity,
            total_cost=total_cost,
            notes=notes
        )

        self._store_allocation(allocation)

        # Update project cost
        self._update_project_cost(project_id)

        logger.info(f"Allocated resource: {allocation.allocation_id}")
        return allocation

    def _store_allocation(self, allocation: ResourceAllocation):
        """Store resource allocation"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO resource_allocations
                (allocation_id, project_id, resource_type, resource_id, allocated_from,
                 allocated_to, allocation_percentage, cost_per_unit, quantity, total_cost, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                allocation.allocation_id,
                allocation.project_id,
                allocation.resource_type,
                allocation.resource_id,
                allocation.allocated_from.isoformat(),
                allocation.allocated_to.isoformat(),
                allocation.allocation_percentage,
                allocation.cost_per_unit,
                allocation.quantity,
                allocation.total_cost,
                allocation.notes
            ))

    def _update_project_cost(self, project_id: str):
        """Update project actual cost"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(total_cost) as total FROM resource_allocations WHERE project_id = ?
            """, (project_id,))

            row = cursor.fetchone()
            total_cost = row['total'] or 0.0

            cursor.execute("""
                UPDATE projects SET actual_cost = ? WHERE project_id = ?
            """, (total_cost, project_id))

    def generate_gantt_chart(self, project_id: str) -> Any:
        """
        Generate Gantt chart for project

        Args:
            project_id: Project ID

        Returns:
            Plotly figure
        """
        project = self.get_project(project_id)
        if not project:
            return None

        # Get milestones
        milestones = [self.get_milestone(mid) for mid in project.milestones]
        milestones = [m for m in milestones if m is not None]

        if not milestones:
            return None

        # Prepare data for Gantt chart
        df_data = []
        for milestone in milestones:
            start = milestone.due_date - timedelta(days=30)  # Estimate start
            finish = milestone.completion_date or milestone.due_date

            df_data.append(dict(
                Task=milestone.name,
                Start=start.strftime('%Y-%m-%d'),
                Finish=finish.strftime('%Y-%m-%d'),
                Resource=', '.join(milestone.assigned_to) if milestone.assigned_to else 'Unassigned'
            ))

        df = pd.DataFrame(df_data)

        # Create Gantt chart
        fig = ff.create_gantt(
            df,
            title=f"Project Gantt Chart: {project.name}",
            index_col='Resource',
            show_colorbar=True,
            group_tasks=True
        )

        return fig

    def _log_activity(
        self,
        project_id: str,
        activity_type: str,
        description: str,
        performed_by: str,
        details: Optional[Dict] = None
    ):
        """Log project activity"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO project_activities
                (activity_id, project_id, activity_type, description, performed_by,
                 performed_at, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                project_id,
                activity_type,
                description,
                performed_by,
                datetime.now(timezone.utc).isoformat(),
                json.dumps(details or {})
            ))

    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,))
            row = cursor.fetchone()

            if row:
                return Project(
                    project_id=row['project_id'],
                    name=row['name'],
                    description=row['description'],
                    start_date=datetime.fromisoformat(row['start_date']),
                    end_date=datetime.fromisoformat(row['end_date']),
                    actual_end_date=datetime.fromisoformat(row['actual_end_date']) if row['actual_end_date'] else None,
                    status=ProjectStatus(row['status']),
                    manager_id=row['manager_id'],
                    team_members=json.loads(row['team_members']),
                    budget=row['budget'],
                    actual_cost=row['actual_cost'],
                    milestones=json.loads(row['milestones']),
                    protocols=json.loads(row['protocols']),
                    progress_percentage=row['progress_percentage'],
                    risk_score=row['risk_score'],
                    metadata=json.loads(row['metadata'])
                )
        return None

    def get_milestone(self, milestone_id: str) -> Optional[Milestone]:
        """Get milestone by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM milestones WHERE milestone_id = ?", (milestone_id,))
            row = cursor.fetchone()

            if row:
                return Milestone(
                    milestone_id=row['milestone_id'],
                    name=row['name'],
                    description=row['description'],
                    due_date=datetime.fromisoformat(row['due_date']),
                    completion_date=datetime.fromisoformat(row['completion_date']) if row['completion_date'] else None,
                    status=MilestoneStatus(row['status']),
                    dependencies=json.loads(row['dependencies']),
                    deliverables=json.loads(row['deliverables']),
                    assigned_to=json.loads(row['assigned_to']),
                    completion_percentage=row['completion_percentage'],
                    priority=Priority(row['priority']),
                    metadata=json.loads(row['metadata'])
                )
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get project management statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Total projects
            cursor.execute("SELECT COUNT(*) as count FROM projects")
            stats['total_projects'] = cursor.fetchone()['count']

            # Projects by status
            cursor.execute("SELECT status, COUNT(*) as count FROM projects GROUP BY status")
            stats['projects_by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}

            # Total budget vs actual cost
            cursor.execute("SELECT SUM(budget) as budget, SUM(actual_cost) as cost FROM projects")
            row = cursor.fetchone()
            stats['total_budget'] = row['budget'] or 0
            stats['total_actual_cost'] = row['cost'] or 0

            # Overdue milestones
            cursor.execute("""
                SELECT COUNT(*) as count FROM milestones
                WHERE status != 'completed' AND due_date < ?
            """, (datetime.now(timezone.utc).isoformat(),))
            stats['overdue_milestones'] = cursor.fetchone()['count']

            return stats


if __name__ == "__main__":
    # Example usage
    pm = ProjectManager()

    # Create project
    project = pm.create_project(
        name="PVTP-048-054 Testing Campaign",
        description="Comprehensive testing campaign for protocols 048-054",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=90),
        manager_id="PM001",
        budget=150000.0,
        protocols=["PVTP-048", "PVTP-049", "PVTP-050"]
    )

    # Create milestone
    milestone = pm.create_milestone(
        project_id=project.project_id,
        name="Complete Phase 1 Testing",
        description="Complete all thermal cycling tests",
        due_date=datetime.now(timezone.utc) + timedelta(days=30),
        priority=Priority.HIGH
    )

    print(f"Created project: {project.project_id}")
    print(f"Created milestone: {milestone.milestone_id}")
