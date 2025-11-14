# Contributing to PV Testing Protocol Framework

Thank you for your interest in contributing to the PV Testing Protocol Framework! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and professional in all interactions. We are committed to providing a welcoming and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, etc.)

### Suggesting Enhancements

We welcome suggestions for new features or improvements. Please open an issue with:
- A clear description of the enhancement
- Use cases and benefits
- Any relevant examples or mockups

### Contributing Code

1. **Fork the repository**
   ```bash
   git fork https://github.com/ganeshgowri-ASA/test-protocols.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the coding standards below
   - Write tests for new functionality
   - Update documentation as needed

4. **Run tests**
   ```bash
   pytest tests/
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Description of changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Ensure all tests pass

## Coding Standards

### Python Style

- Follow PEP 8 style guide
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable and function names

### Documentation

- Add docstrings to all functions and classes
- Use Google-style docstrings
- Update README.md for user-facing changes
- Add protocol documentation in `docs/protocols/`

### Testing

- Write unit tests for new functions
- Write integration tests for workflows
- Aim for >80% code coverage
- Use meaningful test names

### Example

```python
def calculate_degradation(initial_power: float, final_power: float) -> float:
    """
    Calculate power degradation percentage.

    Args:
        initial_power: Initial Pmax in watts
        final_power: Final Pmax in watts

    Returns:
        Degradation percentage (positive value indicates loss)

    Raises:
        ValueError: If initial_power is zero or negative

    Example:
        >>> calculate_degradation(300.0, 285.0)
        5.0
    """
    if initial_power <= 0:
        raise ValueError("Initial power must be greater than 0")

    return ((initial_power - final_power) / initial_power) * 100
```

## Adding New Protocols

To add a new test protocol:

1. **Create JSON definition** in `protocols/YOUR-PROTOCOL.json`
2. **Implement protocol class** in `src/protocols/your_protocol.py`
3. **Create database schema** in `db/schemas/your_protocol_schema.sql`
4. **Build UI component** in `src/ui/your_protocol_ui.py`
5. **Write tests** in `tests/unit/` and `tests/integration/`
6. **Document** in `docs/protocols/YOUR-PROTOCOL.md`

See [Getting Started Guide](docs/guides/getting-started.md) for detailed instructions.

## Commit Message Guidelines

Use clear and descriptive commit messages:

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- First line should be 50 characters or less
- Reference issues and pull requests

### Examples

```
Add HAIL-001 protocol implementation

- Create JSON protocol definition
- Implement Python protocol handler
- Add Streamlit UI component
- Write comprehensive tests

Fixes #42
```

## Pull Request Process

1. Update documentation for any user-facing changes
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers
6. Address review feedback
7. Squash commits if requested

## Testing Guidelines

### Running Tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage
pytest --cov=src tests/

# Specific test file
pytest tests/unit/test_hail_001_protocol.py
```

### Writing Tests

- Test one thing per test function
- Use descriptive test names
- Include positive and negative test cases
- Use fixtures for common setup
- Mock external dependencies

## Documentation Guidelines

### Protocol Documentation

Each protocol should have documentation in `docs/protocols/` that includes:

- Overview and purpose
- Test parameters
- Equipment required
- Detailed procedure
- Pass/fail criteria
- Safety considerations
- References

### Code Documentation

- Add docstrings to all public functions and classes
- Include type hints
- Document parameters, return values, and exceptions
- Provide usage examples

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions about contributing, please:
- Open an issue on GitHub
- Contact the maintainers
- Check the documentation

Thank you for contributing!
