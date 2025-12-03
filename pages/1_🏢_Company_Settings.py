"""
Company Settings Module
=======================
Manage company profile, branding, and accreditation information.

This page provides a comprehensive interface for configuring:
- Company profile and contact information
- Logo management with image upload
- Address and location details
- Industry type and accreditation credentials
"""

import streamlit as st
from datetime import datetime, date
import sys
from pathlib import Path
from io import BytesIO
import base64

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from config.settings import setup_page_config, config, apply_custom_css
from config.database import get_db
from components.navigation import render_header, render_sidebar_navigation, clear_company_branding_cache
from database import CompanyProfile, IndustryType

# Page configuration
setup_page_config(page_title="Company Settings", page_icon="🏢")

# Constants for image validation
MAX_LOGO_SIZE_MB = 5
ALLOWED_LOGO_TYPES = ["image/png", "image/jpeg", "image/jpg"]
ALLOWED_LOGO_EXTENSIONS = [".png", ".jpg", ".jpeg"]

# US States list for dropdown
US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming", "District of Columbia", "Other"
]

# Countries list for dropdown
COUNTRIES = [
    "United States", "Canada", "Mexico", "United Kingdom", "Germany", "France", "Italy",
    "Spain", "Netherlands", "Belgium", "Switzerland", "Austria", "Australia", "New Zealand",
    "Japan", "South Korea", "China", "India", "Singapore", "Malaysia", "Thailand", "Vietnam",
    "Brazil", "Argentina", "Chile", "Colombia", "South Africa", "United Arab Emirates",
    "Saudi Arabia", "Israel", "Turkey", "Other"
]

# Industry type display names
INDUSTRY_TYPE_DISPLAY = {
    IndustryType.SOLAR_PV_TESTING: "Solar PV Testing Laboratory",
    IndustryType.RENEWABLE_ENERGY: "Renewable Energy",
    IndustryType.ELECTRICAL_TESTING: "Electrical Testing",
    IndustryType.MATERIALS_TESTING: "Materials Testing",
    IndustryType.ENVIRONMENTAL_TESTING: "Environmental Testing",
    IndustryType.CERTIFICATION_BODY: "Certification Body",
    IndustryType.RESEARCH_INSTITUTION: "Research Institution",
    IndustryType.MANUFACTURING: "Manufacturing",
    IndustryType.CONSULTING: "Consulting",
    IndustryType.OTHER: "Other"
}

# Accreditation standards
ACCREDITATION_STANDARDS = {
    "ISO_17025": {
        "name": "ISO/IEC 17025",
        "description": "General requirements for the competence of testing and calibration laboratories"
    },
    "ISO_9001": {
        "name": "ISO 9001",
        "description": "Quality management systems requirements"
    },
    "IEC_61215": {
        "name": "IEC 61215",
        "description": "Terrestrial photovoltaic (PV) modules - Design qualification and type approval"
    },
    "IEC_61730": {
        "name": "IEC 61730",
        "description": "Photovoltaic (PV) module safety qualification"
    },
    "UL_1703": {
        "name": "UL 1703",
        "description": "Standard for Flat-Plate Photovoltaic Modules and Panels"
    },
    "IEC_61646": {
        "name": "IEC 61646",
        "description": "Thin-film terrestrial photovoltaic (PV) modules"
    },
    "IEC_62108": {
        "name": "IEC 62108",
        "description": "Concentrator photovoltaic (CPV) modules and assemblies"
    },
    "IECEE_CB": {
        "name": "IECEE CB Scheme",
        "description": "International certification scheme for electrical equipment"
    }
}


def get_company_profile():
    """
    Get or create the default company profile

    Returns:
        CompanyProfile instance (or None on error)
    """
    try:
        with get_db() as db:
            profile = CompanyProfile.get_default(db)
            # Eagerly load all attributes to avoid DetachedInstanceError
            profile_data = {
                'id': profile.id,
                'company_id': profile.company_id,
                'company_name': profile.company_name,
                'company_logo': profile.company_logo,
                'logo_filename': profile.logo_filename,
                'logo_content_type': profile.logo_content_type,
                'phone': profile.phone,
                'email': profile.email,
                'website': profile.website,
                'address': profile.address,
                'city': profile.city,
                'state': profile.state,
                'zip_code': profile.zip_code,
                'country': profile.country,
                'industry_type': profile.industry_type,
                'established_date': profile.established_date,
                'employees_count': profile.employees_count,
                'tax_id': profile.tax_id,
                'registration_id': profile.registration_id,
                'accreditation_details': profile.accreditation_details or {},
                'accreditation_notes': profile.accreditation_notes,
                'description': profile.description,
                'tagline': profile.tagline,
                'created_at': profile.created_at,
                'updated_at': profile.updated_at
            }
            return profile_data
    except Exception as e:
        st.error(f"Error loading company profile: {str(e)}")
        return None


