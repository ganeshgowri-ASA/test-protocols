"""
Entity Management Page
======================
Manage organizational hierarchy (Company → Division → Plant → Department).
"""

import streamlit as st
from datetime import datetime
from config.database import get_db
from models.entity import Entity
from components.auth import check_authentication, render_user_info, require_role
from components.forms import render_entity_form
from components.tables import render_entity_table
from utils.excel_export import export_entities_to_excel


st.set_page_config(page_title="Entity Management", page_icon="🏢", layout="wide")


def render_entity_tree(entities, parent_id=None, level=0):
    """
    Render hierarchical entity tree

    Args:
        entities: List of all entities
        parent_id: Current parent ID (None for root)
        level: Current depth level
    """
    children = [e for e in entities if e.parent_id == parent_id]

    for entity in sorted(children, key=lambda x: x.name):
        indent = "  " * level
        icon = {"Company": "🏢", "Division": "🏭", "Plant": "🏗️", "Department": "📁"}.get(entity.type, "📌")

        with st.expander(f"{indent}{icon} {entity.name} ({entity.type})", expanded=(level < 2)):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**Code:** {entity.code}")
                st.write(f"**Location:** {entity.location or 'N/A'}")
                st.write(f"**Manager:** {entity.manager_name or 'N/A'}")
                st.write(f"**Contact:** {entity.contact_email or 'N/A'}")

            with col2:
                if st.button("Edit", key=f"edit_{entity.id}"):
                    st.session_state.edit_entity_id = entity.id
                    st.rerun()

                if st.button("Delete", key=f"del_{entity.id}"):
                    st.session_state.delete_entity_id = entity.id
                    st.rerun()

        # Recursively render children
        render_entity_tree(entities, entity.id, level + 1)


def main():
    """Main entity management page"""
    if not check_authentication():
        st.error("Please login to access this page.")
        st.stop()

    st.title("🏢 Entity Management")
    st.markdown("Manage your organizational hierarchy")

    # Sidebar
    with st.sidebar:
        st.title("🎯 Navigation")
        render_user_info()

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 View All", "🌳 Hierarchy Tree", "➕ Add Entity"])

    with tab1:
        st.subheader("All Entities")

        with get_db() as db:
            entities = db.query(Entity).order_by(Entity.level, Entity.name).all()

        if entities:
            render_entity_table(entities)

            # Export button
            if st.button("📥 Export to Excel"):
                try:
                    output_path = export_entities_to_excel(entities)
                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="Download Excel File",
                            data=f.read(),
                            file_name=f"entities_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    st.success("Export successful!")
                except Exception as e:
                    st.error(f"Export failed: {e}")
        else:
            st.info("No entities found. Create your first entity in the 'Add Entity' tab.")

    with tab2:
        st.subheader("Organization Hierarchy")

        with get_db() as db:
            entities = db.query(Entity).all()

        if entities:
            render_entity_tree(entities)
        else:
            st.info("No entities found. Create your first entity in the 'Add Entity' tab.")

    with tab3:
        st.subheader("Create New Entity")

        # Check for edit mode
        entity_to_edit = None
        if 'edit_entity_id' in st.session_state:
            with get_db() as db:
                entity_to_edit = db.query(Entity).filter_by(id=st.session_state.edit_entity_id).first()

        form_data = render_entity_form(entity_to_edit)

        if form_data:
            try:
                with get_db() as db:
                    if entity_to_edit:
                        # Update existing entity
                        for key, value in form_data.items():
                            setattr(entity_to_edit, key, value)
                        entity_to_edit.updated_at = datetime.utcnow()
                        db.commit()
                        st.success(f"Entity '{form_data['name']}' updated successfully!")
                        del st.session_state.edit_entity_id
                    else:
                        # Create new entity
                        new_entity = Entity(
                            **form_data,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        db.add(new_entity)
                        db.commit()
                        st.success(f"Entity '{form_data['name']}' created successfully!")

                st.rerun()

            except Exception as e:
                st.error(f"Error saving entity: {e}")

    # Handle delete
    if 'delete_entity_id' in st.session_state:
        with get_db() as db:
            entity = db.query(Entity).filter_by(id=st.session_state.delete_entity_id).first()
            if entity:
                # Check if entity has children
                children = db.query(Entity).filter_by(parent_id=entity.id).count()
                if children > 0:
                    st.error(f"Cannot delete '{entity.name}' - it has {children} child entities.")
                else:
                    db.delete(entity)
                    db.commit()
                    st.success(f"Entity '{entity.name}' deleted successfully!")

        del st.session_state.delete_entity_id
        st.rerun()


if __name__ == "__main__":
    main()
