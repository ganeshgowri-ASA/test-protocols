"""
Sample data generator for testing and demonstration
"""
import random
from datetime import datetime, timedelta
from typing import List
import uuid

from models.protocol import (
    Protocol, ProtocolStatus, ProtocolType, QCResult,
    ServiceRequest, Inspection, Equipment, QCRecord,
    Report, KPIMetrics, Notification
)


class DataGenerator:
    """Generates sample data for testing and demonstration"""

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.protocol_names = self._generate_protocol_names()
        self.operators = ["John Doe", "Jane Smith", "Bob Johnson", "Alice Williams", "Charlie Brown"]
        self.customers = ["Acme Corp", "TechCo Industries", "Green Energy Ltd", "Solar Solutions", "PV Systems Inc"]

    def _generate_protocol_names(self) -> List[str]:
        """Generate 54 protocol names"""
        protocols = []
        categories = {
            ProtocolType.ELECTRICAL: [
                "IV Curve Analysis", "Insulation Resistance", "Ground Continuity",
                "High Voltage Test", "Dielectric Strength", "Contact Resistance",
                "Series Resistance"
            ],
            ProtocolType.MECHANICAL: [
                "Mechanical Load Test", "Hail Impact Test", "Static Load",
                "Dynamic Load", "Twist Test", "Robustness Test"
            ],
            ProtocolType.ENVIRONMENTAL: [
                "Thermal Cycling", "Humidity Freeze", "Damp Heat", "UV Exposure",
                "Salt Mist", "Ammonia Corrosion", "Sand Dust"
            ],
            ProtocolType.PERFORMANCE: [
                "STC Performance", "NOCT Performance", "Low Irradiance",
                "Temperature Coefficient", "Spectral Response", "Angle of Incidence"
            ],
            ProtocolType.SAFETY: [
                "Wet Leakage Current", "Reverse Current Overload", "Bypass Diode",
                "Hot Spot Endurance", "Fire Class Rating", "Edge Seal Durability"
            ],
            ProtocolType.QC: [
                "Visual Inspection", "Electroluminescence", "Flash Test",
                "Dimensional Check", "Weight Verification", "Label Verification"
            ],
            ProtocolType.CALIBRATION: [
                "Reference Cell Calibration", "IV Tracer Calibration",
                "Multimeter Calibration", "Infrared Camera Calibration",
                "Pyranometer Calibration"
            ],
            ProtocolType.MATERIAL: [
                "Cell Material Analysis", "Backsheet Analysis", "Encapsulant Analysis",
                "Frame Material Test", "Junction Box Analysis", "Adhesion Test"
            ]
        }

        for ptype, names in categories.items():
            for name in names:
                protocols.append(f"{ptype.value} - {name}")

        return protocols[:54]  # Ensure exactly 54 protocols

    def generate_service_requests(self, count: int = 20) -> List[ServiceRequest]:
        """Generate sample service requests"""
        requests = []
        for i in range(count):
            request_date = datetime.now() - timedelta(days=random.randint(0, 30))
            requests.append(ServiceRequest(
                request_id=f"SR-{2024001 + i}",
                customer_name=random.choice(self.customers),
                sample_id=f"SMP-{2024001 + i}",
                request_date=request_date,
                required_protocols=random.sample(self.protocol_names, k=random.randint(2, 8)),
                priority=random.choice(["low", "normal", "high", "urgent"]),
                status=random.choice(["active", "active", "active", "completed", "on_hold"]),
                assigned_to=random.choice(self.operators)
            ))
        return requests

    def generate_protocols(self, service_requests: List[ServiceRequest]) -> List[Protocol]:
        """Generate protocols based on service requests"""
        protocols = []
        protocol_types = list(ProtocolType)

        for sr in service_requests:
            for i, protocol_name in enumerate(sr.required_protocols):
                start_time = sr.request_date + timedelta(hours=random.randint(1, 48))
                status = random.choice([
                    ProtocolStatus.COMPLETED, ProtocolStatus.COMPLETED,
                    ProtocolStatus.IN_PROGRESS, ProtocolStatus.PENDING
                ])

                end_time = None
                if status == ProtocolStatus.COMPLETED:
                    end_time = start_time + timedelta(hours=random.uniform(0.5, 24))

                qc_result = QCResult.PASS if status == ProtocolStatus.COMPLETED else QCResult.PENDING
                if status == ProtocolStatus.COMPLETED and random.random() < 0.1:  # 10% fail rate
                    qc_result = QCResult.FAIL

                protocols.append(Protocol(
                    protocol_id=f"PROT-{sr.request_id}-{i+1:03d}",
                    protocol_name=protocol_name,
                    protocol_type=random.choice(protocol_types),
                    service_request_id=sr.request_id,
                    sample_id=sr.sample_id,
                    status=status,
                    start_time=start_time if status != ProtocolStatus.PENDING else None,
                    end_time=end_time,
                    operator=random.choice(self.operators),
                    equipment_id=f"EQ-{random.randint(1001, 1020)}",
                    qc_result=qc_result,
                    nc_number=f"NC-{random.randint(1000, 9999)}" if qc_result == QCResult.FAIL else None,
                    test_data={
                        "measurement_1": random.uniform(50, 150),
                        "measurement_2": random.uniform(20, 80),
                        "temperature": random.uniform(20, 30)
                    }
                ))

        return protocols

    def generate_equipment(self, count: int = 20) -> List[Equipment]:
        """Generate equipment records"""
        equipment_types = [
            "IV Curve Tracer", "Multimeter", "Thermal Chamber",
            "Mechanical Tester", "UV Simulator", "EL Camera",
            "Pyranometer", "Infrared Camera", "Salt Spray Chamber"
        ]

        equipment_list = []
        for i in range(count):
            last_cal = datetime.now() - timedelta(days=random.randint(0, 300))
            next_cal = last_cal + timedelta(days=365)

            equipment_list.append(Equipment(
                equipment_id=f"EQ-{1001 + i}",
                equipment_name=f"{random.choice(equipment_types)} #{i+1}",
                equipment_type=random.choice(equipment_types),
                status=random.choice(["available", "available", "in_use", "maintenance"]),
                last_calibration=last_cal,
                next_calibration=next_cal,
                utilization_rate=random.uniform(40, 95),
                total_hours=random.uniform(1000, 5000)
            ))

        return equipment_list

    def generate_kpi_metrics(self, days: int = 30) -> List[KPIMetrics]:
        """Generate KPI metrics for the past N days"""
        metrics = []
        for i in range(days):
            date = datetime.now() - timedelta(days=days - i)
            metrics.append(KPIMetrics(
                date=date,
                total_samples=random.randint(5, 20),
                completed_protocols=random.randint(20, 60),
                pending_protocols=random.randint(5, 25),
                failed_protocols=random.randint(0, 5),
                average_tat=random.uniform(24, 72),
                pass_rate=random.uniform(85, 99),
                first_time_pass_rate=random.uniform(80, 95),
                equipment_utilization=random.uniform(60, 90),
                throughput_daily=random.randint(15, 50)
            ))

        return metrics

    def generate_notifications(self, count: int = 10) -> List[Notification]:
        """Generate sample notifications"""
        notifications = []
        notification_templates = [
            ("alert", "QC Failure Detected", "Sample SMP-2024{} failed quality control check"),
            ("warning", "Equipment Calibration Due", "Equipment EQ-{} calibration due in 5 days"),
            ("info", "Protocol Completed", "Protocol PROT-{} has been completed successfully"),
            ("alert", "TAT Exceeded", "Service request SR-{} has exceeded target TAT"),
            ("warning", "Inspection Pending", "Inspection pending for sample SMP-2024{}")
        ]

        for i in range(count):
            ntype, title, msg_template = random.choice(notification_templates)
            created_at = datetime.now() - timedelta(hours=random.randint(1, 72))

            notifications.append(Notification(
                notification_id=str(uuid.uuid4()),
                notification_type=ntype,
                title=title,
                message=msg_template.format(random.randint(100, 999)),
                created_at=created_at,
                priority="high" if ntype == "alert" else "normal",
                read=random.random() < 0.3  # 30% already read
            ))

        return sorted(notifications, key=lambda x: x.created_at, reverse=True)


# Singleton instance
_generator = DataGenerator()


def get_sample_data():
    """Get all sample data"""
    service_requests = _generator.generate_service_requests(20)
    protocols = _generator.generate_protocols(service_requests)
    equipment = _generator.generate_equipment(20)
    kpi_metrics = _generator.generate_kpi_metrics(30)
    notifications = _generator.generate_notifications(15)

    return {
        "service_requests": service_requests,
        "protocols": protocols,
        "equipment": equipment,
        "kpi_metrics": kpi_metrics,
        "notifications": notifications,
        "protocol_names": _generator.protocol_names
    }
