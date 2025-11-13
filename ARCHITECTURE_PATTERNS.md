# Key Patterns and Technology Stack

## Architecture Patterns

### 1. Protocol-Based Design
- **Pattern**: Each protocol is a self-contained JSON definition
- **Benefits**: Modularity, reusability, easy addition of new protocols
- **Files**: `protocols/{protocol-id}/schema.json`, `template.json`, `config.json`

### 2. Engine-Based Execution
- **Pattern**: Protocol engine loads and executes protocols
- **Components**:
  - Loader: Reads JSON definitions
  - Validator: Ensures data compliance
  - Executor: Runs protocol steps
- **Benefits**: Decoupling logic from UI

### 3. Layered Architecture
```
UI Layer (GenSpark/Streamlit)
    ↓
Business Logic Layer (Protocol Engine, Analysis, QC)
    ↓
Data Access Layer (Database Repository)
    ↓
Database Layer (SQLAlchemy ORM)
```

### 4. Integration Layer
- **Pattern**: Abstract client interfaces for LIMS, QMS, etc.
- **Benefits**: Easy switching between different systems

---

## Technology Stack Details

### Backend Framework
- **Primary**: Python 3.8+
- **Web Framework**: FastAPI (recommended for REST APIs)
- **ORM**: SQLAlchemy with Alembic migrations
- **Task Queue**: Celery (optional, for async operations)

### Frontend/UI
- **Framework**: Streamlit (for rapid development) or custom GenSpark
- **Alternatives**: 
  - Streamlit for data science/analysis focus
  - FastAPI + React for web app focus
  - Gradio for simple interfaces

### Data Processing
- **Data Manipulation**: pandas, numpy
- **Statistical Analysis**: scipy, statsmodels
- **Scientific Computing**: scikit-learn (if needed for ML)

### Visualization
- **Interactive Charts**: plotly, bokeh
- **Static Charts**: matplotlib, seaborn
- **3D Visualization**: mayavi (if needed)

### Reporting
- **HTML Generation**: Jinja2 templates
- **PDF Generation**: reportlab or wkhtmltopdf
- **Excel Generation**: openpyxl, xlsxwriter
- **Markdown**: python-markdown

### Testing
- **Unit Testing**: pytest with fixtures
- **Coverage**: pytest-cov
- **Mocking**: unittest.mock, pytest-mock
- **Integration Testing**: pytest with test database
- **E2E Testing**: Streamlit testing utilities or Playwright

### Database
- **Development**: SQLite
- **Production**: PostgreSQL
- **Migrations**: Alembic
- **Connection Pooling**: SQLAlchemy

### Code Quality
- **Linting**: flake8, pylint
- **Formatting**: black, isort
- **Type Checking**: mypy, pydantic
- **Pre-commit Hooks**: pre-commit framework
- **Documentation**: Sphinx or mkdocs

### Deployment
- **Containerization**: Docker
- **Orchestration**: Docker Compose (local), Kubernetes (cloud)
- **Web Server**: Gunicorn/uvicorn for FastAPI, streamlit run for Streamlit
- **Reverse Proxy**: Nginx

### DevOps
- **CI/CD**: GitHub Actions
- **Version Control**: Git
- **Package Management**: pip, poetry, or uv
- **Environment Management**: venv, conda

---

## Project Structure Patterns

### 1. Configuration Management
```python
# config/development.yaml
database:
  url: sqlite:///dev.db
  echo: true
logging:
  level: DEBUG
  format: detailed
```

### 2. Database Models Pattern
```python
# src/database/models.py
class ProtocolRun(Base):
    __tablename__ = "protocol_runs"
    
    id = Column(Integer, primary_key=True)
    protocol_id = Column(String, ForeignKey("protocols.id"))
    status = Column(Enum(ProtocolStatus))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    measurements = relationship("MeasurementData", back_populates="protocol_run")
```

### 3. Protocol Loader Pattern
```python
# src/protocols/loader.py
class ProtocolLoader:
    def load_schema(self, protocol_id: str) -> dict:
        path = f"protocols/{protocol_id}/schema.json"
        return json.load(open(path))
    
    def load_template(self, protocol_id: str) -> dict:
        path = f"protocols/{protocol_id}/template.json"
        return json.load(open(path))
```

### 4. Validator Pattern
```python
# src/protocols/validator.py
class ProtocolValidator:
    def __init__(self, schema: dict):
        self.schema = schema
    
    def validate(self, data: dict) -> ValidationResult:
        # Use jsonschema or pydantic
        pass
```

### 5. Analysis Pattern
```python
# src/analysis/iam_analyzer.py
class IAMAnalyzer:
    def analyze(self, data: pd.DataFrame) -> AnalysisResult:
        # IAM-specific calculations
        return AnalysisResult(
            iam_curve=self._calculate_iam_curve(data),
            modifier_factors=self._calculate_modifiers(data),
            metrics=self._calculate_metrics(data)
        )
```

