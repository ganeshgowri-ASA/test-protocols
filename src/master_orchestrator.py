"""
Master Orchestration System
Central coordination of all 54 protocols and 5 integration modules
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib
import sqlite3

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class MasterOrchestrator:
    """
    Master orchestration system for all PV testing protocols
    Coordinates protocols PVTP-001 through PVTP-054 and all integration modules
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize master orchestrator"""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()

        # Initialize subsystems
        self.dashboard = None
        self.traceability = None
        self.project_mgmt = None
        self.qms_lims = None
        self.continuous_improvement = None

        # Protocol registry
        self.protocols = {}

        # Initialize all systems
        self._initialize_systems()

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load system configuration"""
        default_config = {
            "database_path": "./data/master.db",
            "log_level": "INFO",
            "max_concurrent_tests": 10,
            "data_retention_days": 3650,  # 10 years
            "enable_blockchain": True,
            "enable_notifications": True,
            "integration_modules": {
                "dashboard": True,
                "traceability": True,
                "project_management": True,
                "qms_lims": True,
                "continuous_improvement": True
            }
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def _setup_logging(self) -> logging.Logger:
        """Setup logging system"""
        logger = logging.getLogger("MasterOrchestrator")
        logger.setLevel(getattr(logging, self.config['log_level']))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler
        log_dir = Path("./logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(
            log_dir / f"orchestrator_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)

        return logger

    def _initialize_systems(self):
        """Initialize all integration modules"""
        self.logger.info("Initializing master orchestration system...")

        try:
            # Initialize database
            self._initialize_database()

            # Load all protocols
            self._load_protocols()

            # Initialize integration modules
            if self.config['integration_modules']['dashboard']:
                self._initialize_dashboard()

            if self.config['integration_modules']['traceability']:
                self._initialize_traceability()

            if self.config['integration_modules']['project_management']:
                self._initialize_project_management()

            if self.config['integration_modules']['qms_lims']:
                self._initialize_qms_lims()

            if self.config['integration_modules']['continuous_improvement']:
                self._initialize_continuous_improvement()

            self.logger.info("All systems initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize systems: {str(e)}")
            raise

    def _initialize_database(self):
        """Initialize master database"""
        self.logger.info("Initializing master database...")

        db_path = Path(self.config['database_path'])
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Create master tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS protocols (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                category TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_sessions (
                session_id TEXT PRIMARY KEY,
                protocol_id TEXT NOT NULL,
                sample_id TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                assigned_to TEXT,
                FOREIGN KEY (protocol_id) REFERENCES protocols(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_test_sessions_protocol
            ON test_sessions(protocol_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_test_sessions_status
            ON test_sessions(status)
        """)

        conn.commit()
        conn.close()

        self.logger.info("Master database initialized")

    def _load_protocols(self):
        """Load all protocol definitions"""
        self.logger.info("Loading protocol definitions...")

        protocols_dir = Path("./protocols")

        if not protocols_dir.exists():
            self.logger.warning("Protocols directory not found")
            return

        # Load protocols 001-054
        for i in range(1, 55):
            protocol_id = f"PVTP-{i:03d}"
            protocol_path = protocols_dir / f"pvtp-{i:03d}" / "protocol.json"

            if protocol_path.exists():
                try:
                    with open(protocol_path, 'r') as f:
                        protocol_data = json.load(f)
                        self.protocols[protocol_id] = protocol_data
                        self.logger.debug(f"Loaded {protocol_id}")
                except Exception as e:
                    self.logger.error(f"Failed to load {protocol_id}: {str(e)}")

        self.logger.info(f"Loaded {len(self.protocols)} protocols")

        # Register protocols in database
        self._register_protocols_in_db()

    def _register_protocols_in_db(self):
        """Register all protocols in master database"""
        conn = sqlite3.connect(self.config['database_path'])
        cursor = conn.cursor()

        for protocol_id, protocol_data in self.protocols.items():
            protocol_info = protocol_data.get('protocol', {})

            cursor.execute("""
                INSERT OR REPLACE INTO protocols
                (id, name, version, category, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                protocol_id,
                protocol_info.get('title', ''),
                protocol_info.get('version', '1.0.0'),
                protocol_info.get('category', ''),
                protocol_info.get('status', 'active')
            ))

        conn.commit()
        conn.close()

    def _initialize_dashboard(self):
        """Initialize dashboard module"""
        try:
            from integrations.dashboard.master_dashboard import MasterDashboard
            self.dashboard = MasterDashboard()
            self.logger.info("Dashboard initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize dashboard: {str(e)}")

    def _initialize_traceability(self):
        """Initialize traceability module"""
        try:
            from integrations.traceability.traceability_engine import TraceabilityEngine
            self.traceability = TraceabilityEngine()
            self.logger.info("Traceability engine initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize traceability: {str(e)}")

    def _initialize_project_management(self):
        """Initialize project management module"""
        try:
            from integrations.project_mgmt.project_manager import ProjectManager
            self.project_mgmt = ProjectManager()
            self.logger.info("Project management initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize project management: {str(e)}")

    def _initialize_qms_lims(self):
        """Initialize QMS/LIMS module"""
        try:
            from integrations.qms_lims.qms_connector import QMSConnector
            from integrations.qms_lims.lims_connector import LIMSConnector

            self.qms_lims = {
                'qms': QMSConnector(),
                'lims': LIMSConnector()
            }
            self.logger.info("QMS/LIMS connectors initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize QMS/LIMS: {str(e)}")

    def _initialize_continuous_improvement(self):
        """Initialize continuous improvement module"""
        try:
            from integrations.continuous_improvement.improvement_engine import ImprovementEngine
            self.continuous_improvement = ImprovementEngine()
            self.logger.info("Continuous improvement initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize continuous improvement: {str(e)}")

    # Core orchestration methods

    def execute_protocol(self, protocol_id: str, sample_id: str,
                        test_data: Dict, user_id: str) -> Dict[str, Any]:
        """
        Execute a protocol test

        Args:
            protocol_id: Protocol identifier (e.g., 'PVTP-048')
            sample_id: Sample identifier
            test_data: Test input data
            user_id: User executing the test

        Returns:
            Test results dictionary
        """
        self.logger.info(f"Executing {protocol_id} for sample {sample_id}")

        # Validate protocol exists
        if protocol_id not in self.protocols:
            raise ValueError(f"Protocol {protocol_id} not found")

        # Create test session
        session_id = self._create_test_session(protocol_id, sample_id, user_id)

        try:
            # Load protocol handler
            handler = self._load_protocol_handler(protocol_id)
            validator = self._load_protocol_validator(protocol_id)
            reporter = self._load_protocol_reporter(protocol_id)

            # Record data lineage (traceability)
            if self.traceability:
                self.traceability.record_data_input(session_id, test_data)

            # Execute test
            results = handler.process(test_data)

            # Validate results
            is_valid, violations = validator.validate_all(results)

            # Generate report
            report = reporter.generate_full_report()

            # Update test session
            self._update_test_session(
                session_id,
                'completed' if is_valid else 'failed',
                results
            )

            # Record in QMS if failures
            if not is_valid and self.qms_lims:
                self._create_nonconformance(session_id, violations)

            # Update continuous improvement metrics
            if self.continuous_improvement:
                self.continuous_improvement.record_test_result(
                    protocol_id,
                    is_valid,
                    results
                )

            return {
                'session_id': session_id,
                'status': 'completed' if is_valid else 'failed',
                'results': results,
                'violations': violations,
                'report': report
            }

        except Exception as e:
            self.logger.error(f"Protocol execution failed: {str(e)}")
            self._update_test_session(session_id, 'error', {'error': str(e)})
            raise

    def execute_multiple_protocols(self, test_requests: List[Dict]) -> List[Dict]:
        """
        Execute multiple protocols in parallel

        Args:
            test_requests: List of test request dictionaries

        Returns:
            List of test results
        """
        self.logger.info(f"Executing {len(test_requests)} protocols in parallel")

        results = []
        max_workers = self.config['max_concurrent_tests']

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self.execute_protocol,
                    req['protocol_id'],
                    req['sample_id'],
                    req['test_data'],
                    req['user_id']
                ): req for req in test_requests
            }

            for future in as_completed(futures):
                req = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Failed to execute {req['protocol_id']}: {str(e)}")
                    results.append({
                        'protocol_id': req['protocol_id'],
                        'status': 'error',
                        'error': str(e)
                    })

        return results

    def get_protocol_status(self, protocol_id: str) -> Dict[str, Any]:
        """Get status and statistics for a protocol"""
        conn = sqlite3.connect(self.config['database_path'])
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total_tests,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                MAX(completed_at) as last_run
            FROM test_sessions
            WHERE protocol_id = ?
        """, (protocol_id,))

        row = cursor.fetchone()
        conn.close()

        return {
            'protocol_id': protocol_id,
            'total_tests': row[0],
            'completed': row[1],
            'failed': row[2],
            'last_run': row[3],
            'pass_rate': (row[1] / row[0] * 100) if row[0] > 0 else 0
        }

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'protocols_loaded': len(self.protocols),
            'active_tests': self._get_active_test_count(),
            'modules': {
                'dashboard': self.dashboard is not None,
                'traceability': self.traceability is not None,
                'project_mgmt': self.project_mgmt is not None,
                'qms_lims': self.qms_lims is not None,
                'continuous_improvement': self.continuous_improvement is not None
            },
            'database': self._check_database_health()
        }

    # Helper methods

    def _create_test_session(self, protocol_id: str, sample_id: str, user_id: str) -> str:
        """Create new test session"""
        session_id = f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}-{protocol_id}"

        conn = sqlite3.connect(self.config['database_path'])
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO test_sessions
            (session_id, protocol_id, sample_id, status, started_at, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, protocol_id, sample_id, 'in_progress', datetime.now(), user_id))

        conn.commit()
        conn.close()

        return session_id

    def _update_test_session(self, session_id: str, status: str, results: Dict):
        """Update test session"""
        conn = sqlite3.connect(self.config['database_path'])
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE test_sessions
            SET status = ?, completed_at = ?
            WHERE session_id = ?
        """, (status, datetime.now(), session_id))

        conn.commit()
        conn.close()

    def _load_protocol_handler(self, protocol_id: str):
        """Dynamically load protocol handler"""
        protocol_num = protocol_id.split('-')[1]
        module_path = f"protocols.pvtp_{protocol_num}.handler"

        try:
            module = importlib.import_module(module_path)
            # Return handler class (implementation specific)
            return module
        except ImportError:
            self.logger.warning(f"Handler for {protocol_id} not found, using default")
            return None

    def _load_protocol_validator(self, protocol_id: str):
        """Dynamically load protocol validator"""
        # Similar to handler loading
        return None

    def _load_protocol_reporter(self, protocol_id: str):
        """Dynamically load protocol reporter"""
        # Similar to handler loading
        return None

    def _create_nonconformance(self, session_id: str, violations: List[Dict]):
        """Create nonconformance record in QMS"""
        if self.qms_lims and 'qms' in self.qms_lims:
            for violation in violations:
                self.qms_lims['qms'].create_nc(
                    title=f"Test Failure: {session_id}",
                    description=violation.get('message', ''),
                    severity=violation.get('severity', 'MAJOR'),
                    related_test=session_id
                )

    def _get_active_test_count(self) -> int:
        """Get count of active tests"""
        conn = sqlite3.connect(self.config['database_path'])
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM test_sessions
            WHERE status = 'in_progress'
        """)

        count = cursor.fetchone()[0]
        conn.close()

        return count

    def _check_database_health(self) -> str:
        """Check database health"""
        try:
            conn = sqlite3.connect(self.config['database_path'])
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return "healthy"
        except Exception as e:
            return f"unhealthy: {str(e)}"

    def launch_dashboard(self):
        """Launch the master dashboard"""
        if self.dashboard:
            self.dashboard.render()
        else:
            self.logger.error("Dashboard not initialized")

    def shutdown(self):
        """Gracefully shutdown the orchestrator"""
        self.logger.info("Shutting down master orchestrator...")

        # Close any open connections
        # Cleanup resources

        self.logger.info("Shutdown complete")


# CLI Interface
def main():
    """Main entry point for CLI"""
    import argparse

    parser = argparse.ArgumentParser(description="PV Testing Master Orchestrator")
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--dashboard', action='store_true', help='Launch dashboard')
    parser.add_argument('--status', action='store_true', help='Show system status')

    args = parser.parse_args()

    orchestrator = MasterOrchestrator(config_path=args.config)

    if args.dashboard:
        orchestrator.launch_dashboard()
    elif args.status:
        status = orchestrator.get_system_status()
        print(json.dumps(status, indent=2))
    else:
        print("Master Orchestrator initialized")
        print("Use --dashboard to launch UI or --status to check system")


if __name__ == "__main__":
    main()
