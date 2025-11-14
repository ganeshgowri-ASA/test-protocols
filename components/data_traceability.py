"""
Data Traceability Component - Audit trail and data lineage
=========================================================
Tracks all data changes and provides complete audit trail.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
import streamlit as st
from sqlalchemy import desc

from config.database import get_db
from database.models import AuditLog, User, TestExecution


def log_action(
    user_id: int,
    action: str,
    table_name: str,
    record_id: int,
    old_values: Dict = None,
    new_values: Dict = None,
    summary: str = None
):
    """
    Log an action to the audit trail

    Args:
        user_id: ID of user performing action
        action: Action type (create, update, delete, etc.)
        table_name: Database table affected
        record_id: ID of affected record
        old_values: Previous values (for updates)
        new_values: New values
        summary: Human-readable summary of changes
    """
    try:
        with get_db() as db:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                table_name=table_name,
                record_id=record_id,
                old_values=old_values,
                new_values=new_values,
                changes_summary=summary,
                created_at=datetime.utcnow()
            )
            db.add(audit_log)
            db.commit()
    except Exception as e:
        print(f"Error logging action: {e}")


def get_audit_trail(
    table_name: str = None,
    record_id: int = None,
    user_id: int = None,
    action: str = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get audit trail entries

    Args:
        table_name: Filter by table name
        record_id: Filter by record ID
        user_id: Filter by user ID
        action: Filter by action type
        limit: Maximum number of entries to return

    Returns:
        List of audit log entries
    """
    try:
        with get_db() as db:
            query = db.query(AuditLog).order_by(desc(AuditLog.created_at))

            if table_name:
                query = query.filter(AuditLog.table_name == table_name)
            if record_id:
                query = query.filter(AuditLog.record_id == record_id)
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            if action:
                query = query.filter(AuditLog.action == action)

            logs = query.limit(limit).all()

            return [
                {
                    'id': log.id,
                    'timestamp': log.created_at,
                    'user_id': log.user_id,
                    'action': log.action,
                    'table': log.table_name,
                    'record_id': log.record_id,
                    'summary': log.changes_summary,
                    'old_values': log.old_values,
                    'new_values': log.new_values
                }
                for log in logs
            ]
    except Exception as e:
        print(f"Error getting audit trail: {e}")
        return []


