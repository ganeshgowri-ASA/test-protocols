"""Database package initialization - direct imports from models module"""

# Direct imports from models - no caching needed
# All models have extend_existing=True in __table_args__ which prevents redefinition errors
from database.models import (
    # Core Models
    User,
    ServiceRequest,
    IncomingInspection,
    Equipment,
    EquipmentBooking,
    TestProtocol,
    TestExecution,
    TestData,
    AuditLog,
    QRCode,
    CompanyProfile,

    # Sample Management Models
    Sample,
    SampleReceipt,
    SampleStatusHistory,
    RouteCard,
    SampleTestAssignment,
    SampleInventory,
    SampleAllocation,

    # Training Models
    StaffTraining,
    StaffTrainingRecord,

    # Document Models
    Document,
    DocumentAccessLog,

    # BOM Models
    BOMItem,
    BOMProtocolRequirement,
    BOMUsageLog,

    # QR and Calibration Models
    QRScanLog,
    CalibrationRecord,

    # Enums
    UserRole,
    RequestStatus,
    TestStatus,
    EquipmentStatus,
    InspectionStatus,
    IndustryType,
    SampleStatus,
    DocumentCategory,
    TrainingStatus,
    BOMItemType,
    ReceiptStatus,
    InventoryStatus,
    DocumentStatus,
)

# Export all for easy access
__all__ = [
    # Core Models
    'User',
    'ServiceRequest',
    'IncomingInspection',
    'Equipment',
    'EquipmentBooking',
    'TestProtocol',
    'TestExecution',
    'TestData',
    'AuditLog',
    'QRCode',
    'CompanyProfile',

    # Sample Management Models
    'Sample',
    'SampleReceipt',
    'SampleStatusHistory',
    'RouteCard',
    'SampleTestAssignment',
    'SampleInventory',
        'SampleAllocation',

    # Training Models
    'StaffTraining',
    'StaffTrainingRecord',

    # Document Models
    'Document',
    'DocumentAccessLog',

    # BOM Models
    'BOMItem',
    'BOMProtocolRequirement',
    'BOMUsageLog',

    # QR and Calibration Models
    'QRScanLog',
    'CalibrationRecord',

    # Enums
    'UserRole',
    'RequestStatus',
    'TestStatus',
    'EquipmentStatus',
    'InspectionStatus',
    'IndustryType',
    'SampleStatus',
    'DocumentCategory',
    'TrainingStatus',
    'BOMItemType',
    'ReceiptStatus',
    'InventoryStatus',
    'DocumentStatus',
]