### 6. Report Generation Pattern
```python
# src/reporting/generator.py
class ReportGenerator:
    def generate(self, result: AnalysisResult, format: str = "html"):
        template = self._load_template(format)
        return template.render(
            title=result.title,
            data=result.data,
            charts=result.charts
        )
```

### 7. GenSpark Page Pattern
```python
# src/genspark/pages/protocol_setup.py
import streamlit as st
from src.protocols.loader import ProtocolLoader

def show():
    st.title("Protocol Setup")
    
    loader = ProtocolLoader()
    protocols = loader.list_available_protocols()
    
    selected = st.selectbox("Select Protocol", protocols)
    schema = loader.load_schema(selected)
    
    # Render dynamic form from schema
```

---

## Testing Patterns

### 1. Fixture Pattern
```python
# tests/fixtures/sample_data.py
import pytest

@pytest.fixture
def sample_iam_measurements():
    return pd.DataFrame({
        'angle': [0, 10, 20, 30, 40, 50],
        'power': [1000, 980, 950, 890, 800, 650]
    })
```

### 2. Mock Integration Pattern
```python
# tests/fixtures/mock_integrations.py
from unittest.mock import Mock

@pytest.fixture
def mock_lims():
    lims = Mock()
    lims.submit_result = Mock(return_value={"status": "success"})
    return lims
```

### 3. Database Test Pattern
```python
# tests/conftest.py
@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()
```

### 4. API Test Pattern
```python
# tests/integration/test_api.py
from fastapi.testclient import TestClient

def test_protocol_endpoint(client: TestClient):
    response = client.get("/api/protocols/iam-001")
    assert response.status_code == 200
    assert response.json()["protocol_id"] == "iam-001"
```

---

## File Naming Conventions

### Python Files
- **Modules**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase`
- **Functions**: `lowercase_with_underscores()`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`

### Test Files
- **Unit tests**: `test_{module}_unit.py`
- **Integration tests**: `test_{module}_integration.py`
- **E2E tests**: `test_{feature}_e2e.py`

### Configuration Files
- **YAML**: `snake_case_config.yaml`
- **JSON**: `snake_case_config.json`
- **Environment**: `.env.{environment}`

### JSON Schema Files
- **Protocol**: `{protocol_id}/schema.json`
- **Template**: `{protocol_id}/template.json`
- **Config**: `{protocol_id}/config.json`

---

## Key Dependencies (Recommended)

### Core
```
streamlit>=1.28.0
fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
alembic>=1.12.0
pydantic>=2.0.0
```

### Data Processing
```
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.3.0
```

### Visualization
```
plotly>=5.17.0
matplotlib>=3.8.0
seaborn>=0.12.0
```

### Reporting
```
jinja2>=3.1.0
reportlab>=4.0.0
openpyxl>=3.1.0
wkhtmltopdf-wrapper>=1.0.0
```

### Testing
```
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
factory-boy>=3.3.0
```

### Development
```
black>=23.0.0
flake8>=6.1.0
isort>=5.12.0
mypy>=1.6.0
pre-commit>=3.5.0
```

---

## Best Practices

### 1. Protocol Development
- Keep protocols in JSON for language-agnostic use
- Version all protocols (major.minor.patch)
- Include comprehensive schema validation
- Document all parameters and expected values

### 2. Code Organization
- One class per module (with supporting functions)
- Keep modules under 500 lines
- Use type hints throughout
- Document complex algorithms

### 3. Testing
- Aim for 80%+ code coverage
- Test edge cases and error conditions
- Mock external dependencies
- Use fixtures for reusable test data

### 4. Database
- Always use migrations for schema changes
- Include proper indexes
- Use transactions for multi-step operations
- Implement soft deletes where appropriate

### 5. Error Handling
- Create custom exception classes
- Log errors with context
- Provide meaningful error messages
- Handle graceful degradation

### 6. Documentation
- Document at module, class, and function levels
- Include usage examples
- Keep documentation in sync with code
- Use type hints as documentation

---

## IDE and Tool Recommendations

### IDEs
- PyCharm Professional (full-featured)
- VS Code + Python extension (lightweight)
- Sublime Text (fast)

### Development Tools
- GitHub Desktop or Git CLI
- Docker Desktop for containerization
- Postman/Insomnia for API testing
- DataGrip for database management

### Linting and Formatting
- VS Code: Python extension with Black formatter
- Pre-commit hooks: automatic formatting on commit
- GitHub Actions: CI/CD linting checks

---

## Documentation Standards

### Module Documentation
```python
"""
module_name: Brief description.

This module handles [functionality]. It provides:
- Feature 1
- Feature 2

Example:
    >>> from src.module import MyClass
    >>> obj = MyClass()
    >>> result = obj.method()
"""
```

### Function Documentation
```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.
    
    Longer description if needed, explaining:
    - What it does
    - Why it's useful
    - Any important notes
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        bool: Description of return value
        
    Raises:
        ValueError: When this condition occurs
        
    Example:
        >>> result = my_function("test", 42)
        >>> print(result)
        True
    """
```

