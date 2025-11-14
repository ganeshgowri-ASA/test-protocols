"""
Feedback Collector
User feedback collection, analysis, and action tracking
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
import sqlite3
from contextlib import contextmanager
from collections import Counter

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Feedback types"""
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    IMPROVEMENT = "improvement"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"
    QUESTION = "question"
    OTHER = "other"


class FeedbackStatus(Enum):
    """Feedback status"""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACKNOWLEDGED = "acknowledged"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    DUPLICATE = "duplicate"


class Priority(Enum):
    """Feedback priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Feedback:
    """Feedback record"""
    feedback_id: str
    feedback_type: FeedbackType
    title: str
    description: str
    submitted_by: str
    submitted_date: datetime
    status: FeedbackStatus
    priority: Priority
    category: str
    affected_protocols: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    resolution: str = ""
    resolution_date: Optional[datetime] = None
    satisfaction_rating: Optional[int] = None  # 1-5
    related_feedback_ids: List[str] = field(default_factory=list)
    votes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'feedback_id': self.feedback_id,
            'feedback_type': self.feedback_type.value,
            'title': self.title,
            'description': self.description,
            'submitted_by': self.submitted_by,
            'submitted_date': self.submitted_date.isoformat(),
            'status': self.status.value,
            'priority': self.priority.value,
            'category': self.category,
            'affected_protocols': self.affected_protocols,
            'assigned_to': self.assigned_to,
            'resolution': self.resolution,
            'resolution_date': self.resolution_date.isoformat() if self.resolution_date else None,
            'satisfaction_rating': self.satisfaction_rating,
            'related_feedback_ids': self.related_feedback_ids,
            'votes': self.votes,
            'metadata': self.metadata
        }


class FeedbackCollector:
    """Feedback collection and management system"""

    def __init__(self, db_path: str = "feedback.db"):
        self.db_path = db_path
        self._initialize_database()
        logger.info(f"FeedbackCollector initialized with database: {db_path}")

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
                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id TEXT PRIMARY KEY,
                    feedback_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    submitted_by TEXT NOT NULL,
                    submitted_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    category TEXT,
                    affected_protocols TEXT,
                    assigned_to TEXT,
                    resolution TEXT,
                    resolution_date TEXT,
                    satisfaction_rating INTEGER,
                    related_feedback_ids TEXT,
                    votes INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback_comments (
                    comment_id TEXT PRIMARY KEY,
                    feedback_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    comment TEXT NOT NULL,
                    comment_date TEXT NOT NULL,
                    FOREIGN KEY (feedback_id) REFERENCES feedback(feedback_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback_votes (
                    vote_id TEXT PRIMARY KEY,
                    feedback_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    vote_type TEXT NOT NULL,
                    vote_date TEXT NOT NULL,
                    FOREIGN KEY (feedback_id) REFERENCES feedback(feedback_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback_analytics (
                    analytics_id TEXT PRIMARY KEY,
                    period_start TEXT NOT NULL,
                    period_end TEXT NOT NULL,
                    total_feedback INTEGER,
                    by_type TEXT,
                    by_status TEXT,
                    avg_resolution_time_days REAL,
                    satisfaction_score REAL,
                    generated_at TEXT NOT NULL
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(feedback_type)")

            logger.info("Feedback collector database schema initialized")

    def submit_feedback(
        self,
        feedback_type: FeedbackType,
        title: str,
        description: str,
        submitted_by: str,
        category: str = "",
        affected_protocols: Optional[List[str]] = None,
        priority: Priority = Priority.MEDIUM,
        metadata: Optional[Dict] = None
    ) -> Feedback:
        """Submit new feedback"""
        feedback = Feedback(
            feedback_id=str(uuid.uuid4()),
            feedback_type=feedback_type,
            title=title,
            description=description,
            submitted_by=submitted_by,
            submitted_date=datetime.now(timezone.utc),
            status=FeedbackStatus.SUBMITTED,
            priority=priority,
            category=category,
            affected_protocols=affected_protocols or [],
            assigned_to=None,
            resolution="",
            resolution_date=None,
            satisfaction_rating=None,
            related_feedback_ids=[],
            votes=0,
            metadata=metadata or {}
        )

        self._store_feedback(feedback)
        logger.info(f"Submitted feedback: {feedback.feedback_id}")
        return feedback

    def _store_feedback(self, feedback: Feedback):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO feedback
                (feedback_id, feedback_type, title, description, submitted_by, submitted_date,
                 status, priority, category, affected_protocols, assigned_to, resolution,
                 resolution_date, satisfaction_rating, related_feedback_ids, votes, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback.feedback_id,
                feedback.feedback_type.value,
                feedback.title,
                feedback.description,
                feedback.submitted_by,
                feedback.submitted_date.isoformat(),
                feedback.status.value,
                feedback.priority.value,
                feedback.category,
                json.dumps(feedback.affected_protocols),
                feedback.assigned_to,
                feedback.resolution,
                feedback.resolution_date.isoformat() if feedback.resolution_date else None,
                feedback.satisfaction_rating,
                json.dumps(feedback.related_feedback_ids),
                feedback.votes,
                json.dumps(feedback.metadata)
            ))

    def update_feedback_status(
        self,
        feedback_id: str,
        status: FeedbackStatus,
        assigned_to: Optional[str] = None,
        resolution: str = ""
    ):
        """Update feedback status"""
        feedback = self.get_feedback(feedback_id)
        if not feedback:
            raise ValueError(f"Feedback not found: {feedback_id}")

        feedback.status = status
        if assigned_to:
            feedback.assigned_to = assigned_to

        if status == FeedbackStatus.COMPLETED and resolution:
            feedback.resolution = resolution
            feedback.resolution_date = datetime.now(timezone.utc)

        self._store_feedback(feedback)

    def add_comment(
        self,
        feedback_id: str,
        user_id: str,
        comment: str
    ):
        """Add comment to feedback"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback_comments
                (comment_id, feedback_id, user_id, comment, comment_date)
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                feedback_id,
                user_id,
                comment,
                datetime.now(timezone.utc).isoformat()
            ))

    def vote_feedback(
        self,
        feedback_id: str,
        user_id: str,
        vote_type: str = "upvote"
    ):
        """Vote on feedback"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Check if already voted
            cursor.execute("""
                SELECT vote_id FROM feedback_votes
                WHERE feedback_id = ? AND user_id = ?
            """, (feedback_id, user_id))

            if cursor.fetchone():
                logger.warning(f"User {user_id} already voted on {feedback_id}")
                return

            # Add vote
            cursor.execute("""
                INSERT INTO feedback_votes
                (vote_id, feedback_id, user_id, vote_type, vote_date)
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                feedback_id,
                user_id,
                vote_type,
                datetime.now(timezone.utc).isoformat()
            ))

            # Update vote count
            cursor.execute("""
                UPDATE feedback
                SET votes = votes + 1
                WHERE feedback_id = ?
            """, (feedback_id,))

    def analyze_feedback(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze feedback for a period"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get feedback in period
            cursor.execute("""
                SELECT * FROM feedback
                WHERE submitted_date >= ? AND submitted_date <= ?
            """, (start_date.isoformat(), end_date.isoformat()))

            feedback_list = cursor.fetchall()

            analysis = {
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'total_feedback': len(feedback_list),
                'by_type': {},
                'by_status': {},
                'by_priority': {},
                'avg_resolution_time_days': 0.0,
                'satisfaction_score': 0.0,
                'top_categories': [],
                'most_voted': []
            }

            if not feedback_list:
                return analysis

            # Count by type, status, priority
            types = [row['feedback_type'] for row in feedback_list]
            statuses = [row['status'] for row in feedback_list]
            priorities = [row['priority'] for row in feedback_list]

            analysis['by_type'] = dict(Counter(types))
            analysis['by_status'] = dict(Counter(statuses))
            analysis['by_priority'] = dict(Counter(priorities))

            # Calculate average resolution time
            resolved = [row for row in feedback_list if row['resolution_date']]
            if resolved:
                resolution_times = []
                for row in resolved:
                    submitted = datetime.fromisoformat(row['submitted_date'])
                    resolved_date = datetime.fromisoformat(row['resolution_date'])
                    days = (resolved_date - submitted).days
                    resolution_times.append(days)

                analysis['avg_resolution_time_days'] = sum(resolution_times) / len(resolution_times)

            # Calculate satisfaction score
            ratings = [row['satisfaction_rating'] for row in feedback_list if row['satisfaction_rating']]
            if ratings:
                analysis['satisfaction_score'] = sum(ratings) / len(ratings)

            # Top categories
            categories = [row['category'] for row in feedback_list if row['category']]
            analysis['top_categories'] = [
                {'category': cat, 'count': count}
                for cat, count in Counter(categories).most_common(5)
            ]

            # Most voted feedback
            cursor.execute("""
                SELECT feedback_id, title, votes FROM feedback
                WHERE submitted_date >= ? AND submitted_date <= ?
                ORDER BY votes DESC
                LIMIT 5
            """, (start_date.isoformat(), end_date.isoformat()))

            analysis['most_voted'] = [
                {'feedback_id': row['feedback_id'], 'title': row['title'], 'votes': row['votes']}
                for row in cursor.fetchall()
            ]

            # Store analytics
            self._store_analytics(analysis)

            return analysis

    def _store_analytics(self, analysis: Dict):
        """Store analytics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback_analytics
                (analytics_id, period_start, period_end, total_feedback, by_type, by_status,
                 avg_resolution_time_days, satisfaction_score, generated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                analysis['period_start'],
                analysis['period_end'],
                analysis['total_feedback'],
                json.dumps(analysis['by_type']),
                json.dumps(analysis['by_status']),
                analysis['avg_resolution_time_days'],
                analysis['satisfaction_score'],
                datetime.now(timezone.utc).isoformat()
            ))

    def get_feedback(self, feedback_id: str) -> Optional[Feedback]:
        """Get feedback by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM feedback WHERE feedback_id = ?", (feedback_id,))
            row = cursor.fetchone()

            if row:
                return Feedback(
                    feedback_id=row['feedback_id'],
                    feedback_type=FeedbackType(row['feedback_type']),
                    title=row['title'],
                    description=row['description'],
                    submitted_by=row['submitted_by'],
                    submitted_date=datetime.fromisoformat(row['submitted_date']),
                    status=FeedbackStatus(row['status']),
                    priority=Priority(row['priority']),
                    category=row['category'],
                    affected_protocols=json.loads(row['affected_protocols']),
                    assigned_to=row['assigned_to'],
                    resolution=row['resolution'],
                    resolution_date=datetime.fromisoformat(row['resolution_date']) if row['resolution_date'] else None,
                    satisfaction_rating=row['satisfaction_rating'],
                    related_feedback_ids=json.loads(row['related_feedback_ids']),
                    votes=row['votes'],
                    metadata=json.loads(row['metadata'])
                )
        return None


if __name__ == "__main__":
    collector = FeedbackCollector()

    # Submit feedback
    feedback = collector.submit_feedback(
        feedback_type=FeedbackType.FEATURE_REQUEST,
        title="Add export to Excel feature",
        description="Would be great to export test results directly to Excel",
        submitted_by="user001",
        category="Features",
        affected_protocols=["PVTP-048", "PVTP-049"],
        priority=Priority.MEDIUM
    )

    print(f"Submitted feedback: {feedback.feedback_id}")

    # Analyze
    analysis = collector.analyze_feedback(
        start_date=datetime.now(timezone.utc) - timedelta(days=30),
        end_date=datetime.now(timezone.utc)
    )

    print(f"Analysis: {json.dumps(analysis, indent=2)}")
