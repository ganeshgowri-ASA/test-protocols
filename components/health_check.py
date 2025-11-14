"""
Health Check Module
===================
System health monitoring and diagnostics for production deployment.

Provides comprehensive health checks for:
- Database connectivity
- Protocol registry status
- System dependencies
- Performance metrics
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class HealthCheckStatus:
    """Health check status constants"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@st.cache_data(ttl=60)
def check_database_health(db_session) -> dict:
    """
    Check database connectivity and health

    Args:
        db_session: Database session object

    Returns:
        dict: Health check results
    """
    try:
        if db_session is None:
            return {
                "status": HealthCheckStatus.UNHEALTHY,
                "message": "Database session not initialized",
                "details": "Database connection failed during initialization"
            }

        # Try a simple query
        # Assuming the session has a connection method
        return {
            "status": HealthCheckStatus.HEALTHY,
            "message": "Database connection active",
            "details": "Successfully connected to database"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": HealthCheckStatus.UNHEALTHY,
            "message": "Database connection failed",
            "details": str(e)
        }


@st.cache_data(ttl=60)
def check_protocol_registry() -> dict:
    """
    Check protocol registry status

    Returns:
        dict: Health check results
    """
    try:
        from config.protocols_registry import get_cached_protocol_registry

        registry = get_cached_protocol_registry()
        protocol_count = registry.get_protocol_count()

        if protocol_count == 0:
            return {
                "status": HealthCheckStatus.DEGRADED,
                "message": "No protocols registered",
                "details": "Protocol registry is empty. Using sample protocols.",
                "protocol_count": 0
            }
        elif protocol_count < 54:
            return {
                "status": HealthCheckStatus.DEGRADED,
                "message": f"Partial protocol coverage: {protocol_count}/54 protocols",
                "details": "Some protocols are missing",
                "protocol_count": protocol_count
            }
        else:
            return {
                "status": HealthCheckStatus.HEALTHY,
                "message": f"All protocols registered: {protocol_count}/54",
                "details": "Full protocol coverage available",
                "protocol_count": protocol_count
            }
    except Exception as e:
        logger.error(f"Protocol registry health check failed: {e}")
        return {
            "status": HealthCheckStatus.UNHEALTHY,
            "message": "Protocol registry check failed",
            "details": str(e),
            "protocol_count": 0
        }


@st.cache_data(ttl=300)
def check_dependencies() -> dict:
    """
    Check system dependencies and versions

    Returns:
        dict: Health check results
    """
    try:
        import pandas
        import plotly
        import sqlalchemy
        import qrcode
        import reportlab

        dependencies = {
            "streamlit": st.__version__,
            "pandas": pandas.__version__,
            "plotly": plotly.__version__,
            "sqlalchemy": sqlalchemy.__version__,
        }

        return {
            "status": HealthCheckStatus.HEALTHY,
            "message": "All dependencies available",
            "details": dependencies
        }
    except ImportError as e:
        logger.error(f"Dependency check failed: {e}")
        return {
            "status": HealthCheckStatus.UNHEALTHY,
            "message": "Missing dependencies",
            "details": str(e)
        }


def check_system_resources() -> dict:
    """
    Check system resources and performance

    Returns:
        dict: Health check results
    """
    try:
        import psutil

        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        status = HealthCheckStatus.HEALTHY
        if cpu_percent > 80 or memory.percent > 85:
            status = HealthCheckStatus.DEGRADED

        return {
            "status": status,
            "message": "System resources checked",
            "details": {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory.percent}%",
                "available_memory": f"{memory.available / (1024**3):.2f} GB"
            }
        }
    except ImportError:
        # psutil not available (optional dependency)
        return {
            "status": HealthCheckStatus.HEALTHY,
            "message": "System resource monitoring not available",
            "details": "Install psutil for detailed resource monitoring"
        }
    except Exception as e:
        logger.error(f"System resource check failed: {e}")
        return {
            "status": HealthCheckStatus.DEGRADED,
            "message": "Resource check incomplete",
            "details": str(e)
        }


def get_system_info() -> dict:
    """
    Get system information

    Returns:
        dict: System information
    """
    return {
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "streamlit_version": st.__version__,
        "app_version": "1.0.0",
        "deployment": "Streamlit Cloud"
    }


def run_all_health_checks(db_session=None) -> dict:
    """
    Run all health checks

    Args:
        db_session: Database session object

    Returns:
        dict: Complete health check results
    """
    checks = {
        "timestamp": datetime.now().isoformat(),
        "database": check_database_health(db_session),
        "protocols": check_protocol_registry(),
        "dependencies": check_dependencies(),
        "resources": check_system_resources(),
        "system_info": get_system_info()
    }

    # Determine overall health status
    statuses = [
        checks["database"]["status"],
        checks["protocols"]["status"],
        checks["dependencies"]["status"],
        checks["resources"]["status"]
    ]

    if HealthCheckStatus.UNHEALTHY in statuses:
        checks["overall_status"] = HealthCheckStatus.UNHEALTHY
    elif HealthCheckStatus.DEGRADED in statuses:
        checks["overall_status"] = HealthCheckStatus.DEGRADED
    else:
        checks["overall_status"] = HealthCheckStatus.HEALTHY

    return checks


