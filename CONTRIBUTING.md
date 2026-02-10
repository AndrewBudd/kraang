# Contributing to Kraang

Thank you for your interest in contributing to Kraang! This document provides guidelines for contributing to the project.

## Project Philosophy

Kraang is built on the thesis that **"The core activity of building software is rationalizing conflicting constraints."** All contributions should align with this core philosophy.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/kraang.git
   cd kraang
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up API key** (for extraction features):
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Development Workflow

### Making Changes

1. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style:
   - Use clear, descriptive variable names
   - Add docstrings to functions and classes
   - Keep functions focused and single-purpose
   - Follow PEP 8 style guidelines

3. **Test your changes**:
   ```bash
   # Test the CLI
   ./kraang --help

   # Test specific modules
   python src/conflict_detector.py
   python src/impact_analyzer.py

   # Run example tests
   python examples/test.py
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Brief description of your changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** on GitHub

### Code Organization

```
src/          - Core engine modules
bin/          - Utility scripts
examples/     - Demo scripts and tests
docs/         - User documentation
docs/archive/ - Development session history
```

## Types of Contributions

### Bug Fixes

- Clear description of the bug
- Steps to reproduce
- Your fix with explanation
- Test demonstrating the fix works

### New Features

Before implementing a major feature:
1. **Open an issue** to discuss the feature
2. **Explain the use case** and how it fits the thesis
3. **Get feedback** from maintainers
4. **Implement** after discussion

### Documentation

- Fix typos or clarify existing docs
- Add examples or tutorials
- Improve README or guides

### Analysis Tools

New analysis tools should:
- Work with existing `.kraang/` data structure
- Provide fast, local analysis (no API if possible)
- Output clear, actionable insights
- Include usage examples

## Code Style

### Python

- **PEP 8** compliance
- **Type hints** where helpful
- **Docstrings** for public functions
- **Clear variable names**
- **Comments** for complex logic only

Example:
```python
def analyze_conflict(fact1: Dict[str, Any], fact2: Dict[str, Any]) -> Optional[Conflict]:
    """
    Analyze two facts to determine if they conflict.

    Args:
        fact1: First fact dictionary with 'statement' and 'type'
        fact2: Second fact dictionary with 'statement' and 'type'

    Returns:
        Conflict object if facts contradict, None otherwise
    """
    # Implementation...
```

### Commit Messages

- **Present tense**: "Add feature" not "Added feature"
- **Imperative mood**: "Fix bug" not "Fixes bug"
- **Brief first line**: <50 chars
- **Detailed explanation**: In body if needed

Example:
```
Add support for multi-file conflict analysis

- Extends conflict detector to analyze across files
- Adds artifact grouping by directory
- Improves performance with caching
```

## Testing

### Manual Testing

1. Initialize a test knowledge base:
   ```bash
   mkdir test-kb
   cd test-kb
   ../kraang init
   ```

2. Add test artifacts and extract facts

3. Verify tools work correctly:
   ```bash
   python ../src/conflict_detector.py
   python ../src/impact_analyzer.py
   ```

### Testing the Web Interface

```bash
python -m http.server 8000
# Open http://localhost:8000/fact-browser.html
```

## Questions?

- **Open an issue** for questions about contributing
- **Check existing issues** for discussions
- **Review the docs** in `docs/` and `docs/archive/`

## License

By contributing to Kraang, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping improve Kraang! 🎉
