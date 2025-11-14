"""
SPONGE-001 Protocol Implementation
Sponge Effect Testing for PV Modules

This module implements the moisture absorption/desorption testing protocol
for evaluating reversible and irreversible degradation effects.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
from uuid import uuid4

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestPhase(Enum):
    """Test phase enumeration"""
    INITIAL = "initial"
    HUMID = "humid"
    DRY = "dry"
    FINAL = "final"


class TestStatus(Enum):
    """Test status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class TestParameters:
    """Test parameters configuration"""
    humidity_cycles: int = 10
    humid_phase_temperature: float = 85.0
    humid_phase_rh: float = 85.0
    humid_phase_duration: int = 24
    dry_phase_temperature: float = 25.0
    dry_phase_rh: float = 10.0
    dry_phase_duration: int = 24
    measurement_interval: int = 60

    def validate(self, spec: Dict) -> List[str]:
        """Validate parameters against specification"""
        errors = []
        param_spec = spec.get('test_parameters', {})

        for param_name, param_value in asdict(self).items():
            if param_name in param_spec:
                spec_def = param_spec[param_name]
                if 'min' in spec_def and param_value < spec_def['min']:
                    errors.append(f"{param_name} ({param_value}) below minimum ({spec_def['min']})")
                if 'max' in spec_def and param_value > spec_def['max']:
                    errors.append(f"{param_name} ({param_value}) above maximum ({spec_def['max']})")

        return errors


@dataclass
class Measurement:
    """Individual measurement data point"""
    measurement_id: str
    sample_id: str
    cycle_number: int
    phase: str
    timestamp: datetime
    weight_g: Optional[float] = None
    pmax_w: Optional[float] = None
    voc_v: Optional[float] = None
    isc_a: Optional[float] = None
    ff_percent: Optional[float] = None
    temperature_c: Optional[float] = None
    rh_percent: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class AnalysisResults:
    """Analysis results for a sample"""
    sample_id: str
    moisture_absorption_percent: float
    moisture_desorption_percent: float
    pmax_degradation_percent: float
    reversible_degradation_percent: float
    irreversible_degradation_percent: float
    sponge_coefficient: float
    pass_fail: str


