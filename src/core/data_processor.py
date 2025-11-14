"""Data processor module for handling measurement data."""

import pandas as pd
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class Measurement:
    """Represents a single measurement."""

    measurement_id: str
    phase_id: str
    timestamp: datetime
    value: float
    unit: str
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert measurement to dictionary."""
        return {
            "measurement_id": self.measurement_id,
            "phase_id": self.phase_id,
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "unit": self.unit,
            "metadata": self.metadata,
        }


class DataProcessor:
    """Process and normalize measurement data."""

    def __init__(self, protocol: Dict[str, Any]):
        """
        Initialize the DataProcessor.

        Args:
            protocol: Protocol definition dictionary
        """
        self.protocol = protocol
        self.measurements: List[Measurement] = []
        logger.info(f"DataProcessor initialized for protocol: {protocol['protocol']['id']}")

    def add_measurement(self, measurement: Measurement) -> None:
        """
        Add a measurement to the dataset.

        Args:
            measurement: Measurement object to add
        """
        self.measurements.append(measurement)
        logger.debug(
            f"Added measurement: {measurement.measurement_id} "
            f"at {measurement.timestamp}"
        )

    def add_measurements(self, measurements: List[Measurement]) -> None:
        """
        Add multiple measurements to the dataset.

        Args:
            measurements: List of Measurement objects
        """
        self.measurements.extend(measurements)
        logger.info(f"Added {len(measurements)} measurements")

    def get_dataframe(self) -> pd.DataFrame:
        """
        Convert measurements to pandas DataFrame.

        Returns:
            DataFrame containing all measurements
        """
        if not self.measurements:
            logger.warning("No measurements available")
            return pd.DataFrame()

        data = [
            {
                "timestamp": m.timestamp,
                "phase_id": m.phase_id,
                "measurement_id": m.measurement_id,
                "value": m.value,
                "unit": m.unit,
            }
            for m in self.measurements
        ]
        df = pd.DataFrame(data)
        logger.info(f"Created DataFrame with {len(df)} rows")
        return df

    def aggregate_by_phase(self) -> Dict[str, pd.DataFrame]:
        """
        Aggregate measurements by test phase.

        Returns:
            Dictionary mapping phase_id to DataFrame
        """
        df = self.get_dataframe()
        if df.empty:
            return {}

        aggregated = {phase: group for phase, group in df.groupby("phase_id")}
        logger.info(f"Aggregated data into {len(aggregated)} phases")
        return aggregated

    def aggregate_by_measurement(self) -> Dict[str, pd.DataFrame]:
        """
        Aggregate measurements by measurement type.

        Returns:
            Dictionary mapping measurement_id to DataFrame
        """
        df = self.get_dataframe()
        if df.empty:
            return {}

        aggregated = {
            measurement: group for measurement, group in df.groupby("measurement_id")
        }
        logger.info(f"Aggregated data into {len(aggregated)} measurement types")
        return aggregated

    def get_statistics(self, measurement_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate statistical summary of measurements.

        Args:
            measurement_id: Optional filter by measurement ID

        Returns:
            Dictionary containing statistical metrics
        """
        df = self.get_dataframe()
        if df.empty:
            return {}

        if measurement_id:
            df = df[df["measurement_id"] == measurement_id]

        stats = {
            "count": len(df),
            "mean": df["value"].mean(),
            "std": df["value"].std(),
            "min": df["value"].min(),
            "max": df["value"].max(),
            "median": df["value"].median(),
        }

        # Calculate quartiles
        stats["q1"] = df["value"].quantile(0.25)
        stats["q3"] = df["value"].quantile(0.75)
        stats["iqr"] = stats["q3"] - stats["q1"]

        logger.info(f"Calculated statistics for {stats['count']} measurements")
        return stats

    def filter_by_time_range(
        self, start_time: datetime, end_time: datetime
    ) -> List[Measurement]:
        """
        Filter measurements by time range.

        Args:
            start_time: Start of time range
            end_time: End of time range

        Returns:
            List of filtered measurements
        """
        filtered = [
            m for m in self.measurements if start_time <= m.timestamp <= end_time
        ]
        logger.info(f"Filtered to {len(filtered)} measurements in time range")
        return filtered

    def get_measurement_count(self) -> int:
        """
        Get total number of measurements.

        Returns:
            Count of measurements
        """
        return len(self.measurements)

    def clear_measurements(self) -> None:
        """Clear all measurements."""
        count = len(self.measurements)
        self.measurements.clear()
        logger.info(f"Cleared {count} measurements")

    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export all measurements to dictionary format.

        Returns:
            Dictionary containing all measurements
        """
        return {
            "protocol_id": self.protocol["protocol"]["id"],
            "measurement_count": len(self.measurements),
            "measurements": [m.to_dict() for m in self.measurements],
        }