def render_audit_trail_viewer(
    table_name: str = None,
    record_id: int = None,
    title: str = "Audit Trail"
):
    """
    Render audit trail viewer component

    Args:
        table_name: Filter by table name
        record_id: Filter by record ID
        title: Component title
    """
    st.markdown(f"### 📜 {title}")

    # Get audit trail
    logs = get_audit_trail(table_name=table_name, record_id=record_id)

    if not logs:
        st.info("No audit trail entries found")
        return

    # Display in expandable sections
    for log in logs:
        timestamp_str = log['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        action_emoji = get_action_emoji(log['action'])

        with st.expander(
            f"{action_emoji} {log['action'].upper()} - {timestamp_str}",
            expanded=False
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Table:** {log['table']}")
                st.markdown(f"**Record ID:** {log['record_id']}")

            with col2:
                st.markdown(f"**User ID:** {log['user_id']}")
                st.markdown(f"**Action:** {log['action']}")

            if log['summary']:
                st.markdown(f"**Summary:** {log['summary']}")

            # Show old vs new values
            if log['old_values'] or log['new_values']:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Old Values:**")
                    if log['old_values']:
                        st.json(log['old_values'])
                    else:
                        st.caption("N/A")

                with col2:
                    st.markdown("**New Values:**")
                    if log['new_values']:
                        st.json(log['new_values'])
                    else:
                        st.caption("N/A")


def get_action_emoji(action: str) -> str:
    """Get emoji for action type"""
    emoji_map = {
        'create': '➕',
        'update': '✏️',
        'delete': '🗑️',
        'approve': '✅',
        'reject': '❌',
        'submit': '📤',
        'complete': '🎯'
    }
    return emoji_map.get(action.lower(), '📝')


def get_data_lineage(test_execution_id: int) -> Dict[str, Any]:
    """
    Get complete data lineage for a test execution

    Args:
        test_execution_id: Test execution ID

    Returns:
        Dictionary containing data lineage information
    """
    try:
        with get_db() as db:
            test = db.query(TestExecution).filter(
                TestExecution.id == test_execution_id
            ).first()

            if not test:
                return {}

            lineage = {
                'test_execution': {
                    'id': test.id,
                    'number': test.execution_number,
                    'protocol_id': test.protocol_id,
                    'status': test.status.value if test.status else None
                },
                'service_request': None,
                'sample': {
                    'id': test.sample_id,
                    'qr_code': test.qr_code
                },
                'timeline': [],
                'data_files': test.data_files or [],
                'processing_steps': []
            }

            # Get service request info
            if test.service_request:
                lineage['service_request'] = {
                    'id': test.service_request.id,
                    'number': test.service_request.request_number,
                    'client': test.service_request.client_name
                }

            # Get timeline from audit log
            audit_logs = get_audit_trail(
                table_name='test_executions',
                record_id=test_execution_id
            )

            lineage['timeline'] = [
                {
                    'timestamp': log['timestamp'],
                    'action': log['action'],
                    'summary': log['summary']
                }
                for log in audit_logs
            ]

            return lineage

    except Exception as e:
        print(f"Error getting data lineage: {e}")
        return {}


def render_data_lineage_viewer(test_execution_id: int):
    """
    Render data lineage viewer for a test execution

    Args:
        test_execution_id: Test execution ID
    """
    st.markdown("### 🔍 Data Lineage")

    lineage = get_data_lineage(test_execution_id)

    if not lineage:
        st.error("Could not retrieve data lineage")
        return

    # Test execution info
    st.markdown("#### Test Execution")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Execution Number", lineage['test_execution']['number'])

    with col2:
        st.metric("Protocol ID", lineage['test_execution']['protocol_id'])

    with col3:
        st.metric("Status", lineage['test_execution']['status'] or 'N/A')

    # Service request link
    if lineage['service_request']:
        st.markdown("#### Source Service Request")
        st.info(
            f"**SR Number:** {lineage['service_request']['number']} | "
            f"**Client:** {lineage['service_request']['client']}"
        )

    # Sample information
    st.markdown("#### Sample Information")
    col1, col2 = st.columns(2)

    with col1:
        st.text(f"Sample ID: {lineage['sample']['id']}")

    with col2:
        st.text(f"QR Code: {lineage['sample']['qr_code']}")

    # Timeline
    if lineage['timeline']:
        st.markdown("#### Timeline")

        timeline_df = pd.DataFrame(lineage['timeline'])
        st.dataframe(timeline_df, use_container_width=True)

    # Data files
    if lineage['data_files']:
        st.markdown("#### Data Files")
        for file in lineage['data_files']:
            st.text(f"📄 {file}")


def track_data_modification(
    entity_type: str,
    entity_id: int,
    field_name: str,
    old_value: Any,
    new_value: Any,
    user_id: int,
    reason: str = None
):
    """
    Track a data modification

    Args:
        entity_type: Type of entity (test_execution, service_request, etc.)
        entity_id: ID of entity
        field_name: Name of field modified
        old_value: Previous value
        new_value: New value
        user_id: User making the change
        reason: Reason for change
    """
    log_action(
        user_id=user_id,
        action='update',
        table_name=entity_type,
        record_id=entity_id,
        old_values={field_name: old_value},
        new_values={field_name: new_value},
        summary=f"Modified {field_name}" + (f": {reason}" if reason else "")
    )


def get_modification_history(
    entity_type: str,
    entity_id: int,
    field_name: str = None
) -> pd.DataFrame:
    """
    Get modification history for an entity/field

    Args:
        entity_type: Type of entity
        entity_id: ID of entity
        field_name: Specific field name (optional)

    Returns:
        DataFrame with modification history
    """
    logs = get_audit_trail(table_name=entity_type, record_id=entity_id)

    modifications = []

    for log in logs:
        if log['action'] == 'update':
            old_vals = log['old_values'] or {}
            new_vals = log['new_values'] or {}

            if field_name:
                if field_name in old_vals or field_name in new_vals:
                    modifications.append({
                        'timestamp': log['timestamp'],
                        'field': field_name,
                        'old_value': old_vals.get(field_name),
                        'new_value': new_vals.get(field_name),
                        'user_id': log['user_id']
                    })
            else:
                # All fields
                all_fields = set(list(old_vals.keys()) + list(new_vals.keys()))
                for field in all_fields:
                    modifications.append({
                        'timestamp': log['timestamp'],
                        'field': field,
                        'old_value': old_vals.get(field),
                        'new_value': new_vals.get(field),
                        'user_id': log['user_id']
                    })

    return pd.DataFrame(modifications)


def verify_data_integrity(test_execution_id: int) -> Dict[str, Any]:
    """
    Verify data integrity for a test execution

    Args:
        test_execution_id: Test execution ID

    Returns:
        Dictionary with integrity check results
    """
    results = {
        'is_valid': True,
        'checks': [],
        'warnings': [],
        'errors': []
    }

    try:
        with get_db() as db:
            test = db.query(TestExecution).filter(
                TestExecution.id == test_execution_id
            ).first()

            if not test:
                results['is_valid'] = False
                results['errors'].append("Test execution not found")
                return results

            # Check 1: Service request exists
            if not test.service_request_id:
                results['warnings'].append("No service request linked")
            else:
                results['checks'].append("✓ Service request linked")

            # Check 2: Sample identified
            if not test.sample_id:
                results['warnings'].append("No sample ID")
            else:
                results['checks'].append("✓ Sample identified")

            # Check 3: Raw data present
            if not test.raw_data:
                results['warnings'].append("No raw data")
            else:
                results['checks'].append("✓ Raw data present")

            # Check 4: Processed data present
            if test.status == 'completed' and not test.processed_data:
                results['warnings'].append("Missing processed data")
            else:
                results['checks'].append("✓ Processed data present")

            # Check 5: Audit trail exists
            audit_count = len(get_audit_trail(
                table_name='test_executions',
                record_id=test_execution_id,
                limit=1
            ))
            if audit_count > 0:
                results['checks'].append("✓ Audit trail present")
            else:
                results['warnings'].append("No audit trail")

    except Exception as e:
        results['is_valid'] = False
        results['errors'].append(f"Integrity check failed: {str(e)}")

    return results
