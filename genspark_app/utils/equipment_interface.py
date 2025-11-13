"""
Equipment Interface Utilities

Provides interfaces for connecting to laboratory equipment:
- Solar simulators
- Environmental chambers
- I-V curve tracers
- Data acquisition systems
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EquipmentInterface(ABC):
    """Abstract base class for equipment interfaces"""

    def __init__(self, equipment_id: str, connection_params: Dict[str, Any]):
        """
        Initialize equipment interface

        Args:
            equipment_id: Unique equipment identifier
            connection_params: Connection parameters (port, address, etc.)
        """
        self.equipment_id = equipment_id
        self.connection_params = connection_params
        self.is_connected = False
        self.last_communication = None

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to equipment"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from equipment"""
        pass

    @abstractmethod
    def read_data(self) -> Dict[str, Any]:
        """Read data from equipment"""
        pass

    @abstractmethod
    def send_command(self, command: str) -> bool:
        """Send command to equipment"""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get equipment status"""
        pass


class SolarSimulatorInterface(EquipmentInterface):
    """Interface for solar simulators"""

    def __init__(self, equipment_id: str, connection_params: Dict[str, Any]):
        super().__init__(equipment_id, connection_params)
        self.current_irradiance = 0
        self.current_spectrum = "AM1.5G"

    def connect(self) -> bool:
        """Connect to solar simulator"""
        try:
            logger.info(f"Connecting to solar simulator {self.equipment_id}")
            # In production: actual connection logic here
            self.is_connected = True
            self.last_communication = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def disconnect(self) -> bool:
        """Disconnect from solar simulator"""
        logger.info(f"Disconnecting from solar simulator {self.equipment_id}")
        self.is_connected = False
        return True

    def set_irradiance(self, irradiance: float) -> bool:
        """
        Set irradiance level

        Args:
            irradiance: Target irradiance (W/m²)

        Returns:
            Success status
        """
        try:
            logger.info(f"Setting irradiance to {irradiance} W/m²")
            # In production: send actual command to equipment
            self.current_irradiance = irradiance
            self.last_communication = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Set irradiance failed: {e}")
            return False

    def set_spectrum(self, spectrum: str) -> bool:
        """
        Set spectrum type

        Args:
            spectrum: Spectrum type (AM1.5G, AM1.5D, AM0, etc.)

        Returns:
            Success status
        """
        try:
            logger.info(f"Setting spectrum to {spectrum}")
            self.current_spectrum = spectrum
            self.last_communication = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Set spectrum failed: {e}")
            return False

    def read_data(self) -> Dict[str, Any]:
        """Read current solar simulator data"""
        return {
            'equipment_id': self.equipment_id,
            'timestamp': datetime.utcnow().isoformat(),
            'irradiance': self.current_irradiance,
            'spectrum': self.current_spectrum,
            'uniformity': 95.0,  # Placeholder
            'stability': 99.0    # Placeholder
        }

    def send_command(self, command: str) -> bool:
        """Send command to solar simulator"""
        logger.debug(f"Sending command: {command}")
        self.last_communication = datetime.utcnow()
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get solar simulator status"""
        return {
            'equipment_id': self.equipment_id,
            'is_connected': self.is_connected,
            'irradiance': self.current_irradiance,
            'spectrum': self.current_spectrum,
            'lamp_hours': 1500,  # Placeholder
            'status': 'ready'
        }


