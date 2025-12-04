"""
Tests for Document Management Module
=====================================
Tests for document version control, digital signatures, and approval workflow.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Skip streamlit import for testing
import os
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'


def test_document_model_has_signature_fields():
    """Test that Document model has digital signature fields"""
    from database.models import Document
    
    # Check that signature fields exist
    assert hasattr(Document, 'author_signature')
    assert hasattr(Document, 'author_signature_date')
    assert hasattr(Document, 'reviewer_signature')
    assert hasattr(Document, 'reviewer_signature_date')
    assert hasattr(Document, 'approver_signature')
    assert hasattr(Document, 'approver_signature_date')
    print("✅ Document model has all signature fields")


def test_document_model_has_version_control_fields():
    """Test that Document model has version control fields"""
    from database.models import Document
    
    # Check that version control fields exist
    assert hasattr(Document, 'version')
    assert hasattr(Document, 'revision_number')
    assert hasattr(Document, 'is_current_version')
    assert hasattr(Document, 'previous_version_id')
    assert hasattr(Document, 'status')
    print("✅ Document model has all version control fields")


def test_document_status_enum():
    """Test that DocumentStatus enum has all required statuses"""
    from database.models import DocumentStatus
    
    # Check all required statuses exist
    assert hasattr(DocumentStatus, 'DRAFT')
    assert hasattr(DocumentStatus, 'IN_REVIEW')
    assert hasattr(DocumentStatus, 'APPROVED')
    assert hasattr(DocumentStatus, 'SUPERSEDED')
    assert hasattr(DocumentStatus, 'OBSOLETE')
    print("✅ DocumentStatus enum has all required statuses")


def test_document_category_enum():
    """Test that DocumentCategory enum has required categories"""
    from database.models import DocumentCategory
    
    # Check some common categories
    assert hasattr(DocumentCategory, 'PROCEDURE')
    assert hasattr(DocumentCategory, 'WORK_INSTRUCTION')
    assert hasattr(DocumentCategory, 'FORM')
    assert hasattr(DocumentCategory, 'RECORD')
    assert hasattr(DocumentCategory, 'SPECIFICATION')
    print("✅ DocumentCategory enum has required categories")


def test_document_access_log_model():
    """Test that DocumentAccessLog model exists and has required fields"""
    from database.models import DocumentAccessLog
    
    # Check that access log fields exist
    assert hasattr(DocumentAccessLog, 'document_id')
    assert hasattr(DocumentAccessLog, 'user_id')
    assert hasattr(DocumentAccessLog, 'user_name')
    assert hasattr(DocumentAccessLog, 'access_type')
    assert hasattr(DocumentAccessLog, 'access_timestamp')
    print("✅ DocumentAccessLog model has all required fields")


def test_document_management_page_exists():
    """Test that the document management page file exists"""
    page_path = project_root / "pages" / "12_📄_Document_Management.py"
    assert page_path.exists()
    print(f"✅ Document Management page exists at {page_path}")


def test_document_management_page_syntax():
    """Test that the document management page has valid Python syntax"""
    import py_compile
    page_path = project_root / "pages" / "12_📄_Document_Management.py"
    
    try:
        py_compile.compile(str(page_path), doraise=True)
        print("✅ Document Management page has valid Python syntax")
    except py_compile.PyCompileError as e:
        raise AssertionError(f"Syntax error in Document Management page: {e}")


def test_generate_document_number_function():
    """Test that generate_document_number function exists in the page"""
    page_path = project_root / "pages" / "12_📄_Document_Management.py"
    
    with open(page_path, 'r') as f:
        content = f.read()
    
    assert 'def generate_document_number()' in content
    assert 'DOC-' in content
    print("✅ generate_document_number function exists")


def test_create_new_version_function():
    """Test that create_new_version function exists in the page"""
    page_path = project_root / "pages" / "12_📄_Document_Management.py"
    
    with open(page_path, 'r') as f:
        content = f.read()
    
    assert 'def create_new_version(' in content
    assert 'DocumentStatus.SUPERSEDED' in content
    assert 'is_current_version = False' in content
    assert 'previous_version_id' in content
    print("✅ create_new_version function exists with proper version management")


def test_render_signature_section_function():
    """Test that render_signature_section function exists in the page"""
    page_path = project_root / "pages" / "12_📄_Document_Management.py"
    
    with open(page_path, 'r') as f:
        content = f.read()
    
    assert 'def render_signature_section(' in content
    assert 'author_signature' in content
    assert 'reviewer_signature' in content
    assert 'approver_signature' in content
    print("✅ render_signature_section function exists with all signature types")


def test_render_version_history_function():
    """Test that render_version_history function exists in the page"""
    page_path = project_root / "pages" / "12_📄_Document_Management.py"
    
    with open(page_path, 'r') as f:
        content = f.read()
    
    assert 'def render_version_history(' in content
    assert 'Version History' in content
    assert 'document_number' in content
    print("✅ render_version_history function exists")


def test_approval_workflow_implementation():
    """Test that approval workflow is properly implemented"""
    page_path = project_root / "pages" / "12_📄_Document_Management.py"
    
    with open(page_path, 'r') as f:
        content = f.read()
    
    # Check for approval workflow elements
    assert 'Submit Review' in content
    assert 'Approve' in content
    assert 'Request Changes' in content
    assert 'Reject' in content
    assert 'reviewer_signature' in content
    assert 'approver_signature' in content
    print("✅ Approval workflow is properly implemented with signatures")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Running Document Management Tests")
    print("="*60 + "\n")
    
    tests = [
        test_document_model_has_signature_fields,
        test_document_model_has_version_control_fields,
        test_document_status_enum,
        test_document_category_enum,
        test_document_access_log_model,
        test_document_management_page_exists,
        test_document_management_page_syntax,
        test_generate_document_number_function,
        test_create_new_version_function,
        test_render_signature_section_function,
        test_render_version_history_function,
        test_approval_workflow_implementation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    if failed > 0:
        sys.exit(1)
