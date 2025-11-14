# FIRE-001 Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python -c "from src.db.models import DatabaseManager; db = DatabaseManager(); db.create_all_tables()"
```

### 3. Launch Web Interface
```bash
streamlit run src/ui/fire_resistance_ui.py
```

### 4. Access Application
Open browser to: **http://localhost:8501**

## Quick Test (Python)

```python
from src.handlers.fire_resistance_handler import FireResistanceProtocolHandler
from src.models.fire_resistance_model import *

# Initialize
handler = FireResistanceProtocolHandler()

# Create sample
sample = SampleInformation(
    sample_id="QUICK-001",
    manufacturer="Test Co",
    model_number="TC-100",
    serial_number="SN001"
)

# Create test
test = handler.create_test_session(sample, ["Tester A"])

# Record measurement
handler.record_measurement(30.0, 150.5, 25.0)

# Finalize
obs = TestObservations(max_flame_spread_mm=75.0)
results = handler.finalize_test(obs)

print(f"Result: {results.overall_result.value}")
```

## Common Commands

### Run Tests
```bash
pytest tests/ -v
```

### Generate Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html
```

### Check Code Style
```bash
flake8 src/
black src/ --check
```

## Directory Structure
```
protocols/FIRE-001/json/    # Protocol definition
src/models/                 # Data models
src/handlers/               # Test execution
src/ui/                     # Web interface
src/db/                     # Database
tests/                      # Test suite
docs/                       # Documentation
```

## Key Files

- **Protocol**: `protocols/FIRE-001/json/fire_resistance_protocol.json`
- **Models**: `src/models/fire_resistance_model.py`
- **Handler**: `src/handlers/fire_resistance_handler.py`
- **UI**: `src/ui/fire_resistance_ui.py`
- **Database**: `src/db/models.py`
- **Schema**: `src/db/schema.sql`
- **User Guide**: `docs/protocols/FIRE-001_USER_GUIDE.md`

## Need Help?

- 📖 Read: `docs/protocols/FIRE-001_USER_GUIDE.md`
- 💻 Example: `README_FIRE001.md` - API Examples section
- 🧪 Tests: Check `tests/` for usage examples
- 🐛 Issues: Create issue in repository

## Acceptance Criteria Quick Reference

✅ Self-extinguish ≤ 60 seconds
✅ Flame spread ≤ 100 mm
✅ No flaming drips

## Safety First!

- Fire-resistant PPE required
- 2+ personnel minimum
- Fire extinguisher ready
- Well-ventilated area

---
**Ready in 5 minutes!** 🚀