def save_company_profile(profile_data: dict, logo_data: dict = None) -> bool:
    """
    Save company profile to database

    Args:
        profile_data: Dictionary with profile field values
        logo_data: Optional dictionary with logo binary data and metadata

    Returns:
        True if save successful, False otherwise
    """
    try:
        from sqlalchemy import select
        with get_db() as db:
            profile = db.execute(
                select(CompanyProfile).where(CompanyProfile.company_id == "DEFAULT")
            ).scalar_one_or_none()

            if not profile:
                profile = CompanyProfile(company_id="DEFAULT")
                db.add(profile)

            # Update fields from profile_data
            for field, value in profile_data.items():
                if hasattr(profile, field) and field not in ['id', 'company_id', 'created_at', 'updated_at']:
                    setattr(profile, field, value)

            # Update logo if provided
            if logo_data:
                profile.company_logo = logo_data.get('data')
                profile.logo_filename = logo_data.get('filename')
                profile.logo_content_type = logo_data.get('content_type')

            profile.updated_at = datetime.utcnow()
            db.commit()
            return True

    except Exception as e:
        st.error(f"Error saving company profile: {str(e)}")
        return False


def clear_company_logo() -> bool:
    """
    Remove company logo from profile

    Returns:
        True if successful, False otherwise
    """
    try:
        from sqlalchemy import select
        with get_db() as db:
            stmt = select(CompanyProfile).where(CompanyProfile.company_id == "DEFAULT")
            profile = db.execute(stmt).scalars().first()
            if profile:
                profile.company_logo = None
                profile.logo_filename = None
                profile.logo_content_type = None
                profile.updated_at = datetime.utcnow()
                db.commit()
                return True
        return False
    except Exception as e:
        st.error(f"Error removing logo: {str(e)}")
        return False


def validate_logo(uploaded_file) -> tuple:
    """
    Validate uploaded logo file

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not uploaded_file:
        return False, "No file uploaded"

    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_LOGO_SIZE_MB:
        return False, f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({MAX_LOGO_SIZE_MB} MB)"

    # Check file type by MIME type
    if uploaded_file.type not in ALLOWED_LOGO_TYPES:
        return False, f"File type '{uploaded_file.type}' not allowed. Use PNG or JPG images only."

    # Check file extension
    file_ext = Path(uploaded_file.name).suffix.lower()
    if file_ext not in ALLOWED_LOGO_EXTENSIONS:
        return False, f"File extension '{file_ext}' not allowed. Use .png, .jpg, or .jpeg files only."

    return True, ""


def display_logo_preview(logo_data: bytes, content_type: str, size: str = "medium"):
    """
    Display logo image preview

    Args:
        logo_data: Binary image data
        content_type: MIME type of the image
        size: Size preset ("small", "medium", "large")
    """
    if not logo_data:
        return

    # Encode to base64 for HTML display
    b64_logo = base64.b64encode(logo_data).decode()

    # Size presets
    sizes = {
        "small": "80px",
        "medium": "150px",
        "large": "250px"
    }
    max_height = sizes.get(size, "150px")

    st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; border: 2px dashed #ddd;">
            <img src="data:{content_type};base64,{b64_logo}"
                 style="max-height: {max_height}; max-width: 100%; object-fit: contain; border-radius: 8px;"
                 alt="Company Logo">
        </div>
    """, unsafe_allow_html=True)


