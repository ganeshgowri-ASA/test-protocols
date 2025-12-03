"""
Document Management Module
==========================
Document control, version management, and distribution tracking.
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path
import hashlib

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from components.navigation import render_header, render_sidebar_navigation
from database import (
    Document, DocumentAccessLog, DocumentCategory, DocumentStatus, User
)
from sqlalchemy import select, desc, func

# Page configuration
setup_page_config(page_title="Document Management", page_icon="📄")

# Render navigation
render_header("Document Management", "Document control and version management")
render_sidebar_navigation()


def generate_document_number():
    """Generate unique document number"""
    with get_db() as db:
        count = db.execute(
            select(func.count(Document.id))
        ).scalar() or 0
        return f"DOC-{datetime.now().year}-{count + 1:05d}"


def main():
    """Main document management page"""

    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 Document Library",
        "➕ Add Document",
        "📝 Pending Reviews",
        "📊 Access Log"
    ])

    with tab1:
        render_document_library()

    with tab2:
        render_add_document()

    with tab3:
        render_pending_reviews()

    with tab4:
        render_access_log()


def render_document_library():
    """Render document library with search and filters"""

    st.markdown("### 📚 Document Library")

    # Search and filters
    col1, col2, col3 = st.columns(3)

    with col1:
        search_query = st.text_input("🔍 Search", placeholder="Search by title or number...")

    with col2:
        category_filter = st.selectbox(
            "Category",
            options=["All"] + [c.value.replace('_', ' ').title() for c in DocumentCategory]
        )

    with col3:
        status_filter = st.selectbox(
            "Status",
            options=["All", "Draft", "In Review", "Approved", "Superseded", "Obsolete"]
        )

    # Quick stats
    with get_db() as db:
        total_docs = db.execute(select(func.count(Document.id))).scalar()
        approved_docs = db.execute(
            select(func.count(Document.id))
            .where(Document.status == DocumentStatus.APPROVED)
        ).scalar()
        pending_review = db.execute(
            select(func.count(Document.id))
            .where(Document.status == DocumentStatus.IN_REVIEW)
        ).scalar()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Documents", total_docs or 0)
    col2.metric("Approved", approved_docs or 0)
    col3.metric("Pending Review", pending_review or 0)
    col4.metric("Current Versions", db.execute(
        select(func.count(Document.id))
        .where(Document.is_current_version == True)
    ).scalar() or 0)

    st.divider()

    # Document list
    with get_db() as db:
        query = select(Document).where(Document.is_current_version == True)

        if search_query:
            query = query.where(
                (Document.title.contains(search_query)) |
                (Document.document_number.contains(search_query))
            )

        if category_filter != "All":
            cat_value = category_filter.lower().replace(' ', '_')
            query = query.where(Document.category == DocumentCategory(cat_value))

        if status_filter != "All":
            status_value = status_filter.lower().replace(' ', '_')
            query = query.where(Document.status == DocumentStatus(status_value))

        documents = db.execute(
            query.order_by(Document.category, Document.title)
        ).scalars().all()

        if documents:
            # Group by category
            by_category = {}
            for doc in documents:
                cat = doc.category.value if doc.category else 'other'
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(doc)

            for category, docs in by_category.items():
                st.markdown(f"#### 📁 {category.replace('_', ' ').title()}")

                for doc in docs:
                    status_colors = {
                        DocumentStatus.DRAFT: "🟡",
                        DocumentStatus.IN_REVIEW: "🔵",
                        DocumentStatus.APPROVED: "🟢",
                        DocumentStatus.SUPERSEDED: "⚪",
                        DocumentStatus.OBSOLETE: "🔴"
                    }
                    status_icon = status_colors.get(doc.status, "⚪")

                    with st.expander(f"{status_icon} {doc.document_number} - {doc.title} (v{doc.version})"):
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(f"**Document Number:** {doc.document_number}")
                            st.markdown(f"**Title:** {doc.title}")
                            st.markdown(f"**Category:** {doc.category.value.replace('_', ' ').title() if doc.category else 'N/A'}")
                            st.markdown(f"**Version:** {doc.version}")
                            st.markdown(f"**Revision:** {doc.revision_number}")

                        with col2:
                            st.markdown(f"**Status:** {doc.status.value.upper() if doc.status else 'N/A'}")
                            st.markdown(f"**Department:** {doc.department or 'N/A'}")
                            st.markdown(f"**Effective Date:** {doc.effective_date.strftime('%Y-%m-%d') if doc.effective_date else 'N/A'}")
                            st.markdown(f"**Next Review:** {doc.next_review_date.strftime('%Y-%m-%d') if doc.next_review_date else 'N/A'}")

                        with col3:
                            st.markdown(f"**Access Level:** {doc.access_level or 'Internal'}")

                            if doc.file_path:
                                if st.button("📥 Download", key=f"download_{doc.id}"):
                                    # Log access
                                    log = DocumentAccessLog(
                                        document_id=doc.id,
                                        user_id=1,
                                        user_name="Admin User",
                                        access_type="download"
                                    )
                                    db.add(log)
                                    db.commit()

                                    if Path(doc.file_path).exists():
                                        with open(doc.file_path, 'rb') as f:
                                            st.download_button(
                                                "Download File",
                                                data=f.read(),
                                                file_name=doc.file_name,
                                                key=f"dl_{doc.id}"
                                            )
                                    else:
                                        st.warning("File not found")

                        if doc.description:
                            st.markdown(f"**Description:** {doc.description}")

                        if doc.change_summary:
                            st.info(f"**Change Summary:** {doc.change_summary}")

                        # Action buttons
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            if st.button("👁️ View", key=f"view_{doc.id}"):
                                # Log view
                                log = DocumentAccessLog(
                                    document_id=doc.id,
                                    user_id=1,
                                    user_name="Admin User",
                                    access_type="view"
                                )
                                db.add(log)
                                db.commit()
                                st.info("Document viewer")

                        with col2:
                            if doc.status == DocumentStatus.APPROVED:
                                if st.button("🔄 New Version", key=f"newver_{doc.id}"):
                                    st.session_state.new_version_doc = doc.id

                        with col3:
                            if doc.status == DocumentStatus.DRAFT:
                                if st.button("📤 Submit Review", key=f"submit_{doc.id}"):
                                    doc.status = DocumentStatus.IN_REVIEW
                                    db.commit()
                                    st.rerun()

                st.markdown("---")
        else:
            st.info("No documents found")


def render_add_document():
    """Render add document form"""

    st.markdown("### ➕ Add New Document")

    with st.form("add_document"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Document Title *", placeholder="e.g., Test Procedure for IV Characterization")

            category = st.selectbox(
                "Category *",
                options=[c.value.replace('_', ' ').title() for c in DocumentCategory]
            )

            document_type = st.selectbox(
                "Document Type",
                options=["PDF", "Word", "Excel", "Image", "Other"]
            )

            department = st.selectbox(
                "Department",
                options=["Quality", "Testing", "Operations", "Administration", "Safety", "All"]
            )

        with col2:
            version = st.text_input("Version", value="1.0")

            effective_date = st.date_input("Effective Date", value=datetime.now().date())

            next_review_date = st.date_input(
                "Next Review Date",
                value=datetime.now().date() + timedelta(days=365)
            )

            access_level = st.selectbox(
                "Access Level",
                options=["Public", "Internal", "Confidential", "Restricted"]
            )

        description = st.text_area("Description", placeholder="Brief description of the document...")

        # File upload
        uploaded_file = st.file_uploader(
            "Upload Document",
            type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg']
        )

        tags = st.text_input("Tags (comma-separated)", placeholder="e.g., testing, procedure, IEC")

        if st.form_submit_button("📄 Create Document", type="primary"):
            if not title:
                st.error("Title is required")
            else:
                try:
                    doc_number = generate_document_number()

                    # Save uploaded file
                    file_path = None
                    file_name = None
                    file_size = None
                    file_hash = None

                    if uploaded_file:
                        docs_dir = Path("static/documents")
                        docs_dir.mkdir(parents=True, exist_ok=True)

                        file_name = uploaded_file.name
                        file_path = str(docs_dir / f"{doc_number}_{file_name}")

                        content = uploaded_file.read()
                        file_size = len(content)
                        file_hash = hashlib.sha256(content).hexdigest()

                        with open(file_path, 'wb') as f:
                            f.write(content)

                    cat_value = category.lower().replace(' ', '_')

                    with get_db() as db:
                        new_doc = Document(
                            document_number=doc_number,
                            title=title,
                            description=description,
                            category=DocumentCategory(cat_value),
                            document_type=document_type.lower(),
                            department=department,
                            version=version,
                            revision_number=1,
                            is_current_version=True,
                            file_path=file_path,
                            file_name=file_name,
                            file_size_bytes=file_size,
                            file_hash=file_hash,
                            status=DocumentStatus.DRAFT,
                            effective_date=datetime.combine(effective_date, datetime.min.time()),
                            next_review_date=datetime.combine(next_review_date, datetime.min.time()),
                            access_level=access_level.lower(),
                            tags=tags.split(',') if tags else None,
                            author_id=1
                        )
                        db.add(new_doc)
                        db.commit()

                    st.success(f"✅ Document created: {doc_number}")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error: {str(e)}")


def render_pending_reviews():
    """Render pending review queue"""

    st.markdown("### 📝 Pending Document Reviews")

    with get_db() as db:
        pending = db.execute(
            select(Document)
            .where(Document.status == DocumentStatus.IN_REVIEW)
            .order_by(Document.updated_at)
        ).scalars().all()

        if pending:
            st.warning(f"⏳ {len(pending)} document(s) pending review")

            for doc in pending:
                with st.container():
                    st.markdown(f"### {doc.document_number} - {doc.title}")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"**Category:** {doc.category.value.replace('_', ' ').title() if doc.category else 'N/A'}")
                        st.markdown(f"**Version:** {doc.version}")

                    with col2:
                        st.markdown(f"**Submitted:** {doc.updated_at.strftime('%Y-%m-%d') if doc.updated_at else 'N/A'}")
                        st.markdown(f"**Department:** {doc.department or 'N/A'}")

                    with col3:
                        if doc.description:
                            st.markdown(f"**Description:** {doc.description[:100]}...")

                    # Review actions
                    review_notes = st.text_area(
                        "Review Comments",
                        key=f"review_{doc.id}",
                        placeholder="Enter review comments..."
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button("✅ Approve", key=f"approve_{doc.id}", type="primary"):
                            doc.status = DocumentStatus.APPROVED
                            doc.reviewer_id = 1
                            doc.review_date = datetime.utcnow()
                            doc.approval_date = datetime.utcnow()
                            doc.approver_id = 1
                            doc.notes = review_notes
                            db.commit()
                            st.success("Document approved!")
                            st.rerun()

                    with col2:
                        if st.button("🔄 Request Changes", key=f"changes_{doc.id}"):
                            doc.status = DocumentStatus.DRAFT
                            doc.notes = f"Changes requested: {review_notes}"
                            db.commit()
                            st.warning("Sent back for revisions")
                            st.rerun()

                    with col3:
                        if st.button("❌ Reject", key=f"reject_{doc.id}"):
                            doc.status = DocumentStatus.OBSOLETE
                            doc.notes = f"Rejected: {review_notes}"
                            db.commit()
                            st.error("Document rejected")
                            st.rerun()

                    st.divider()
        else:
            st.success("No documents pending review!")


def render_access_log():
    """Render document access log"""

    st.markdown("### 📊 Document Access Log")

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        days_filter = st.selectbox(
            "Time Period",
            options=["Last 7 days", "Last 30 days", "Last 90 days", "All time"]
        )

    with col2:
        access_type_filter = st.selectbox(
            "Access Type",
            options=["All", "View", "Download", "Print", "Edit"]
        )

    # Calculate date range
    if days_filter == "Last 7 days":
        start_date = datetime.utcnow() - timedelta(days=7)
    elif days_filter == "Last 30 days":
        start_date = datetime.utcnow() - timedelta(days=30)
    elif days_filter == "Last 90 days":
        start_date = datetime.utcnow() - timedelta(days=90)
    else:
        start_date = None

    with get_db() as db:
        query = select(DocumentAccessLog).order_by(desc(DocumentAccessLog.access_timestamp))

        if start_date:
            query = query.where(DocumentAccessLog.access_timestamp >= start_date)

        if access_type_filter != "All":
            query = query.where(DocumentAccessLog.access_type == access_type_filter.lower())

        logs = db.execute(query.limit(100)).scalars().all()

        if logs:
            # Summary stats
            total_accesses = len(logs)
            unique_users = len(set([l.user_id for l in logs]))
            unique_docs = len(set([l.document_id for l in logs]))

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Accesses", total_accesses)
            col2.metric("Unique Users", unique_users)
            col3.metric("Documents Accessed", unique_docs)

            st.divider()

            # Log table
            for log in logs:
                doc = db.execute(
                    select(Document).where(Document.id == log.document_id)
                ).scalar()

                col1, col2, col3, col4 = st.columns([2, 2, 1, 2])
                col1.markdown(f"**{log.access_timestamp.strftime('%Y-%m-%d %H:%M') if log.access_timestamp else 'N/A'}**")
                col2.markdown(f"{doc.document_number if doc else 'Unknown'}")
                col3.markdown(f"{log.access_type or 'N/A'}")
                col4.markdown(f"{log.user_name or 'Unknown'}")
        else:
            st.info("No access logs found")


if __name__ == "__main__":
    main()
