"""Database package initialization with Streamlit caching to prevent model reimport"""
import streamlit as st

# Use Streamlit's resource caching to import models only once
@st.cache_resource
def get_models():
    """Import and cache database models to prevent table redefinition errors"""
    from database import models
    return models

# Import models through cache
_cached_models = get_models()

# Re-export all model classes
User = _cached_models.User
ServiceRequest = _cached_models.ServiceRequest
IncomingInspection = _cached_models.IncomingInspection
Equipment = _cached_models.Equipment
EquipmentBooking = _cached_models.EquipmentBooking
TestProtocol = _cached_models.TestProtocol
TestExecution = _cached_models.TestExecution
TestData = _cached_models.TestData
AuditLog = _cached_models.AuditLog
QRCode = _cached_models.QRCode
CompanyProfile = _cached_models.CompanyProfile

# Sample Management Models
Sample = _cached_models.Sample
SampleReceipt = _cached_models.SampleReceipt
SampleStatusHistory = _cached_models.SampleStatusHistory
RouteCard = _cached_models.RouteCard
SampleTestAssignment = _cached_models.SampleTestAssignment
SampleInventory = _cached_models.SampleInventory
StorageLocation = _cached_models.StorageLocation

# Training Models
StaffTraining = _cached_models.StaffTraining
StaffTrainingRecord = _cached_models.StaffTrainingRecord

# Document Models
Document = _cached_models.Document
DocumentAccessLog = _cached_models.DocumentAccessLog

# BOM Models
BOMItem = _cached_models.BOMItem
BOMProtocolRequirement = _cached_models.BOMProtocolRequirement
BOMUsageLog = _cached_models.BOMUsageLog

# QR and Calibration Models
QRScanLog = _cached_models.QRScanLog
CalibrationRecord = _cached_models.CalibrationRecord

# Export enums
UserRole = _cached_models.UserRole
RequestStatus = _cached_models.RequestStatus
TestStatus = _cached_models.TestStatus
EquipmentStatus = _cached_models.EquipmentStatus
InspectionStatus = _cached_models.InspectionStatus
IndustryType = _cached_models.IndustryType
SampleStatus = _cached_models.SampleStatus
DocumentCategory = _cached_models.DocumentCategory
TrainingStatus = _cached_models.TrainingStatus
BOMItemType = _cached_models.BOMItemType
ReceiptStatus = _cached_models.ReceiptStatus
InventoryStatus = _cached_models.InventoryStatus
DocumentStatus = _cached_models.DocumentStatus