def render_company_profile_tab(profile_data: dict):
    """Render the Company Profile tab"""

    st.markdown("### Company Profile")
    st.markdown("Configure your organization's basic information and contact details.")

    with st.form("company_profile_form"):
        st.markdown("#### 🏢 Organization Details")

        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input(
                "Company Name *",
                value=profile_data.get('company_name', ''),
                placeholder="Enter company name",
                help="Your organization's official name"
            )

            tagline = st.text_input(
                "Tagline",
                value=profile_data.get('tagline', ''),
                placeholder="Excellence in Solar PV Testing",
                help="A short memorable phrase for your organization"
            )

        with col2:
            description = st.text_area(
                "Company Description",
                value=profile_data.get('description', ''),
                placeholder="Brief description of your organization...",
                height=100,
                help="A brief description of your organization and services"
            )

        st.divider()
        st.markdown("#### 📞 Contact Information")

        col1, col2, col3 = st.columns(3)

        with col1:
            email = st.text_input(
                "Email *",
                value=profile_data.get('email', ''),
                placeholder="contact@company.com",
                help="Primary contact email"
            )

        with col2:
            phone = st.text_input(
                "Phone",
                value=profile_data.get('phone', ''),
                placeholder="+1 (555) 123-4567",
                help="Primary contact phone number"
            )

        with col3:
            website = st.text_input(
                "Website",
                value=profile_data.get('website', ''),
                placeholder="https://www.company.com",
                help="Company website URL"
            )

        # Form submission
        submitted = st.form_submit_button("💾 Save Company Profile", width="stretch", type="primary")

        if submitted:
            # Validation
            errors = []
            if not company_name or len(company_name.strip()) < 2:
                errors.append("Company name is required (minimum 2 characters)")
            if not email or '@' not in email:
                errors.append("Valid email address is required")
            if website and not (website.startswith('http://') or website.startswith('https://')):
                errors.append("Website URL must start with http:// or https://")

            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Save profile
                updated_data = {
                    'company_name': company_name.strip(),
                    'tagline': tagline.strip() if tagline else None,
                    'description': description.strip() if description else None,
                    'email': email.strip(),
                    'phone': phone.strip() if phone else None,
                    'website': website.strip() if website else None
                }

                if save_company_profile(updated_data):
                    st.success("✅ Company profile saved successfully!")
                    st.cache_data.clear()
                    clear_company_branding_cache()
                    st.rerun()


def render_address_tab(profile_data: dict):
    """Render the Address Details tab"""

    st.markdown("### Address Details")
    st.markdown("Configure your organization's physical location.")

    with st.form("address_form"):
        st.markdown("#### 📍 Location Information")

        address = st.text_area(
            "Street Address",
            value=profile_data.get('address', ''),
            placeholder="123 Solar Panel Drive\nSuite 100",
            height=80,
            help="Street address including suite/unit number"
        )

        col1, col2 = st.columns(2)

        with col1:
            city = st.text_input(
                "City *",
                value=profile_data.get('city', ''),
                placeholder="San Francisco",
                help="City name"
            )

            # Get current country for state filtering
            current_country = profile_data.get('country', 'United States')

            # State selection
            current_state = profile_data.get('state', '')
            if current_country == "United States":
                state_index = US_STATES.index(current_state) if current_state in US_STATES else len(US_STATES) - 1
                state = st.selectbox(
                    "State/Province *",
                    options=US_STATES,
                    index=state_index,
                    help="Select state or province"
                )
            else:
                state = st.text_input(
                    "State/Province *",
                    value=current_state,
                    placeholder="Province or State",
                    help="Enter state or province name"
                )

        with col2:
            zip_code = st.text_input(
                "ZIP/Postal Code *",
                value=profile_data.get('zip_code', ''),
                placeholder="94105",
                help="ZIP or postal code"
            )

            # Country selection
            current_country_index = COUNTRIES.index(current_country) if current_country in COUNTRIES else 0
            country = st.selectbox(
                "Country *",
                options=COUNTRIES,
                index=current_country_index,
                help="Select country"
            )

        # Map placeholder (optional feature)
        st.markdown("---")
        st.info("💡 **Tip:** After saving, your address can be used in reports and certificates.")

        # Form submission
        submitted = st.form_submit_button("💾 Save Address", width="stretch", type="primary")

        if submitted:
            # Validation
            errors = []
            if not city or len(city.strip()) < 2:
                errors.append("City is required")
            if not state or len(str(state).strip()) < 2:
                errors.append("State/Province is required")
            if not zip_code:
                errors.append("ZIP/Postal code is required")
            if not country:
                errors.append("Country is required")

            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Save address
                updated_data = {
                    'address': address.strip() if address else None,
                    'city': city.strip(),
                    'state': state if isinstance(state, str) else str(state),
                    'zip_code': zip_code.strip(),
                    'country': country
                }

                if save_company_profile(updated_data):
                    st.success("✅ Address saved successfully!")
                    st.cache_data.clear()
                    clear_company_branding_cache()
                    st.rerun()