class EnvironmentalChamberInterface(EquipmentInterface):
    """Interface for environmental chambers"""

    def __init__(self, equipment_id: str, connection_params: Dict[str, Any]):
        super().__init__(equipment_id, connection_params)
        self.current_temperature = 25.0
        self.current_humidity = 50.0
        self.setpoint_temperature = 25.0
        self.setpoint_humidity = 50.0

    def connect(self) -> bool:
        """Connect to environmental chamber"""
        try:
            logger.info(f"Connecting to environmental chamber {self.equipment_id}")
            self.is_connected = True
            self.last_communication = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def disconnect(self) -> bool:
        """Disconnect from environmental chamber"""
        logger.info(f"Disconnecting from environmental chamber {self.equipment_id}")
        self.is_connected = False
        return True

    def set_temperature(self, temperature: float) -> bool:
        """Set temperature setpoint (°C)"""
        try:
            logger.info(f"Setting temperature to {temperature}°C")
            self.setpoint_temperature = temperature
            # In production: actual temperature would ramp to setpoint
            self.current_temperature = temperature
            self.last_communication = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Set temperature failed: {e}")
            return False

    def set_humidity(self, humidity: float) -> bool:
        """Set humidity setpoint (%RH)"""
        try:
            logger.info(f"Setting humidity to {humidity}%RH")
            self.setpoint_humidity = humidity
            self.current_humidity = humidity
            self.last_communication = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Set humidity failed: {e}")
            return False

    def read_data(self) -> Dict[str, Any]:
        """Read current chamber conditions"""
        return {
            'equipment_id': self.equipment_id,
            'timestamp': datetime.utcnow().isoformat(),
            'temperature': self.current_temperature,
            'humidity': self.current_humidity,
            'setpoint_temperature': self.setpoint_temperature,
            'setpoint_humidity': self.setpoint_humidity,
            'at_setpoint': abs(self.current_temperature - self.setpoint_temperature) < 0.5
        }

    def send_command(self, command: str) -> bool:
        """Send command to chamber"""
        logger.debug(f"Sending command: {command}")
        self.last_communication = datetime.utcnow()
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get chamber status"""
        return {
            'equipment_id': self.equipment_id,
            'is_connected': self.is_connected,
            'temperature': self.current_temperature,
            'humidity': self.current_humidity,
            'status': 'ready',
            'door_open': False
        }


class IVCurveTracerInterface(EquipmentInterface):
    """Interface for I-V curve tracers"""

    def __init__(self, equipment_id: str, connection_params: Dict[str, Any]):
        super().__init__(equipment_id, connection_params)
        self.measurement_mode = 'auto'

    def connect(self) -> bool:
        """Connect to I-V curve tracer"""
        try:
            logger.info(f"Connecting to I-V curve tracer {self.equipment_id}")
            self.is_connected = True
            self.last_communication = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def disconnect(self) -> bool:
        """Disconnect from I-V curve tracer"""
        logger.info(f"Disconnecting from I-V curve tracer {self.equipment_id}")
        self.is_connected = False
        return True

    def measure_iv_curve(
        self,
        voltage_range: tuple = (0, 50),
        points: int = 100
    ) -> Dict[str, List[float]]:
        """
        Measure I-V curve

        Args:
            voltage_range: (min_voltage, max_voltage) in volts
            points: Number of measurement points

        Returns:
            Dict with voltage and current arrays
        """
        try:
            logger.info(f"Measuring I-V curve: {voltage_range}V, {points} points")

            # In production: actual measurement from equipment
            # Placeholder: simulate typical I-V curve
            import numpy as np

            v_min, v_max = voltage_range
            voltage = np.linspace(v_min, v_max, points)

            # Simplified I-V model for demonstration
            isc = 8.5  # A
            voc = 45.0  # V
            current = isc * (1 - voltage / voc) * np.exp(-voltage / (voc * 0.1))

            self.last_communication = datetime.utcnow()

            return {
                'voltage': voltage.tolist(),
                'current': current.tolist(),
                'timestamp': datetime.utcnow().isoformat(),
                'points': points
            }

        except Exception as e:
            logger.error(f"I-V measurement failed: {e}")
            return {'voltage': [], 'current': []}

    def read_data(self) -> Dict[str, Any]:
        """Read current measurement data"""
        return self.measure_iv_curve()

    def send_command(self, command: str) -> bool:
        """Send command to I-V tracer"""
        logger.debug(f"Sending command: {command}")
        self.last_communication = datetime.utcnow()
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get I-V tracer status"""
        return {
            'equipment_id': self.equipment_id,
            'is_connected': self.is_connected,
            'measurement_mode': self.measurement_mode,
            'status': 'ready'
        }


class EquipmentManager:
    """Manager for all equipment interfaces"""

    def __init__(self):
        self.equipment = {}

    def register_equipment(self, equipment_id: str, interface: EquipmentInterface):
        """Register equipment interface"""
        self.equipment[equipment_id] = interface
        logger.info(f"Registered equipment: {equipment_id}")

    def get_equipment(self, equipment_id: str) -> Optional[EquipmentInterface]:
        """Get equipment interface by ID"""
        return self.equipment.get(equipment_id)

    def connect_all(self) -> Dict[str, bool]:
        """Connect to all registered equipment"""
        results = {}
        for eq_id, interface in self.equipment.items():
            results[eq_id] = interface.connect()
        return results

    def disconnect_all(self) -> Dict[str, bool]:
        """Disconnect from all equipment"""
        results = {}
        for eq_id, interface in self.equipment.items():
            results[eq_id] = interface.disconnect()
        return results

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all equipment"""
        status = {}
        for eq_id, interface in self.equipment.items():
            status[eq_id] = interface.get_status()
        return status
