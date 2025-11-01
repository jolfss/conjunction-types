# Development Setup

## Installing for Development

```bash
# Clone the repository
git clone https://github.com/yourusername/product-types.git
cd product-types

# Create a virtual environment (Python 3.14+)
python3.14 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=product_types --cov-report=html

# Run specific test file
pytest tests/test_product_types.py

# Run with verbose output
pytest -v
```

## Type Checking

```bash
# Check with mypy
mypy product_types/

# Check with pyright
pyright product_types/

# Check examples
mypy examples/
pyright examples/
```

## Running Examples

```bash
# Run the interactive demo
python examples/demo.py

# Run type hint verification
python examples/type_hint_verification.py
```

## Building the Package

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the built package
twine check dist/*
```

## Publishing to PyPI

```bash
# Test PyPI (recommended first)
twine upload --repository testpypi dist/*

# Production PyPI
twine upload dist/*
```

## Code Style

This project follows PEP 8 and uses type hints throughout.

```bash
# Format code (if using black)
black product_types/ tests/ examples/

# Lint code (if using ruff)
ruff check product_types/ tests/ examples/
```

## Documentation

Documentation is in the `docs/` directory and uses Markdown format.

## Project Structure

```
product-types/
├── product_types/          # Main package
│   ├── __init__.py        # Package exports
│   ├── _core.py           # Core implementation
│   └── py.typed           # PEP 561 marker
├── tests/                 # Test suite
│   └── test_product_types.py
├── examples/              # Example scripts
│   ├── demo.py
│   └── type_hint_verification.py
├── docs/                  # Documentation
│   ├── README.md
│   ├── QUICK_REFERENCE.md
│   └── ...
├── pyproject.toml         # Package configuration
├── README.md              # Main readme
├── LICENSE                # MIT license
└── MANIFEST.in           # Package manifest
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and type checking
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Requirements

- Python 3.14+
- typing-extensions >= 4.12.0

## Development Dependencies

- pytest >= 8.0.0
- mypy >= 1.11.0
- pyright >= 1.1.380

## Release Process

1. Update version in `pyproject.toml` and `product_types/__init__.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Build package: `python -m build`
5. Test on TestPyPI
6. Tag release: `git tag v0.1.0`
7. Push tags: `git push --tags`
8. Upload to PyPI: `twine upload dist/*`
9. Create GitHub release

## Support

For bugs, feature requests, or questions:
- Open an issue on GitHub
- Check existing issues and documentation first
- Provide minimal reproducible examples for bugs