def render_accreditation_tab(profile_data: dict):
    """Render the Accreditation & Details tab"""

    st.markdown("### Accreditation & Company Details")
    st.markdown("Configure your organization's industry classification and certifications.")

    with st.form("accreditation_form"):
        st.markdown("#### 🏭 Industry Classification")

        col1, col2 = st.columns(2)

        with col1:
            # Industry type selection
            current_industry = profile_data.get('industry_type', IndustryType.SOLAR_PV_TESTING)
            industry_options = list(INDUSTRY_TYPE_DISPLAY.values())
            industry_keys = list(INDUSTRY_TYPE_DISPLAY.keys())

            current_index = 0
            for i, key in enumerate(industry_keys):
                if key == current_industry:
                    current_index = i
                    break

            industry_display = st.selectbox(
                "Industry Type *",
                options=industry_options,
                index=current_index,
                help="Select your organization's primary industry"
            )

            # Map back to enum
            selected_industry = industry_keys[industry_options.index(industry_display)]

            # Established date
            established = profile_data.get('established_date')
            established_date = st.date_input(
                "Established Date",
                value=established if established else None,
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                help="When was your organization established?"
            )

        with col2:
            employees = st.slider(
                "Number of Employees",
                min_value=1,
                max_value=10000,
                value=profile_data.get('employees_count', 1),
                help="Approximate number of employees"
            )

            tax_id = st.text_input(
                "Tax ID / EIN",
                value=profile_data.get('tax_id', ''),
                placeholder="XX-XXXXXXX",
                help="Federal tax identification number"
            )

            registration_id = st.text_input(
                "Business Registration ID",
                value=profile_data.get('registration_id', ''),
                placeholder="Business registration number",
                help="State or local business registration number"
            )

        st.divider()
        st.markdown("#### 📜 Accreditation & Certifications")
        st.markdown("Select the accreditations and certifications your organization holds:")

        # Get current accreditation details
        current_accreditations = profile_data.get('accreditation_details', {})

        # Create checkboxes in columns
        col1, col2 = st.columns(2)

        accreditation_values = {}

        for i, (key, info) in enumerate(ACCREDITATION_STANDARDS.items()):
            with col1 if i % 2 == 0 else col2:
                is_checked = current_accreditations.get(key, False)
                accreditation_values[key] = st.checkbox(
                    f"**{info['name']}**",
                    value=is_checked,
                    help=info['description'],
                    key=f"accred_{key}"
                )

        st.divider()

        accreditation_notes = st.text_area(
            "Additional Accreditation Notes",
            value=profile_data.get('accreditation_notes', ''),
            placeholder="Enter any additional accreditation details, certificate numbers, expiry dates, etc.",
            height=100,
            help="Additional notes about your accreditations"
        )

        # Form submission
        submitted = st.form_submit_button("💾 Save Accreditation Details", width="stretch", type="primary")

        if submitted:
            # Save accreditation details
            updated_data = {
                'industry_type': selected_industry,
                'established_date': established_date,
                'employees_count': employees,
                'tax_id': tax_id.strip() if tax_id else None,
                'registration_id': registration_id.strip() if registration_id else None,
                'accreditation_details': accreditation_values,
                'accreditation_notes': accreditation_notes.strip() if accreditation_notes else None
            }

            if save_company_profile(updated_data):
                st.success("✅ Accreditation details saved successfully!")
                st.cache_data.clear()
                clear_company_branding_cache()
                st.rerun()


