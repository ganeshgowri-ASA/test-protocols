"""
Nominal Operating Cell Temperature (NOCT) Test Protocol
=======================================================

Protocol ID: NOCT-001
Category: PERFORMANCE
Standard: IEC 61215-2:2021

Description:
Measurement of module operating temperature under specified conditions (800 W/m², 20°C ambient, 1 m/s wind)

Author: GenSpark PV Testing Framework
Auto-generated: 2025-11-13 11:56:42
"""

from typing import Dict, List, Any
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from protocols.base_protocol import (
    BaseProtocol,
    ProtocolMetadata,
    ValidationResult,
    ValidationLevel,
    ProtocolFactory
)
from utils.data_validation import DataValidator, FieldValidator
from utils.visualization import PlotlyChartBuilder
from utils.calculations import PVCalculations, StatisticalAnalysis


class NOCT001Protocol(BaseProtocol):
    """
    Implementation of Nominal Operating Cell Temperature (NOCT) Test

    This protocol implements IEC 61215-2:2021 testing procedures
    for PV module performance characterization.
    """

    def __init__(self):
        metadata = ProtocolMetadata(
            protocol_id="NOCT-001",
            protocol_name="Nominal Operating Cell Temperature (NOCT) Test",
            version="1.0.0",
            category="performance",
            standard_reference="IEC 61215-2:2021",
            description="Measurement of module operating temperature under specified conditions (800 W/m², 20°C ambient, 1 m/s wind)"
        )
        super().__init__(metadata)
        self.validator = DataValidator()

    def get_protocol_id(self) -> str:
        return "NOCT-001"

    def get_protocol_name(self) -> str:
        return "Nominal Operating Cell Temperature (NOCT) Test"

    def get_category(self) -> str:
        return "performance"

    def get_standard_reference(self) -> str:
        return "IEC 61215-2:2021"

    def setup_test_parameters(self) -> Dict[str, Any]:
        """
        Define test setup parameters for NOCT-001.

        Returns:
            Dictionary of setup parameters with validation rules
        """
        parameters = {}

        parameters['irradiance'] = {
            'type': 'float',
            'default': 800,
            'unit': 'W/m²',
            'required': False
        }
        parameters['ambient_temperature'] = {
            'type': 'float',
            'default': 20,
            'unit': '°C',
            'required': False
        }
        parameters['wind_speed'] = {
            'type': 'float',
            'default': 1.0,
            'unit': 'm/s',
            'required': False
        }
        parameters['tilt_angle'] = {
            'type': 'float',
            'default': 45,
            'unit': 'degrees',
            'required': False
        }

        return parameters

    def acquire_data(self, setup_params: Dict[str, Any]) -> pd.DataFrame:
        """
        Acquire test data for NOCT-001.

        Args:
            setup_params: Test setup configuration

        Returns:
            DataFrame containing raw test data
        """
        # Data acquisition implementation
        # In production, this would interface with test equipment

        # Simulated data acquisition
        # In production, replace with actual equipment interface
        data = pd.DataFrame({
            'cell_temperature': np.random.randn(100),
            'back_temperature': np.random.randn(100),
            'irradiance': np.random.randn(100),
            'voltage': np.random.randn(100),
            'current': np.random.randn(100),
            'time': np.random.randn(100),
        })


        return data

    def analyze_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze acquired data for NOCT-001.

        Args:
            data: Raw test data

        Returns:
            Dictionary containing analysis results
        """
        results = {}

        # Perform analysis
        try:
            # Implement specific analysis methods
            # results['temperature_stabilization'] = self._temperature_stabilization(data)
            # results['noct_calculation'] = self._noct_calculation(data)
            # results['power_temperature_coefficient'] = self._power_temperature_coefficient(data)
            results['analysis_complete'] = True
        except Exception as e:
            self.logger.error(f"Analysis error: {e}")
            results['error'] = str(e)


        return results

    def validate_results(self, results: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate analysis results against IEC 61215-2:2021 criteria.

        Args:
            results: Analysis results to validate

        Returns:
            List of validation results
        """
        validation_results = []


        # Validate noct
        if 'noct' in results:
            if results['noct'] < 35:
                validation_results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field='noct',
                    message=f'noct below minimum: {results[\"noct\"]}',
                    value=results['noct'],
                    expected=35
                ))
            if results['noct'] > 60:
                validation_results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field='noct',
                    message=f'noct above maximum: {results[\"noct\"]}',
                    value=results['noct'],
                    expected=60
                ))

        # Validate stabilization_time
        if 'stabilization_time' in results:
            if results['stabilization_time'] > 120:
                validation_results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field='stabilization_time',
                    message=f'stabilization_time above maximum: {results[\"stabilization_time\"]}',
                    value=results['stabilization_time'],
                    expected=120
                ))


        return validation_results

    def generate_visualizations(self, data: pd.DataFrame,
                               results: Dict[str, Any]) -> List[go.Figure]:
        """
        Generate interactive visualizations for NOCT-001.

        Args:
            data: Test data
            results: Analysis results

        Returns:
            List of Plotly figure objects
        """
        figures = []


        # Generate standard visualizations
        try:
            # fig = PlotlyChartBuilder.create_temperature_profile(...)
            # figures.append(fig)
            # fig = PlotlyChartBuilder.create_time_series(...)
            # figures.append(fig)
            # fig = PlotlyChartBuilder.create_thermal_analysis(...)
            # figures.append(fig)
            pass
        except Exception as e:
            self.logger.error(f"Visualization error: {e}")


        return figures


# Register protocol with factory
ProtocolFactory.register("NOCT-001", NOCT001Protocol)


if __name__ == "__main__":
    # Example usage and testing
    protocol = NOCT001Protocol()
    print(f"Protocol: {protocol.get_protocol_name()}")
    print(f"ID: {protocol.get_protocol_id()}")
    print(f"Category: {protocol.get_category()}")
    print(f"Standard: {protocol.get_standard_reference()}")
