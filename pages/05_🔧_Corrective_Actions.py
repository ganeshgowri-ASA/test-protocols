"""
Corrective Actions Page
========================
Manage corrective action requests (CAR) with 8D methodology.
"""

import streamlit as st
from datetime import datetime, timedelta
from config.database import get_db
from models.nc_ofi import NC_OFI, NCStatus
from models.car import CorrectiveAction, CARStatus, CARMethod
from models.user import User
from components.auth import check_authentication, render_user_info


st.set_page_config(page_title="Corrective Actions", page_icon="🔧", layout="wide")


def main():
    """Main corrective actions page"""
    if not check_authentication():
        st.error("Please login to access this page.")
        st.stop()

    st.title("🔧 Corrective Actions (CAR/8D)")
    st.markdown("Manage corrective and preventive actions")

    with st.sidebar:
        st.title("🎯 Navigation")
        render_user_info()

    tabs = st.tabs(["📋 All CARs", "➕ New CAR", "🔄 In Progress", "✅ Completed"])

    with tabs[0]:  # All CARs
        st.subheader("All Corrective Actions")

        with get_db() as db:
            cars = db.query(CorrectiveAction).order_by(
                CorrectiveAction.created_at.desc()
            ).all()

        if cars:
            for car in cars:
                with st.expander(f"🔧 {car.car_number} - {car.nc_ofi.nc_number if car.nc_ofi else 'N/A'}"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**Method:** {car.method.value.upper()}")
                        st.write(f"**Problem:** {car.problem_description[:100]}...")
                        st.write(f"**Root Cause:** {car.root_cause or 'Not identified'}")
                        st.write(f"**Status:** {car.status.value}")
                        st.write(f"**Due Date:** {car.due_date.strftime('%Y-%m-%d') if car.due_date else 'Not set'}")
                        st.write(f"**Verified:** {'Yes' if car.effectiveness_verified else 'No'}")

                    with col2:
                        if st.button("View Details", key=f"view_{car.id}"):
                            st.session_state.view_car_id = car.id
                            st.rerun()

            st.info(f"Total CARs: {len(cars)}")
        else:
            st.info("No corrective actions found.")

    with tabs[1]:  # New CAR
        st.subheader("Create New CAR")

        # Select NC/OFI
        with get_db() as db:
            open_nc_ofis = db.query(NC_OFI).filter(
                NC_OFI.status.in_([NCStatus.OPEN, NCStatus.IN_PROGRESS])
            ).all()

        if not open_nc_ofis:
            st.warning("No open NC/OFI items found. Create an NC/OFI first.")
        else:
            with st.form("create_car"):
                nc_options = [f"{nc.nc_number} - {nc.description[:50]}..." for nc in open_nc_ofis]
                selected_nc_idx = st.selectbox("Select NC/OFI *", range(len(nc_options)),
                                               format_func=lambda x: nc_options[x])

                method = st.selectbox("CAR Method", ["8D", "5WHY", "FISHBONE", "PDCA", "OTHER"])

                problem_description = st.text_area(
                    "Problem Description *",
                    help="D2: Describe the problem in detail"
                )

                containment_actions = st.text_area(
                    "Interim Containment Actions",
                    help="D3: Immediate actions to contain the problem"
                )

                root_cause = st.text_area(
                    "Root Cause Analysis",
                    help="D4: Identify the root cause"
                )

                action_plan = st.text_area(
                    "Permanent Corrective Actions",
                    help="D5: Define permanent corrective actions"
                )

                col1, col2 = st.columns(2)

                with col1:
                    with get_db() as db:
                        users = db.query(User).all()
                    user_options = [f"{u.full_name} ({u.username})" for u in users]
                    assigned_to_idx = st.selectbox("Assign To", range(len(user_options)),
                                                   format_func=lambda x: user_options[x])

                with col2:
                    due_date = st.date_input("Due Date", value=datetime.now() + timedelta(days=30))

                if st.form_submit_button("Create CAR"):
                    if problem_description:
                        try:
                            with get_db() as db:
                                count = db.query(CorrectiveAction).count()
                                car_number = f"CAR-{datetime.now().year}-{count + 1:04d}"

                                new_car = CorrectiveAction(
                                    car_number=car_number,
                                    nc_ofi_id=open_nc_ofis[selected_nc_idx].id,
                                    method=CARMethod[method],
                                    problem_description=problem_description,
                                    containment_actions=containment_actions,
                                    root_cause=root_cause,
                                    action_plan=action_plan,
                                    assigned_to_id=users[assigned_to_idx].id,
                                    due_date=datetime.combine(due_date, datetime.min.time()),
                                    status=CARStatus.IN_PROGRESS,
                                    created_at=datetime.utcnow()
                                )
                                db.add(new_car)
                                db.commit()

                            st.success(f"CAR {car_number} created successfully!")
                            st.balloons()
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error creating CAR: {e}")
                    else:
                        st.error("Please provide a problem description")

    with tabs[2]:  # In Progress
        st.subheader("In Progress CARs")

        with get_db() as db:
            in_progress_cars = db.query(CorrectiveAction).filter(
                CorrectiveAction.status == CARStatus.IN_PROGRESS
            ).all()

        if in_progress_cars:
            for car in in_progress_cars:
                with st.expander(f"🔄 {car.car_number}"):
                    st.write(f"**Problem:** {car.problem_description}")
                    st.write(f"**Assigned To:** {car.assigned_to.full_name if car.assigned_to else 'Unassigned'}")
                    st.write(f"**Due Date:** {car.due_date.strftime('%Y-%m-%d') if car.due_date else 'Not set'}")

                    if st.button("Mark as Pending Verification", key=f"verify_{car.id}"):
                        with get_db() as db:
                            car_obj = db.query(CorrectiveAction).filter_by(id=car.id).first()
                            car_obj.status = CARStatus.PENDING_VERIFICATION
                            car_obj.actual_completion_date = datetime.utcnow()
                            db.commit()
                        st.success("Status updated!")
                        st.rerun()

            st.info(f"In progress: {len(in_progress_cars)}")
        else:
            st.info("No CARs in progress.")

    with tabs[3]:  # Completed
        st.subheader("Completed CARs")

        with get_db() as db:
            completed_cars = db.query(CorrectiveAction).filter(
                CorrectiveAction.status.in_([CARStatus.VERIFIED, CARStatus.CLOSED])
            ).order_by(CorrectiveAction.closed_at.desc()).limit(20).all()

        if completed_cars:
            for car in completed_cars:
                with st.expander(f"✅ {car.car_number}"):
                    st.write(f"**Problem:** {car.problem_description[:100]}...")
                    st.write(f"**Root Cause:** {car.root_cause or 'N/A'}")
                    st.write(f"**Status:** {car.status.value}")
                    st.write(f"**Verified:** {'Yes' if car.effectiveness_verified else 'No'}")
                    st.write(f"**Closed:** {car.closed_at.strftime('%Y-%m-%d') if car.closed_at else 'N/A'}")

            st.info(f"Showing {len(completed_cars)} recent completed CARs")
        else:
            st.info("No completed CARs.")


if __name__ == "__main__":
    main()
