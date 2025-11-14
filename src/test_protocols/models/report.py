"""Report database model."""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class Report(Base):
    """Database model for test reports."""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to test session
    session_id = Column(Integer, ForeignKey("test_sessions.id"), nullable=False)

    # Report metadata
    report_id = Column(String(100), unique=True, nullable=False, index=True)
    report_type = Column(String(50), nullable=False)  # pdf, html, json, excel
    title = Column(String(200))
    generated_by = Column(String(100))

    # Report content
    # For text-based formats (HTML, JSON), store in 'content' field
    # For binary formats (PDF, Excel), store in 'binary_content' field
    content = Column(Text)  # For HTML, JSON, etc.
    binary_content = Column(LargeBinary)  # For PDF, Excel, etc.

    # File path if report is saved to disk
    file_path = Column(String(500))

    # Report sections included
    sections = Column(Text)  # Comma-separated list of sections

    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("TestSession", back_populates="reports")

    def __repr__(self) -> str:
        return (
            f"<Report(id={self.id}, report_id='{self.report_id}', "
            f"type='{self.report_type}')>"
        )

    def to_dict(self, include_content: bool = False) -> dict:
        """
        Convert to dictionary.

        Args:
            include_content: Whether to include report content

        Returns:
            Dictionary representation
        """
        data = {
            "id": self.id,
            "session_id": self.session_id,
            "report_id": self.report_id,
            "report_type": self.report_type,
            "title": self.title,
            "generated_by": self.generated_by,
            "file_path": self.file_path,
            "sections": self.sections.split(",") if self.sections else [],
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        if include_content:
            if self.report_type in ["html", "json"]:
                data["content"] = self.content
            elif self.binary_content:
                data["has_binary_content"] = True
                data["binary_size_bytes"] = len(self.binary_content)

        return data

    @classmethod
    def from_session(
        cls,
        session_id: int,
        report_type: str,
        content: str = None,
        binary_content: bytes = None,
        **kwargs,
    ) -> "Report":
        """
        Create Report instance from test session.

        Args:
            session_id: Test session ID
            report_type: Report type (pdf, html, json, excel)
            content: Text content for HTML/JSON reports
            binary_content: Binary content for PDF/Excel reports
            **kwargs: Additional report metadata

        Returns:
            Report instance
        """
        # Generate report ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_id = f"REPORT_{session_id}_{timestamp}"

        return cls(
            session_id=session_id,
            report_id=report_id,
            report_type=report_type,
            content=content,
            binary_content=binary_content,
            title=kwargs.get("title"),
            generated_by=kwargs.get("generated_by"),
            file_path=kwargs.get("file_path"),
            sections=kwargs.get("sections"),
        )