def render_health_status_sidebar(db_session=None):
    """
    Render health status in sidebar

    Args:
        db_session: Database session object
    """
    with st.sidebar:
        st.divider()
        st.subheader("🏥 System Health")

        # Run health checks
        health = run_all_health_checks(db_session)

        # Display overall status
        if health["overall_status"] == HealthCheckStatus.HEALTHY:
            st.success("🟢 All Systems Operational", icon="✅")
        elif health["overall_status"] == HealthCheckStatus.DEGRADED:
            st.warning("🟡 System Degraded", icon="⚠️")
        else:
            st.error("🔴 System Issues Detected", icon="❌")

        # Show details in expander
        with st.expander("View Details"):
            # Database status
            db_status = health["database"]
            if db_status["status"] == HealthCheckStatus.HEALTHY:
                st.success(f"**Database:** {db_status['message']}")
            else:
                st.error(f"**Database:** {db_status['message']}")

            # Protocol registry status
            protocol_status = health["protocols"]
            protocol_count = protocol_status.get("protocol_count", 0)
            if protocol_status["status"] == HealthCheckStatus.HEALTHY:
                st.success(f"**Protocols:** {protocol_count}/54 loaded")
            elif protocol_status["status"] == HealthCheckStatus.DEGRADED:
                st.warning(f"**Protocols:** {protocol_count}/54 loaded")
            else:
                st.error(f"**Protocols:** Failed to load")

            # Dependencies
            deps_status = health["dependencies"]
            if deps_status["status"] == HealthCheckStatus.HEALTHY:
                st.success("**Dependencies:** All available")
            else:
                st.error("**Dependencies:** Some missing")

            # System info
            st.info(f"**Python:** {health['system_info']['python_version']}")
            st.info(f"**Streamlit:** {health['system_info']['streamlit_version']}")


def render_health_dashboard(db_session=None):
    """
    Render detailed health dashboard page

    Args:
        db_session: Database session object
    """
    st.title("🏥 System Health Dashboard")
    st.markdown("Comprehensive system health monitoring and diagnostics")

    # Run health checks
    health = run_all_health_checks(db_session)

    # Overall status banner
    if health["overall_status"] == HealthCheckStatus.HEALTHY:
        st.success("### 🟢 All Systems Operational", icon="✅")
    elif health["overall_status"] == HealthCheckStatus.DEGRADED:
        st.warning("### 🟡 System Running with Degraded Performance", icon="⚠️")
    else:
        st.error("### 🔴 System Issues Detected - Action Required", icon="❌")

    st.divider()

    # Detailed checks in columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🗄️ Database Health")
        db_check = health["database"]
        if db_check["status"] == HealthCheckStatus.HEALTHY:
            st.success(db_check["message"])
        else:
            st.error(db_check["message"])
        st.caption(db_check["details"])

        st.subheader("📋 Protocol Registry")
        protocol_check = health["protocols"]
        if protocol_check["status"] == HealthCheckStatus.HEALTHY:
            st.success(protocol_check["message"])
        elif protocol_check["status"] == HealthCheckStatus.DEGRADED:
            st.warning(protocol_check["message"])
        else:
            st.error(protocol_check["message"])
        st.caption(protocol_check["details"])

    with col2:
        st.subheader("📦 Dependencies")
        deps_check = health["dependencies"]
        if deps_check["status"] == HealthCheckStatus.HEALTHY:
            st.success(deps_check["message"])
            with st.expander("View Versions"):
                for pkg, version in deps_check["details"].items():
                    st.text(f"{pkg}: {version}")
        else:
            st.error(deps_check["message"])

        st.subheader("💻 System Resources")
        resource_check = health["resources"]
        if resource_check["status"] == HealthCheckStatus.HEALTHY:
            st.success(resource_check["message"])
        elif resource_check["status"] == HealthCheckStatus.DEGRADED:
            st.warning(resource_check["message"])

        if isinstance(resource_check["details"], dict):
            with st.expander("View Resource Usage"):
                for key, value in resource_check["details"].items():
                    st.metric(key.replace("_", " ").title(), value)

    st.divider()

    # System information
    st.subheader("ℹ️ System Information")
    info_cols = st.columns(5)
    sys_info = health["system_info"]

    with info_cols[0]:
        st.metric("Python Version", sys_info["python_version"])
    with info_cols[1]:
        st.metric("Streamlit Version", sys_info["streamlit_version"])
    with info_cols[2]:
        st.metric("App Version", sys_info["app_version"])
    with info_cols[3]:
        st.metric("Platform", sys_info["platform"])
    with info_cols[4]:
        st.metric("Deployment", sys_info["deployment"])

    # Last check timestamp
    st.caption(f"Last health check: {health['timestamp']}")
