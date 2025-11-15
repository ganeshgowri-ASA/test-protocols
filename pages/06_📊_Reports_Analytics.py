"""
Reports & Analytics Page
========================
View dashboards, generate reports, and analyze trends.
"""

import streamlit as st
from datetime import datetime
from config.database import get_db
from models.audit import Audit
from models.nc_ofi import NC_OFI
from components.auth import check_authentication, render_user_info
from components.charts import render_audit_dashboard, render_nc_trends, render_entity_audit_heatmap
from utils.pdf_generator import generate_audit_report_pdf, generate_nc_ofi_report_pdf


st.set_page_config(page_title="Reports & Analytics", page_icon="📊", layout="wide")


def main():
    """Main reports and analytics page"""
    if not check_authentication():
        st.error("Please login to access this page.")
        st.stop()

    st.title("📊 Reports & Analytics")
    st.markdown("View analytics and generate reports")

    with st.sidebar:
        st.title("🎯 Navigation")
        render_user_info()

    tabs = st.tabs(["📈 Dashboard", "📄 Generate Reports", "📉 Trends", "🗺️ Entity Analytics"])

    with tabs[0]:  # Dashboard
        st.subheader("Audit Analytics Dashboard")
        render_audit_dashboard()

    with tabs[1]:  # Generate Reports
        st.subheader("Generate Reports")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Audit Report")

            with get_db() as db:
                audits = db.query(Audit).order_by(Audit.created_at.desc()).limit(50).all()

            if audits:
                audit_options = [f"{a.audit_number} - {a.schedule.auditee_entity.name if a.schedule else 'N/A'}"
                                for a in audits]
                selected_audit_idx = st.selectbox("Select Audit", range(len(audit_options)),
                                                 format_func=lambda x: audit_options[x])

                if st.button("Generate Audit PDF Report"):
                    try:
                        audit = audits[selected_audit_idx]
                        pdf_path = generate_audit_report_pdf(audit)

                        with open(pdf_path, 'rb') as f:
                            st.download_button(
                                label="Download PDF Report",
                                data=f.read(),
                                file_name=f"audit_report_{audit.audit_number}.pdf",
                                mime="application/pdf"
                            )
                        st.success("PDF report generated successfully!")

                    except Exception as e:
                        st.error(f"Error generating report: {e}")
            else:
                st.info("No audits available for reporting.")

        with col2:
            st.markdown("### NC/OFI Report")

            if st.button("Generate NC/OFI PDF Report"):
                try:
                    with get_db() as db:
                        nc_ofis = db.query(NC_OFI).order_by(NC_OFI.created_at.desc()).limit(100).all()

                    if nc_ofis:
                        pdf_path = generate_nc_ofi_report_pdf(nc_ofis)

                        with open(pdf_path, 'rb') as f:
                            st.download_button(
                                label="Download PDF Report",
                                data=f.read(),
                                file_name=f"nc_ofi_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf"
                            )
                        st.success("PDF report generated successfully!")
                    else:
                        st.warning("No NC/OFI records found.")

                except Exception as e:
                    st.error(f"Error generating report: {e}")

    with tabs[2]:  # Trends
        st.subheader("NC/OFI Trends")

        months = st.slider("Show last N months", min_value=3, max_value=24, value=6)
        render_nc_trends(months)

    with tabs[3]:  # Entity Analytics
        st.subheader("Audits by Entity")
        render_entity_audit_heatmap()


if __name__ == "__main__":
    main()
