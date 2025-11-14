"""Constants and enumerations for test protocols."""

from enum import Enum


class ProtocolCategory(str, Enum):
    """Protocol category enumeration."""

    ENVIRONMENTAL = "Environmental"
    MECHANICAL = "Mechanical"
    ELECTRICAL = "Electrical"
    THERMAL = "Thermal"
    DURABILITY = "Durability"
    PERFORMANCE = "Performance"


class TestStatus(str, Enum):
    """Test run status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class QCStatus(str, Enum):
    """Quality control status enumeration."""

    PENDING = "pending"
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


class ReportFormat(str, Enum):
    """Report format enumeration."""

    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"
    HTML = "html"


class CorrosionRating(str, Enum):
    """IEC 61701 Corrosion severity ratings."""

    RATING_0 = "0 - No corrosion"
    RATING_1 = "1 - Slight corrosion, <1% of area"
    RATING_2 = "2 - Light corrosion, 1-5% of area"
    RATING_3 = "3 - Moderate corrosion, 5-25% of area"
    RATING_4 = "4 - Heavy corrosion, 25-50% of area"
    RATING_5 = "5 - Severe corrosion, >50% of area"


# IEC 61701 Standard Constants
IEC_61701_SALT_CONCENTRATION_MIN = 4.5  # % NaCl
IEC_61701_SALT_CONCENTRATION_MAX = 5.5  # % NaCl
IEC_61701_SALT_CONCENTRATION_DEFAULT = 5.0  # % NaCl

IEC_61701_TEMP_MIN = 34.0  # °C
IEC_61701_TEMP_MAX = 36.0  # °C
IEC_61701_TEMP_DEFAULT = 35.0  # °C

IEC_61701_HUMIDITY_MIN = 93.0  # % RH
IEC_61701_HUMIDITY_MAX = 97.0  # % RH
IEC_61701_HUMIDITY_DEFAULT = 95.0  # % RH

# IEC 61701 Severity levels (hours of exposure)
IEC_61701_SEVERITY_LEVEL_1 = 60  # hours
IEC_61701_SEVERITY_LEVEL_2 = 120  # hours
IEC_61701_SEVERITY_LEVEL_3 = 240  # hours
IEC_61701_SEVERITY_LEVEL_4 = 480  # hours
IEC_61701_SEVERITY_LEVEL_5 = 840  # hours

# Test cycle parameters
SALT_MIST_CYCLE_SPRAY_DURATION = 2.0  # hours
SALT_MIST_CYCLE_DRY_DURATION = 22.0  # hours
SALT_MIST_TOTAL_CYCLE_DURATION = 24.0  # hours

# I-V measurement tolerances
IV_MEASUREMENT_TOLERANCE = 0.02  # 2%
MAX_DEGRADATION_THRESHOLD = 0.05  # 5% power loss threshold
