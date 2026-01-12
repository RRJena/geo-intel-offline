# Contributing to geo-intel-offline

Thank you for your interest in contributing to geo-intel-offline! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/geo-intel-offline.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes: `python run_tests.py`
6. Commit your changes: `git commit -m 'Add some feature'`
7. Push to your branch: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Run tests
python run_tests.py

# Build package
python scripts/build_package.py
```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and small

## Testing

- Write tests for new features
- Ensure all existing tests pass
- Test edge cases and error conditions
- Test with multiple Python versions (3.8+)

## Commit Messages

- Use clear, descriptive commit messages
- Reference issue numbers if applicable
- Format: `type(scope): description`

Examples:
- `feat(resolver): add support for custom data directory`
- `fix(pip): handle edge case in polygon validation`
- `docs(readme): update installation instructions`

## Pull Request Process

1. Update documentation if needed
2. Ensure all tests pass
3. Update CHANGELOG.md if applicable
4. Request review from maintainers
5. Address any feedback

## Questions?

Feel free to open an issue for any questions about contributing.
