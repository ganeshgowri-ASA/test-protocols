# Report Generation Module

## Overview

The Report Generation module provides comprehensive functionality for creating professional test reports with custom templates, digital signatures, and multi-language support.

## Features

### 1. Auto PDF Report Generation
- Generate test reports from test result data
- Professional formatting with company branding (via ReportLab)
- Include charts, tables, and images
- Multi-page report support with headers/footers
- Excel export option for data analysis

### 2. Custom Report Templates
- Pre-built templates:
  - IEC 61215 Test Report
  - IEC 61730 Safety Report
  - NABL Format Report
- Create, edit, duplicate, and delete templates
- Version control for templates
- Configurable sections (header, body, footer)
- Custom branding (logo, colors)

### 3. Digital Signatures
- Add digital signature placeholders to reports
- Role-based signature workflows (Technician → Reviewer → Approver)
- Signature timestamp tracking
- Status tracking (Pending, Signed, Distributed)

### 4. Multi-Language Support
- Generate reports in multiple languages:
  - English
  - Hindi
  - Spanish
- Language-specific formatting support

### 5. Scheduled Report Generation
- Schedule daily/weekly/monthly reports
- Automated report triggers (on test completion)
- Email distribution lists
- Track last run and next run times
- Enable/disable schedules

### 6. Report History & Management
- Searchable report history
- Filter by status, language, date
- Download generated reports
- Resend email functionality
- Complete audit trail

## Database Models

### ReportTemplate
Stores custom report templates with configurable structure.

**Key Fields:**
- `template_id`: Unique identifier
- `template_name`: Display name
- `template_type`: IEC 61215, IEC 61730, NABL, Custom
- `version`: Template version number
- `header_content`: JSON configuration for header
- `body_sections`: Array of section definitions
- `footer_content`: JSON configuration for footer
- `is_active`: Template availability status

### GeneratedReport
Tracks all generated reports with metadata.

**Key Fields:**
- `report_id`: Unique identifier
- `report_number`: Sequential report number (TEST-RPT-00001)
- `template_id`: Reference to template used
- `sample_ids`: Array of sample IDs included
- `test_ids`: Array of test IDs included
- `file_path`: Storage location of generated file
- `file_size`: File size in bytes
- `language`: Report language
- `status`: Draft, Generated, Signed, Distributed
- `signatures`: JSON array of signature records
- `distributed_to`: Email addresses list
- `generated_by`: User who generated the report

### ScheduledReport
Manages automated report generation schedules.

**Key Fields:**
- `schedule_id`: Unique identifier
- `schedule_name`: Display name
- `template_id`: Template to use
- `frequency`: Daily, Weekly, Monthly, On Test Completion
- `trigger_time`: HH:MM format for scheduled execution
- `filters`: JSON filters for data selection
- `recipients`: Email distribution list
- `is_active`: Schedule active status
- `last_run`: Last execution timestamp
- `next_run`: Next scheduled execution
- `last_status`: Success/Failed status

## Usage

### Generating a Report

1. Navigate to **Report Generation** page
2. Select **Generate Report** tab
3. Choose a template from dropdown
4. Select report language
5. Select samples and tests to include
6. Configure report options:
   - Include charts
   - Include raw data
   - Include photos
   - Add digital signature
7. Choose output format (PDF, Excel, or Both)
8. Click **Preview Report** to review or **Generate PDF** to create

### Managing Templates

1. Go to **Templates** tab
2. View existing templates in expandable cards
3. Actions available:
   - **Edit**: Modify template settings
   - **Duplicate**: Create a copy for customization
   - **Delete**: Remove unused templates
4. Click **Create New Template** to add a custom template

### Scheduling Reports

1. Navigate to **Scheduled** tab
2. Click **Create New Schedule**
3. Configure:
   - Schedule name
   - Frequency (Daily, Weekly, Monthly)
   - Template to use
   - Trigger time
   - Email recipients
4. Toggle **Active** to enable/disable schedule
5. View last run and next run timestamps

### Viewing Report History

1. Go to **History** tab
2. Use filters:
   - Status (All, Draft, Generated, Signed, Distributed)
   - Language
   - Search by report number or title
3. Expand report cards to view details
4. Download reports using the download button
5. Resend reports via email if needed

## Technical Details

### PDF Generation
Uses the existing `components/report_generator.py` module which provides:
- **PDFReportGenerator**: Professional PDF generation using ReportLab
- **FPDFReportGenerator**: Alternative PDF generator using FPDF2
- **ExcelReportGenerator**: Excel export with multiple sheets

### File Storage
Generated reports are stored in `/reports` directory with naming:
- PDF: `{report_id}.pdf`
- Excel: `{report_id}.xlsx`

### Integration Points
- **Sample Management**: Links to samples for data
- **Test Execution**: Retrieves test results
- **Company Profile**: Uses branding information
- **User Management**: Tracks who generated reports

## API Reference

### Creating Default Templates
```python
from database import get_db, ReportTemplate

with get_db() as db:
    _create_default_templates(db)
```

### Generating a Report Programmatically
```python
from components.report_generator import PDFReportGenerator

generator = PDFReportGenerator()
test_data = {
    'title': 'Test Report',
    'protocol_id': 'P1-IV-001',
    'sample_id': 'MOD-2024-001',
    # ... more fields
}
results_data = [
    {'parameter': 'Pmax', 'value': 405.2, 'unit': 'W', 'status': 'PASS'},
    # ... more results
]

pdf_bytes = generator.generate_test_report(test_data, results_data)
```

## Security Considerations

1. **File Access**: Reports are stored in the file system with paths tracked in database
2. **User Permissions**: Only authenticated users can generate reports
3. **Digital Signatures**: Placeholder support for future PKI integration
4. **Email Distribution**: Secure email configuration required for scheduled reports

## Future Enhancements

1. **Email Integration**: Implement actual email sending for distribution
2. **Template Editor**: Visual drag-and-drop template designer
3. **Advanced Signatures**: PKI-based digital signature integration
4. **Batch Processing**: Parallel report generation for multiple samples
5. **Report Analytics**: Dashboard for report generation metrics
6. **Custom Branding**: Per-customer branding support
7. **API Endpoints**: RESTful API for external report generation

## Troubleshooting

### Reports Directory Not Found
```bash
mkdir -p /path/to/project/reports
```

### ReportLab Not Installed
```bash
pip install reportlab Pillow
```

### Database Tables Not Created
```bash
python run_migrations.py
```

### Permission Issues
Ensure the web server has write permissions to the `/reports` directory.

## Dependencies

- `reportlab>=4.2.5` - Professional PDF generation
- `fpdf2>=2.7.6` - Alternative PDF generation
- `Pillow>=11.0.0` - Image processing
- `openpyxl>=3.1.2` - Excel export
- `SQLAlchemy>=2.0.36` - Database ORM

## License

Part of the Solar PV Testing LIMS-QMS System.
