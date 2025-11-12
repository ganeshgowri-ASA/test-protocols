"""
Alert management system for quality control issues.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from loguru import logger


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertManager:
    """Manages quality control alerts and notifications."""

    def __init__(self):
        """Initialize alert manager."""
        self.alerts = []
        self.alert_handlers = []

    def create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        protocol_id: Optional[str] = None,
        measurement_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new alert.

        Args:
            alert_type: Type of alert
            severity: Alert severity (info, warning, error, critical)
            message: Alert message
            protocol_id: Related protocol ID
            measurement_id: Related measurement ID
            metadata: Additional metadata

        Returns:
            Alert dictionary
        """
        alert = {
            "alert_id": f"ALERT-{len(self.alerts) + 1:06d}",
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "protocol_id": protocol_id,
            "measurement_id": measurement_id,
            "timestamp": datetime.now().isoformat(),
            "status": "active",
            "metadata": metadata or {},
        }

        self.alerts.append(alert)
        logger.warning(
            f"Alert created: [{severity.upper()}] {alert_type} - {message}"
        )

        # Trigger alert handlers
        self._trigger_handlers(alert)

        return alert

    def register_handler(self, handler_func):
        """
        Register an alert handler function.

        Args:
            handler_func: Function to call when alert is created
        """
        self.alert_handlers.append(handler_func)
        logger.debug(f"Registered alert handler: {handler_func.__name__}")

    def _trigger_handlers(self, alert: Dict[str, Any]):
        """
        Trigger all registered alert handlers.

        Args:
            alert: Alert dictionary
        """
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")

    def get_alerts(
        self,
        severity: Optional[str] = None,
        protocol_id: Optional[str] = None,
        status: str = "active",
    ) -> List[Dict[str, Any]]:
        """
        Get alerts matching criteria.

        Args:
            severity: Filter by severity
            protocol_id: Filter by protocol ID
            status: Filter by status

        Returns:
            List of matching alerts
        """
        filtered = self.alerts

        if severity:
            filtered = [a for a in filtered if a["severity"] == severity]

        if protocol_id:
            filtered = [a for a in filtered if a["protocol_id"] == protocol_id]

        if status:
            filtered = [a for a in filtered if a["status"] == status]

        return filtered

    def acknowledge_alert(self, alert_id: str):
        """
        Acknowledge an alert.

        Args:
            alert_id: Alert ID to acknowledge
        """
        for alert in self.alerts:
            if alert["alert_id"] == alert_id:
                alert["status"] = "acknowledged"
                alert["acknowledged_at"] = datetime.now().isoformat()
                logger.info(f"Alert acknowledged: {alert_id}")
                break

    def resolve_alert(self, alert_id: str, resolution: str = ""):
        """
        Resolve an alert.

        Args:
            alert_id: Alert ID to resolve
            resolution: Resolution description
        """
        for alert in self.alerts:
            if alert["alert_id"] == alert_id:
                alert["status"] = "resolved"
                alert["resolved_at"] = datetime.now().isoformat()
                alert["resolution"] = resolution
                logger.info(f"Alert resolved: {alert_id}")
                break

    def get_alert_count(self, severity: Optional[str] = None) -> int:
        """
        Get count of alerts.

        Args:
            severity: Filter by severity

        Returns:
            Count of alerts
        """
        if severity:
            return len([a for a in self.alerts if a["severity"] == severity])
        return len(self.alerts)

    def get_alert_summary(self) -> Dict[str, Any]:
        """
        Get summary of alerts.

        Returns:
            Summary dictionary
        """
        summary = {
            "total": len(self.alerts),
            "by_severity": {},
            "by_status": {},
            "active": 0,
        }

        for alert in self.alerts:
            # Count by severity
            severity = alert["severity"]
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1

            # Count by status
            status = alert["status"]
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

            if status == "active":
                summary["active"] += 1

        return summary

    def clear_resolved_alerts(self):
        """Clear all resolved alerts."""
        initial_count = len(self.alerts)
        self.alerts = [a for a in self.alerts if a["status"] != "resolved"]
        cleared = initial_count - len(self.alerts)
        logger.info(f"Cleared {cleared} resolved alerts")
