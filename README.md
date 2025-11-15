# Audit Pro Enterprise

Enterprise Audit Management System - Comprehensive audit planning, execution, NC/OFI tracking, and corrective action management with full data traceability.

## Features

✓ **Entity Management** - Hierarchical organization structure (Company → Division → Plant → Department)
✓ **Audit Planning** - Program scheduling, auditor assignment, multi-standard support
✓ **Audit Execution** - Digital checklists, real-time findings capture, evidence attachment
✓ **NC/OFI Tracking** - Non-conformance and opportunity for improvement management
✓ **Corrective Actions** - CAR/8D methodology, root cause analysis, action tracking
✓ **Reports & Analytics** - Dashboard, trend analysis, compliance metrics, PDF export
✓ **Role-Based Access** - Admin, Auditor, Auditee, Viewer roles

## Installation

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/audit-pro-enterprise.git
cd audit-pro-enterprise

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

## Default Login

- **Username**: admin
- **Password**: admin123

## Technology Stack

- **Frontend**: Streamlit
- **Database**: SQLite (SQLAlchemy ORM)
- **Analytics**: Plotly, Pandas
- **Reports**: ReportLab, openpyxl
- **Authentication**: bcrypt

## Session Identifier

SESSION-APE-001: Initial Audit Pro Enterprise implementation

## Architecture

- **Modular Design**: Separation of models, pages, components, and utilities
- **QA-Testable**: Comprehensive test coverage
- **Data Traceability**: Full audit trail for all operations
- **Scalable**: SQLAlchemy ORM supports PostgreSQL migration

## License

MIT License
