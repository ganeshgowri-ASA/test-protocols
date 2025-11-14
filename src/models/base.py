"""
Base Model Module

Base classes and utilities for data models.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, Optional
import json


@dataclass
class BaseModel:
    """Base class for all data models."""

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary.

        Returns:
            Dictionary representation
        """
        data = asdict(self)

        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()

        return data

    def to_json(self) -> str:
        """
        Convert model to JSON string.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create model instance from dictionary.

        Args:
            data: Dictionary with model data

        Returns:
            Model instance
        """
        # Convert ISO format strings back to datetime
        for key, value in data.items():
            if isinstance(value, str) and 'T' in value:
                try:
                    data[key] = datetime.fromisoformat(value)
                except (ValueError, AttributeError):
                    pass

        return cls(**data)

    def update(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()
