# Contributing Guidelines

## Welcome!

Thank you for considering contributing to the PV Testing Protocol Framework. This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Follow professional standards

## How to Contribute

### Reporting Bugs

1. Check existing issues first
2. Create new issue with:
   - Clear title
   - Detailed description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Screenshots if applicable

### Suggesting Enhancements

1. Open issue with `enhancement` label
2. Describe the feature
3. Explain use cases
4. Discuss implementation approach

### Submitting Code

#### Fork and Branch

```bash
# Fork repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/test-protocols.git
cd test-protocols

# Create feature branch
git checkout -b feature/your-feature-name
```

#### Make Changes

1. Write code following style guidelines
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass

#### Commit Messages

Use conventional commits format:
```
type(scope): brief description

Detailed explanation if needed

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(protocols): add PVTP-055 spectral response protocol

- Implement spectral response measurement
- Add data analysis functions
- Create UI page for execution

Closes #456
```

#### Submit Pull Request

1. Push to your fork
2. Open pull request to `main` branch
3. Fill out PR template
4. Link related issues
5. Wait for review

## Development Setup

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Check code style
black .
pylint pv_testing/
mypy pv_testing/
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_protocols.py

# Run with coverage
pytest --cov=pv_testing --cov-report=html
```

## Documentation

- Update relevant `.md` files
- Add docstrings to functions/classes
- Include examples in docstrings
- Update API documentation if needed

## Review Process

1. Automated checks run (CI/CD)
2. Code review by maintainers
3. Address feedback
4. Approval and merge

---

**Thank you for contributing!**
