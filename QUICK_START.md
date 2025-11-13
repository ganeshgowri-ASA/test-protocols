# Quick Start Guide - IAM-001 Implementation

## Executive Summary

The `test-protocols` repository is a brand-new **Modular PV Testing Protocol Framework** using JSON-based protocol definitions with Streamlit/GenSpark UI, automated analysis, QC, and report generation.

**Current State**: Initial commit only (README, LICENSE, .gitignore)  
**Current Branch**: `claude/iam-001-incidence-angle-modifier-011CV5qwu5rkit15bYd6PN2X`  
**Framework Version**: 1.0 (to be implemented)

---

## What Exists Now

- Project boilerplate (.gitignore for Python projects)
- License file
- README describing the framework concept
- Two parallel branches for future development

---

## What Needs to Be Created

See the following documentation files in this repository:

1. **REPOSITORY_STRUCTURE.md** - Complete directory structure and organization
2. **IMPLEMENTATION_CHECKLIST.md** - Detailed task breakdown by phase
3. **ARCHITECTURE_PATTERNS.md** - Design patterns, tech stack, and code examples

---

## Quick Implementation Path (30,000 ft view)

### Phase 1: Foundation (Week 1)
```
1. Create project configuration files
   - pyproject.toml, setup.py, main.py
   - config/ directory with YAML configs
   - requirements/ with dependencies

2. Set up directory structure
   - src/ (with submodules)
   - tests/ (with fixtures)
   - docs/, protocols/
```

### Phase 2: Protocol Definition (Week 1-2)
```
1. Create IAM-001 protocol files
   - protocols/iam-001/schema.json
   - protocols/iam-001/template.json
   - protocols/iam-001/config.json

2. Define protocol structure
   - Input parameters (angle range, intervals, etc.)
   - Data fields (timestamp, angle, measurement)
   - QC rules and thresholds
```

### Phase 3: Core Engine (Week 2-3)
```
1. Protocol execution engine
   - Loader: Read JSON definitions
   - Validator: Check data compliance
   - Executor: Run protocol steps

2. Analysis module
   - IAM-specific calculations
   - Statistical analysis
   - Chart generation

3. Database models
   - ProtocolRun, MeasurementData, AnalysisResult, etc.
   - SQLAlchemy ORM setup
```

### Phase 4: UI & Tests (Week 3-4)
```
1. GenSpark/Streamlit pages
   - Protocol setup
   - Data entry
   - Analysis view
   - QC review
   - Report generation

2. Comprehensive testing
   - Unit tests for protocol engine
   - Integration tests for workflows
   - E2E tests for UI
```

### Phase 5: Polish & Docs (Week 4)
```
1. Report generation
2. QC module
3. Documentation
4. Docker setup
```

---

## Directory Structure Overview

```
test-protocols/
├── protocols/                 # Protocol JSON definitions
│   └── iam-001/              # IAM-001 protocol files
├── src/                      # Main source code
│   ├── genspark/             # UI components
│   ├── protocols/            # Protocol engine
│   ├── analysis/             # Data analysis
│   ├── qc/                   # Quality control
│   ├── database/             # Data models
│   └── common/               # Shared utilities
├── tests/                    # Test suites
├── docs/                     # Documentation
├── config/                   # Configuration files
├── requirements/             # Python dependencies
└── [config files]            # setup.py, pytest.ini, etc.
```

---

## Key Technology Stack

**Backend**: Python 3.8+  
**Framework**: Streamlit or FastAPI (for REST APIs)  
**Database**: SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod)  
**Testing**: pytest with fixtures  
**Data**: pandas, numpy, scipy  
**Visualization**: plotly, matplotlib  
**Reporting**: Jinja2, reportlab, openpyxl  

---

## Critical Files to Create First

### High Priority (Must have for MVP)
1. `protocols/iam-001/schema.json` - Protocol structure
2. `src/protocols/engine.py` - Core execution engine
3. `src/protocols/loader.py` - Load protocol definitions
4. `src/analysis/iam_analyzer.py` - IAM calculations
5. `src/database/models.py` - Database schema
6. `tests/unit/test_protocol_loader.py` - Basic tests
7. `main.py` - Entry point

### Medium Priority (Should have)
1. `src/genspark/app.py` - Main UI application
2. `src/qc/validator.py` - Quality control rules
3. `src/reporting/generator.py` - Report generation
4. Documentation files
5. Configuration files

### Low Priority (Nice to have)
1. LIMS/QMS integrations
2. Advanced visualization
3. Docker setup
4. GitHub workflows

---

## Next Steps

1. Read **REPOSITORY_STRUCTURE.md** for full directory layout
2. Read **IMPLEMENTATION_CHECKLIST.md** for task breakdown
3. Read **ARCHITECTURE_PATTERNS.md** for code patterns and examples
4. Start with Phase 1: Create project configuration files
5. Move to Phase 2: Define IAM-001 protocol in JSON
6. Build the core engine components
7. Write tests alongside implementation
8. Build UI components last

---

## Important Notes

### IAM-001 Protocol Context
- **IAM** = Incidence Angle Modifier
- Measures how photovoltaic performance varies with sun angle
- Parameters: angle (0-90°), measurements at intervals, temperature compensation
- Outputs: IAM curves, modifier factors, performance metrics

### Protocol as Code
- Protocols are defined in JSON (not Python code)
- This allows non-programmers to create new protocols
- Schema validation ensures data integrity
- Templates provide defaults for common scenarios

### Multi-Protocol Support
- Framework is designed for multiple protocols
- IAM-001 is the first implementation
- Future protocols follow the same pattern
- Shared engine handles all protocols

### Integration Focus
- LIMS integration for sample tracking
- QMS integration for quality documentation
- Project management system integration
- Audit trail for compliance

---

## File Reference

### Documentation in This Repository
- **REPOSITORY_STRUCTURE.md** (26 KB)
  - Complete directory tree
  - File descriptions
  - Module responsibilities

- **IMPLEMENTATION_CHECKLIST.md** (15 KB)
  - Phased implementation plan
  - Task breakdown
  - Priority levels

- **ARCHITECTURE_PATTERNS.md** (18 KB)
  - Architecture patterns
  - Code examples
  - Tech stack details

### Getting Help

For specific questions:
1. Check ARCHITECTURE_PATTERNS.md for design patterns
2. Check IMPLEMENTATION_CHECKLIST.md for task status
3. Check REPOSITORY_STRUCTURE.md for file locations

---

## Summary

You're starting with a clean slate - which is good for implementing the framework correctly from the start. The three documentation files provide:

1. **What to build** (REPOSITORY_STRUCTURE.md)
2. **How to build it** (IMPLEMENTATION_CHECKLIST.md)
3. **How it should work** (ARCHITECTURE_PATTERNS.md)

Focus on the protocol definition first (JSON files), then build the engine around it. The modular design ensures that adding new protocols later is straightforward.

Good luck with the IAM-001 implementation!
