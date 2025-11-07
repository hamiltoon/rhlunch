# Contributing to RHLunch

Thank you for considering contributing to RHLunch! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/hamiltoon/rhlunch.git
   cd rhlunch
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install in development mode with test dependencies**
   ```bash
   pip install -e ".[test]"
   ```

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run with coverage report
```bash
pytest tests/ -v --cov=lunchscraper --cov-report=html
```

Open `htmlcov/index.html` in your browser to view the detailed coverage report.

### Run specific test file
```bash
pytest tests/test_dish_classifier.py -v
```

### Run specific test
```bash
pytest tests/test_dish_classifier.py::TestClassifyDish::test_classify_vegetarian_dishes -v
```

## Test Fixtures

Test fixtures are organized by date in `tests/fixtures/`. See [tests/fixtures/README.md](tests/fixtures/README.md) for details.

### Adding New Test Fixtures

To fetch fresh HTML snapshots:
```bash
python tests/fixtures/fetch_test_data.py
```

To fetch for a specific date:
```bash
python tests/fixtures/fetch_test_data.py --date 2025-12-15
```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write descriptive docstrings for functions and classes
- Keep functions focused and small

## Writing Tests

- Write tests for all new features
- Ensure existing tests still pass
- Aim for high coverage on core scrapers (>90%)
- Use descriptive test names that explain what is being tested
- Use fixtures for shared test data

### Test Structure

```python
def test_specific_behavior():
    """Test that [specific behavior] works correctly."""
    # Arrange - set up test data
    test_input = "..."

    # Act - call the function being tested
    result = function_under_test(test_input)

    # Assert - verify the result
    assert result == expected_value
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run tests locally**
   ```bash
   pytest tests/ -v
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

   Use [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test changes
   - `refactor:` for code refactoring

5. **Push to GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to the repository on GitHub
   - Click "New Pull Request"
   - Fill out the PR template
   - Wait for CI to pass
   - Request review

## CI/CD

All pull requests automatically run tests via GitHub Actions:
- Tests run on Python 3.8, 3.9, 3.10, 3.11, and 3.12
- Coverage reports are generated
- All tests must pass before merging

## Code Review

- Be respectful and constructive
- Explain your reasoning
- Be open to feedback
- Keep discussions focused on the code

## Questions?

If you have questions, feel free to:
- Open an issue
- Ask in the pull request
- Check existing documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
