"""
NC/OFI Tracking Page
====================
Track non-conformances and opportunities for improvement.
"""

import streamlit as st
from datetime import datetime, timedelta
from config.database import get_db
from models.nc_ofi import NC_OFI, FindingType, Severity, NCStatus
from models.user import User
from components.auth import check_authentication, render_user_info
from components.tables import render_nc_ofi_table
from utils.excel_export import export_nc_ofi_to_excel


st.set_page_config(page_title="NC/OFI Tracking", page_icon="⚠️", layout="wide")


def main():
    """Main NC/OFI tracking page"""
    if not check_authentication():
        st.error("Please login to access this page.")
        st.stop()

    st.title("⚠️ NC/OFI Tracking")
    st.markdown("Track and manage non-conformances and opportunities for improvement")

    with st.sidebar:
        st.title("🎯 Navigation")
        render_user_info()

    tabs = st.tabs(["📋 All NC/OFI", "🔴 Open Items", "✅ Closed Items", "📊 Statistics"])

    with tabs[0]:  # All NC/OFI
        st.subheader("All NC/OFI Records")

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            filter_type = st.selectbox("Type", ["All", "NC", "OFI"])

        with col2:
            filter_severity = st.selectbox("Severity", ["All", "Critical", "Major", "Minor", "Observation"])

        with col3:
            filter_status = st.selectbox("Status", ["All"] + [s.value for s in NCStatus])

        with get_db() as db:
            query = db.query(NC_OFI)

            if filter_type != "All":
                query = query.filter(NC_OFI.type == FindingType[filter_type])

            if filter_severity != "All":
                query = query.filter(NC_OFI.severity == Severity[filter_severity.upper()])

            if filter_status != "All":
                query = query.filter(NC_OFI.status == filter_status)

            nc_ofis = query.order_by(NC_OFI.created_at.desc()).all()

        if nc_ofis:
            render_nc_ofi_table(nc_ofis)

            # Export button
            if st.button("📥 Export to Excel"):
                try:
                    output_path = export_nc_ofi_to_excel(nc_ofis)
                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="Download Excel File",
                            data=f.read(),
                            file_name=f"nc_ofi_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    st.success("Export successful!")
                except Exception as e:
                    st.error(f"Export failed: {e}")

            st.info(f"Showing {len(nc_ofis)} record(s)")
        else:
            st.info("No NC/OFI records found.")

    with tabs[1]:  # Open Items
        st.subheader("Open NC/OFI Items")

        with get_db() as db:
            open_items = db.query(NC_OFI).filter(
                NC_OFI.status.in_([NCStatus.OPEN, NCStatus.IN_PROGRESS])
            ).order_by(NC_OFI.created_at).all()

        if open_items:
            for nc in open_items:
                severity_color = {
                    Severity.CRITICAL: "🔴",
                    Severity.MAJOR: "🟠",
                    Severity.MINOR: "🟡",
                    Severity.OBSERVATION: "🟢"
                }.get(nc.severity, "⚪")

                with st.expander(f"{severity_color} {nc.nc_number} - {nc.type.value.upper()} - {nc.category}"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**Severity:** {nc.severity.value}")
                        st.write(f"**Clause:** {nc.clause or 'N/A'}")
                        st.write(f"**Description:** {nc.description}")
                        st.write(f"**Assignee:** {nc.assignee.full_name if nc.assignee else 'Unassigned'}")
                        st.write(f"**Due Date:** {nc.due_date.strftime('%Y-%m-%d') if nc.due_date else 'Not set'}")
                        st.write(f"**Status:** {nc.status.value}")
                        st.write(f"**Created:** {nc.created_at.strftime('%Y-%m-%d')}")

                    with col2:
                        if st.button("Update Status", key=f"update_{nc.id}"):
                            st.session_state.update_nc_id = nc.id
                            st.rerun()

                        if st.button("Close", key=f"close_{nc.id}"):
                            with get_db() as db:
                                nc_obj = db.query(NC_OFI).filter_by(id=nc.id).first()
                                nc_obj.status = NCStatus.CLOSED
                                nc_obj.closed_at = datetime.utcnow()
                                db.commit()
                            st.success(f"{nc.nc_number} closed!")
                            st.rerun()

            st.info(f"Total open items: {len(open_items)}")
        else:
            st.success("No open NC/OFI items!")

    with tabs[2]:  # Closed Items
        st.subheader("Closed NC/OFI Items")

        with get_db() as db:
            closed_items = db.query(NC_OFI).filter(
                NC_OFI.status == NCStatus.CLOSED
            ).order_by(NC_OFI.closed_at.desc()).limit(50).all()

        if closed_items:
            render_nc_ofi_table(closed_items)
            st.info(f"Showing {len(closed_items)} most recent closed items")
        else:
            st.info("No closed items found.")

    with tabs[3]:  # Statistics
        st.subheader("NC/OFI Statistics")

        with get_db() as db:
            total_nc = db.query(NC_OFI).filter(NC_OFI.type == FindingType.NC).count()
            total_ofi = db.query(NC_OFI).filter(NC_OFI.type == FindingType.OFI).count()
            open_nc = db.query(NC_OFI).filter(
                NC_OFI.type == FindingType.NC,
                NC_OFI.status.in_([NCStatus.OPEN, NCStatus.IN_PROGRESS])
            ).count()
            closed_nc = db.query(NC_OFI).filter(
                NC_OFI.type == FindingType.NC,
                NC_OFI.status == NCStatus.CLOSED
            ).count()

            # By severity
            critical = db.query(NC_OFI).filter(NC_OFI.severity == Severity.CRITICAL).count()
            major = db.query(NC_OFI).filter(NC_OFI.severity == Severity.MAJOR).count()
            minor = db.query(NC_OFI).filter(NC_OFI.severity == Severity.MINOR).count()

        # Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total NC", total_nc, delta=f"{open_nc} open")

        with col2:
            st.metric("Total OFI", total_ofi)

        with col3:
            st.metric("Closed NC", closed_nc)

        with col4:
            closure_rate = (closed_nc / total_nc * 100) if total_nc > 0 else 0
            st.metric("Closure Rate", f"{closure_rate:.1f}%")

        # Severity breakdown
        st.markdown("### By Severity")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("🔴 Critical", critical)

        with col2:
            st.metric("🟠 Major", major)

        with col3:
            st.metric("🟡 Minor", minor)


if __name__ == "__main__":
    main()