class SpongeProtocol:
    """
    SPONGE-001 Protocol Implementation

    Manages test execution, data collection, and analysis for sponge effect testing.
    """

    def __init__(self, spec_path: Optional[Path] = None):
        """
        Initialize protocol handler

        Args:
            spec_path: Path to protocol specification JSON file
        """
        if spec_path is None:
            spec_path = Path(__file__).parent / 'spec.json'

        self.spec_path = Path(spec_path)
        self.spec = self._load_spec()
        self.test_id = str(uuid4())
        self.measurements: List[Measurement] = []
        self.status = TestStatus.PENDING

        logger.info(f"Initialized SPONGE-001 protocol, test_id: {self.test_id}")

    def _load_spec(self) -> Dict:
        """Load and validate protocol specification"""
        try:
            with open(self.spec_path, 'r') as f:
                spec = json.load(f)

            # Validate required fields
            required_fields = ['protocol_id', 'protocol_name', 'version', 'test_parameters']
            for field in required_fields:
                if field not in spec:
                    raise ValueError(f"Missing required field: {field}")

            logger.info(f"Loaded protocol spec: {spec['protocol_id']} v{spec['version']}")
            return spec

        except Exception as e:
            logger.error(f"Failed to load protocol spec: {e}")
            raise

    def create_test_plan(self, params: TestParameters, sample_ids: List[str]) -> Dict:
        """
        Create a test plan with timeline and measurement schedule

        Args:
            params: Test parameters
            sample_ids: List of sample IDs to test

        Returns:
            Dictionary containing test plan details
        """
        # Validate parameters
        validation_errors = params.validate(self.spec)
        if validation_errors:
            raise ValueError(f"Parameter validation failed: {validation_errors}")

        # Calculate timeline
        cycle_duration = params.humid_phase_duration + params.dry_phase_duration
        total_duration = cycle_duration * params.humidity_cycles

        # Generate measurement schedule
        schedule = []
        current_time = datetime.now()

        # Initial measurements
        schedule.append({
            'time': current_time,
            'phase': TestPhase.INITIAL.value,
            'cycle': 0,
            'actions': ['weight', 'iv_curve', 'visual_inspection']
        })

        # Cycle measurements
        for cycle in range(1, params.humidity_cycles + 1):
            # Start humid phase
            current_time += timedelta(hours=params.humid_phase_duration)
            schedule.append({
                'time': current_time,
                'phase': TestPhase.HUMID.value,
                'cycle': cycle,
                'actions': ['weight', 'environmental_check']
            })

            # Start dry phase
            current_time += timedelta(hours=params.dry_phase_duration)
            schedule.append({
                'time': current_time,
                'phase': TestPhase.DRY.value,
                'cycle': cycle,
                'actions': ['weight', 'iv_curve', 'environmental_check']
            })

        # Final measurements
        schedule.append({
            'time': current_time,
            'phase': TestPhase.FINAL.value,
            'cycle': params.humidity_cycles,
            'actions': ['weight', 'iv_curve', 'visual_inspection', 'insulation_resistance']
        })

        test_plan = {
            'test_id': self.test_id,
            'protocol_id': self.spec['protocol_id'],
            'protocol_version': self.spec['version'],
            'parameters': asdict(params),
            'sample_ids': sample_ids,
            'num_samples': len(sample_ids),
            'start_time': datetime.now().isoformat(),
            'estimated_duration_hours': total_duration,
            'estimated_completion': (datetime.now() + timedelta(hours=total_duration)).isoformat(),
            'measurement_schedule': [
                {**item, 'time': item['time'].isoformat()}
                for item in schedule
            ],
            'total_measurements': len(schedule) * len(sample_ids)
        }

        logger.info(f"Created test plan: {params.humidity_cycles} cycles, "
                   f"{len(sample_ids)} samples, {total_duration}h duration")

        return test_plan

    def record_measurement(self, sample_id: str, cycle: int, phase: TestPhase,
                          **kwargs) -> Measurement:
        """
        Record a measurement data point

        Args:
            sample_id: Sample identifier
            cycle: Cycle number
            phase: Current test phase
            **kwargs: Measurement values (weight_g, pmax_w, etc.)

        Returns:
            Measurement object
        """
        measurement = Measurement(
            measurement_id=str(uuid4()),
            sample_id=sample_id,
            cycle_number=cycle,
            phase=phase.value,
            timestamp=datetime.now(),
            **kwargs
        )

        self.measurements.append(measurement)
        logger.debug(f"Recorded measurement for {sample_id}, cycle {cycle}, phase {phase.value}")

        return measurement

    def get_measurements_df(self) -> pd.DataFrame:
        """
        Get all measurements as a pandas DataFrame

        Returns:
            DataFrame with all measurements
        """
        if not self.measurements:
            return pd.DataFrame()

        data = [m.to_dict() for m in self.measurements]
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        return df

    def calculate_moisture_metrics(self, sample_id: str) -> Dict[str, float]:
        """
        Calculate moisture absorption and desorption metrics

        Args:
            sample_id: Sample identifier

        Returns:
            Dictionary with moisture metrics
        """
        df = self.get_measurements_df()
        sample_df = df[df['sample_id'] == sample_id].copy()

        if sample_df.empty:
            raise ValueError(f"No measurements found for sample {sample_id}")

        # Get initial weight
        initial_weight = sample_df[sample_df['phase'] == TestPhase.INITIAL.value]['weight_g'].iloc[0]

        # Calculate absorption (humid phase)
        humid_weights = sample_df[sample_df['phase'] == TestPhase.HUMID.value]['weight_g']
        if len(humid_weights) > 0:
            max_humid_weight = humid_weights.max()
            absorption_percent = ((max_humid_weight - initial_weight) / initial_weight) * 100
        else:
            absorption_percent = 0.0

        # Calculate desorption (dry phase)
        dry_weights = sample_df[sample_df['phase'] == TestPhase.DRY.value]['weight_g']
        if len(dry_weights) > 0 and len(humid_weights) > 0:
            min_dry_weight = dry_weights.min()
            desorption_percent = ((max_humid_weight - min_dry_weight) / max_humid_weight) * 100
        else:
            desorption_percent = 0.0

        # Calculate sponge coefficient
        sponge_coefficient = absorption_percent / desorption_percent if desorption_percent > 0 else 0.0

        # Weight change trend
        weight_changes = sample_df['weight_g'].diff().dropna()
        avg_absorption_rate = weight_changes[weight_changes > 0].mean() if len(weight_changes[weight_changes > 0]) > 0 else 0.0
        avg_desorption_rate = abs(weight_changes[weight_changes < 0].mean()) if len(weight_changes[weight_changes < 0]) > 0 else 0.0

        return {
            'initial_weight_g': initial_weight,
            'max_humid_weight_g': max_humid_weight if len(humid_weights) > 0 else initial_weight,
            'min_dry_weight_g': min_dry_weight if len(dry_weights) > 0 else initial_weight,
            'moisture_absorption_percent': absorption_percent,
            'moisture_desorption_percent': desorption_percent,
            'sponge_coefficient': sponge_coefficient,
            'avg_absorption_rate_g_per_cycle': avg_absorption_rate,
            'avg_desorption_rate_g_per_cycle': avg_desorption_rate
        }

    def calculate_performance_degradation(self, sample_id: str) -> Dict[str, float]:
        """
        Calculate electrical performance degradation metrics

        Args:
            sample_id: Sample identifier

        Returns:
            Dictionary with performance degradation metrics
        """
        df = self.get_measurements_df()
        sample_df = df[df['sample_id'] == sample_id].copy()

        if sample_df.empty:
            raise ValueError(f"No measurements found for sample {sample_id}")

        # Initial performance
        initial_data = sample_df[sample_df['phase'] == TestPhase.INITIAL.value].iloc[0]
        initial_pmax = initial_data['pmax_w']
        initial_voc = initial_data['voc_v']
        initial_isc = initial_data['isc_a']
        initial_ff = initial_data['ff_percent']

        # Final performance
        final_data = sample_df[sample_df['phase'] == TestPhase.FINAL.value]
        if final_data.empty:
            # Use last available dry phase measurement
            final_data = sample_df[sample_df['phase'] == TestPhase.DRY.value].iloc[-1]
        else:
            final_data = final_data.iloc[0]

        final_pmax = final_data['pmax_w']
        final_voc = final_data['voc_v']
        final_isc = final_data['isc_a']
        final_ff = final_data['ff_percent']

        # Calculate degradation percentages
        pmax_degradation = ((initial_pmax - final_pmax) / initial_pmax) * 100 if initial_pmax else 0.0
        voc_degradation = ((initial_voc - final_voc) / initial_voc) * 100 if initial_voc else 0.0
        isc_degradation = ((initial_isc - final_isc) / initial_isc) * 100 if initial_isc else 0.0
        ff_degradation = ((initial_ff - final_ff) / initial_ff) * 100 if initial_ff else 0.0

        # Calculate reversible vs irreversible degradation
        humid_pmax = sample_df[sample_df['phase'] == TestPhase.HUMID.value]['pmax_w']
        dry_pmax = sample_df[sample_df['phase'] == TestPhase.DRY.value]['pmax_w']

        if len(humid_pmax) > 0 and len(dry_pmax) > 0:
            avg_humid_pmax = humid_pmax.mean()
            avg_dry_pmax = dry_pmax.mean()

            # Reversible: performance recovered after drying
            reversible_degradation = ((avg_humid_pmax - avg_dry_pmax) / initial_pmax) * 100

            # Irreversible: permanent loss even after drying
            irreversible_degradation = ((initial_pmax - avg_dry_pmax) / initial_pmax) * 100
        else:
            reversible_degradation = 0.0
            irreversible_degradation = pmax_degradation

        return {
            'initial_pmax_w': initial_pmax,
            'final_pmax_w': final_pmax,
            'pmax_degradation_percent': pmax_degradation,
            'voc_degradation_percent': voc_degradation,
            'isc_degradation_percent': isc_degradation,
            'ff_degradation_percent': ff_degradation,
            'reversible_degradation_percent': reversible_degradation,
            'irreversible_degradation_percent': irreversible_degradation
        }

    def analyze_sample(self, sample_id: str) -> AnalysisResults:
        """
        Perform complete analysis for a sample

        Args:
            sample_id: Sample identifier

        Returns:
            AnalysisResults object
        """
        try:
            moisture_metrics = self.calculate_moisture_metrics(sample_id)
            performance_metrics = self.calculate_performance_degradation(sample_id)

            # Determine pass/fail based on acceptance criteria
            pass_fail = self._evaluate_acceptance_criteria(performance_metrics, moisture_metrics)

            results = AnalysisResults(
                sample_id=sample_id,
                moisture_absorption_percent=moisture_metrics['moisture_absorption_percent'],
                moisture_desorption_percent=moisture_metrics['moisture_desorption_percent'],
                pmax_degradation_percent=performance_metrics['pmax_degradation_percent'],
                reversible_degradation_percent=performance_metrics['reversible_degradation_percent'],
                irreversible_degradation_percent=performance_metrics['irreversible_degradation_percent'],
                sponge_coefficient=moisture_metrics['sponge_coefficient'],
                pass_fail=pass_fail
            )

            logger.info(f"Analysis complete for {sample_id}: {pass_fail}")
            return results

        except Exception as e:
            logger.error(f"Analysis failed for {sample_id}: {e}")
            raise

    def _evaluate_acceptance_criteria(self, performance: Dict, moisture: Dict) -> str:
        """
        Evaluate acceptance criteria from spec

        Args:
            performance: Performance degradation metrics
            moisture: Moisture metrics

        Returns:
            'PASS', 'FAIL', or 'WARNING'
        """
        criteria = self.spec.get('quality_control', {}).get('acceptance_criteria', [])

        has_failure = False
        has_warning = False

        for criterion in criteria:
            param = criterion['parameter']
            threshold = criterion['threshold']
            comparison = criterion['comparison']
            severity = criterion['severity']

            # Get value from metrics
            value = None
            if param == 'pmax_degradation':
                value = performance.get('pmax_degradation_percent')
            elif param == 'moisture_absorption':
                value = moisture.get('moisture_absorption_percent')

            if value is not None:
                # Evaluate criterion
                if comparison == 'less_than' and value >= threshold:
                    if severity == 'fail':
                        has_failure = True
                    else:
                        has_warning = True
                elif comparison == 'greater_than' and value <= threshold:
                    if severity == 'fail':
                        has_failure = True
                    else:
                        has_warning = True

        if has_failure:
            return 'FAIL'
        elif has_warning:
            return 'WARNING'
        else:
            return 'PASS'

    def generate_report(self, output_path: Optional[Path] = None) -> Dict:
        """
        Generate test report with all results

        Args:
            output_path: Optional path to save report JSON

        Returns:
            Dictionary containing complete report
        """
        df = self.get_measurements_df()
        sample_ids = df['sample_id'].unique()

        # Analyze all samples
        sample_analyses = {}
        for sample_id in sample_ids:
            try:
                analysis = self.analyze_sample(sample_id)
                sample_analyses[sample_id] = asdict(analysis)
            except Exception as e:
                logger.error(f"Failed to analyze {sample_id}: {e}")
                sample_analyses[sample_id] = {'error': str(e)}

        # Compile report
        report = {
            'test_id': self.test_id,
            'protocol_id': self.spec['protocol_id'],
            'protocol_version': self.spec['version'],
            'report_date': datetime.now().isoformat(),
            'status': self.status.value,
            'summary': {
                'total_samples': len(sample_ids),
                'total_measurements': len(self.measurements),
                'passed': sum(1 for a in sample_analyses.values() if a.get('pass_fail') == 'PASS'),
                'failed': sum(1 for a in sample_analyses.values() if a.get('pass_fail') == 'FAIL'),
                'warnings': sum(1 for a in sample_analyses.values() if a.get('pass_fail') == 'WARNING')
            },
            'sample_results': sample_analyses,
            'measurements_data': df.to_dict(orient='records') if not df.empty else []
        }

        # Save report if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Report saved to {output_path}")

        return report

    def export_data(self, output_dir: Path, formats: List[str] = None) -> Dict[str, Path]:
        """
        Export test data in various formats

        Args:
            output_dir: Directory to save exported files
            formats: List of formats ('csv', 'json', 'excel')

        Returns:
            Dictionary mapping format to file path
        """
        if formats is None:
            formats = ['csv', 'json']

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        df = self.get_measurements_df()
        exported_files = {}

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"sponge_001_{self.test_id[:8]}_{timestamp}"

        if 'csv' in formats:
            csv_path = output_dir / f"{base_name}.csv"
            df.to_csv(csv_path, index=False)
            exported_files['csv'] = csv_path
            logger.info(f"Exported CSV to {csv_path}")

        if 'json' in formats:
            json_path = output_dir / f"{base_name}.json"
            report = self.generate_report()
            with open(json_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            exported_files['json'] = json_path
            logger.info(f"Exported JSON to {json_path}")

        if 'excel' in formats:
            excel_path = output_dir / f"{base_name}.xlsx"
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Measurements', index=False)

                # Add analysis sheet
                sample_ids = df['sample_id'].unique()
                analyses = []
                for sample_id in sample_ids:
                    try:
                        analysis = self.analyze_sample(sample_id)
                        analyses.append(asdict(analysis))
                    except Exception as e:
                        logger.warning(f"Could not analyze {sample_id}: {e}")

                if analyses:
                    analysis_df = pd.DataFrame(analyses)
                    analysis_df.to_excel(writer, sheet_name='Analysis', index=False)

            exported_files['excel'] = excel_path
            logger.info(f"Exported Excel to {excel_path}")

        return exported_files


# Example usage and testing
if __name__ == "__main__":
    # Initialize protocol
    protocol = SpongeProtocol()

    # Create test parameters
    params = TestParameters(
        humidity_cycles=10,
        humid_phase_temperature=85.0,
        humid_phase_rh=85.0,
        humid_phase_duration=24,
        dry_phase_temperature=25.0,
        dry_phase_rh=10.0,
        dry_phase_duration=24
    )

    # Create test plan
    sample_ids = ['MODULE-001', 'MODULE-002', 'MODULE-003']
    test_plan = protocol.create_test_plan(params, sample_ids)

    print(f"Test Plan Created:")
    print(f"  Test ID: {test_plan['test_id']}")
    print(f"  Duration: {test_plan['estimated_duration_hours']} hours")
    print(f"  Samples: {test_plan['num_samples']}")
    print(f"  Measurements: {test_plan['total_measurements']}")

    # Simulate some measurements
    for sample_id in sample_ids:
        # Initial measurement
        protocol.record_measurement(
            sample_id=sample_id,
            cycle=0,
            phase=TestPhase.INITIAL,
            weight_g=np.random.uniform(18000, 20000),
            pmax_w=np.random.uniform(295, 305),
            voc_v=np.random.uniform(38, 40),
            isc_a=np.random.uniform(8.5, 9.5),
            ff_percent=np.random.uniform(75, 78)
        )

        # Simulate cycles
        for cycle in range(1, 4):  # 3 cycles for demo
            # Humid phase
            protocol.record_measurement(
                sample_id=sample_id,
                cycle=cycle,
                phase=TestPhase.HUMID,
                weight_g=np.random.uniform(18050, 18150),
                temperature_c=85.0,
                rh_percent=85.0
            )

            # Dry phase
            protocol.record_measurement(
                sample_id=sample_id,
                cycle=cycle,
                phase=TestPhase.DRY,
                weight_g=np.random.uniform(18010, 18030),
                pmax_w=np.random.uniform(292, 302),
                voc_v=np.random.uniform(37.5, 39.5),
                isc_a=np.random.uniform(8.4, 9.4),
                ff_percent=np.random.uniform(74.5, 77.5),
                temperature_c=25.0,
                rh_percent=10.0
            )

        # Final measurement
        protocol.record_measurement(
            sample_id=sample_id,
            cycle=3,
            phase=TestPhase.FINAL,
            weight_g=np.random.uniform(18005, 18025),
            pmax_w=np.random.uniform(290, 300),
            voc_v=np.random.uniform(37, 39),
            isc_a=np.random.uniform(8.3, 9.3),
            ff_percent=np.random.uniform(74, 77)
        )

    # Analyze samples
    print("\nSample Analysis:")
    for sample_id in sample_ids:
        analysis = protocol.analyze_sample(sample_id)
        print(f"\n{sample_id}:")
        print(f"  Pmax Degradation: {analysis.pmax_degradation_percent:.2f}%")
        print(f"  Moisture Absorption: {analysis.moisture_absorption_percent:.3f}%")
        print(f"  Sponge Coefficient: {analysis.sponge_coefficient:.3f}")
        print(f"  Status: {analysis.pass_fail}")

    # Generate report
    report = protocol.generate_report()
    print(f"\nTest Summary:")
    print(f"  Total Samples: {report['summary']['total_samples']}")
    print(f"  Passed: {report['summary']['passed']}")
    print(f"  Failed: {report['summary']['failed']}")
    print(f"  Warnings: {report['summary']['warnings']}")