def render_logo_management_tab(profile_data: dict):
    """Render the Logo Management tab"""

    st.markdown("### Logo Management")
    st.markdown("Upload and manage your organization's logo for reports and branding.")

    # Current logo display
    st.markdown("#### 🖼️ Current Logo")

    current_logo = profile_data.get('company_logo')
    current_filename = profile_data.get('logo_filename')
    current_content_type = profile_data.get('logo_content_type', 'image/png')

    if current_logo:
        col1, col2 = st.columns([2, 1])

        with col1:
            display_logo_preview(current_logo, current_content_type, size="large")

        with col2:
            st.markdown("**Logo Information:**")
            st.markdown(f"- **Filename:** {current_filename or 'Unknown'}")
            st.markdown(f"- **Type:** {current_content_type}")
            st.markdown(f"- **Size:** {len(current_logo) / 1024:.1f} KB")

            st.markdown("---")

            # Remove logo button
            if st.button("🗑️ Remove Logo", width="stretch", type="secondary"):
                if clear_company_logo():
                    st.success("✅ Logo removed successfully!")
                    st.cache_data.clear()
                    clear_company_branding_cache()
                    st.rerun()
    else:
        st.info("📷 No logo uploaded yet. Upload your company logo below.")

    st.divider()

    # Logo upload section
    st.markdown("#### 📤 Upload New Logo")

    st.markdown("""
    **Logo Requirements:**
    - **Format:** PNG or JPG/JPEG
    - **Maximum Size:** 5 MB
    - **Recommended Dimensions:** 400x400 pixels (square) or 800x200 pixels (horizontal)
    - **Background:** Transparent PNG recommended for best results
    """)

    uploaded_file = st.file_uploader(
        "Choose a logo file",
        type=["png", "jpg", "jpeg"],
        help="Upload PNG or JPG image (max 5MB)",
        key="logo_uploader"
    )

    if uploaded_file:
        # Validate the file
        is_valid, error_msg = validate_logo(uploaded_file)

        if not is_valid:
            st.error(f"❌ {error_msg}")
        else:
            st.success("✅ File validated successfully!")

            # Preview
            st.markdown("**Preview:**")
            col1, col2 = st.columns([2, 1])

            with col1:
                st.image(uploaded_file, width="stretch")

            with col2:
                st.markdown(f"**Filename:** {uploaded_file.name}")
                st.markdown(f"**Type:** {uploaded_file.type}")
                st.markdown(f"**Size:** {uploaded_file.size / 1024:.1f} KB")

            # Save button
            if st.button("💾 Save Logo", width="stretch", type="primary"):
                # Read file data
                logo_bytes = uploaded_file.read()

                logo_data = {
                    'data': logo_bytes,
                    'filename': uploaded_file.name,
                    'content_type': uploaded_file.type
                }

                if save_company_profile({}, logo_data=logo_data):
                    st.success("✅ Logo uploaded successfully!")
                    st.cache_data.clear()
                    clear_company_branding_cache()
                    st.rerun()


def render_profile_summary(profile_data: dict):
    """Render a summary card of the company profile"""

    st.markdown("### 📊 Profile Summary")

    col1, col2, col3 = st.columns([1, 2, 2])

    with col1:
        # Logo preview (small)
        current_logo = profile_data.get('company_logo')
        if current_logo:
            content_type = profile_data.get('logo_content_type', 'image/png')
            display_logo_preview(current_logo, content_type, size="small")
        else:
            st.markdown("""
                <div style="text-align: center; padding: 1rem; background: #f0f0f0; border-radius: 10px;">
                    <span style="font-size: 3rem;">🏢</span>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"**{profile_data.get('company_name', 'Not Set')}**")
        if profile_data.get('tagline'):
            st.markdown(f"*{profile_data.get('tagline')}*")

        st.markdown(f"📧 {profile_data.get('email', 'Not set')}")
        if profile_data.get('phone'):
            st.markdown(f"📞 {profile_data.get('phone')}")
        if profile_data.get('website'):
            st.markdown(f"🌐 {profile_data.get('website')}")

    with col3:
        # Address
        city = profile_data.get('city')
        state = profile_data.get('state')
        country = profile_data.get('country')

        if city or state or country:
            location_parts = [p for p in [city, state, country] if p]
            st.markdown(f"📍 {', '.join(location_parts)}")

        # Industry
        industry = profile_data.get('industry_type')
        if industry:
            industry_display = INDUSTRY_TYPE_DISPLAY.get(industry, 'Unknown')
            st.markdown(f"🏭 {industry_display}")

        # Accreditations count
        accreditations = profile_data.get('accreditation_details', {})
        active_count = sum(1 for v in accreditations.values() if v)
        if active_count > 0:
            st.markdown(f"📜 {active_count} Active Certification(s)")


def main():
    """Main company settings page"""

    # Render navigation
    render_header("Company Settings", "Configure your organization profile and branding")
    render_sidebar_navigation()

    # Load company profile
    profile_data = get_company_profile()

    if profile_data is None:
        st.error("Unable to load company profile. Please check database connection.")
        return

    # Profile summary at the top
    render_profile_summary(profile_data)

    st.divider()

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏢 Company Profile",
        "📍 Address Details",
        "📜 Accreditation & Details",
        "🖼️ Logo Management"
    ])

    with tab1:
        render_company_profile_tab(profile_data)

    with tab2:
        render_address_tab(profile_data)

    with tab3:
        render_accreditation_tab(profile_data)

    with tab4:
        render_logo_management_tab(profile_data)

    # Footer with last updated info
    st.markdown("---")
    updated_at = profile_data.get('updated_at')
    if updated_at:
        st.caption(f"Last updated: {updated_at.strftime('%B %d, %Y at %I:%M %p')}")


if __name__ == "__main__":
    main()
else:
    main()
