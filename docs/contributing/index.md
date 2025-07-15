# Contributing

Thank you for your interest in contributing to IVEXES! This guide will help you get started with contributing to the project.

## 🎓 Academic Context

IVEXES is developed as part of a bachelor thesis for academic research purposes. Contributions should align with the project's educational and defensive cybersecurity goals.

## 🤝 How to Contribute

There are many ways to contribute to IVEXES:

### 📝 Documentation
- Improve existing documentation
- Add new examples and tutorials
- Fix typos and clarify explanations
- Translate documentation

### 🐛 Bug Reports
- Report bugs and issues
- Provide detailed reproduction steps
- Test and verify bug fixes

### 💡 Feature Requests
- Suggest new features
- Propose improvements
- Share use cases and requirements

### 🔧 Code Contributions
- Fix bugs and issues
- Implement new features
- Improve performance
- Add tests and validation

### 🧪 Testing
- Write new test cases
- Improve test coverage
- Test on different platforms
- Performance testing

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/your-username/ivexes.git
cd ivexes

# Add upstream remote
git remote add upstream https://github.com/LetsDrinkSomeTea/ivexes.git
```

### 2. Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -e ".[dev,docs]"

# Install pre-commit hooks
pre-commit install
```

### 3. Create a Branch

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Or bug fix branch
git checkout -b fix/issue-description
```

## 📋 Development Guidelines

### Code Style

IVEXES uses strict code formatting and linting:

```bash
# Format code
ruff format

# Check code quality
ruff check

# Fix auto-fixable issues
ruff check --fix
```

**Key Style Guidelines:**
- Follow [PEP 8](https://pep8.org/) for Python code
- Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Type hints are required for all public APIs
- Maximum line length: 88 characters

### Documentation

All code must be properly documented:

```python
def example_function(param1: str, param2: int = 10) -> List[str]:
    """Brief description of the function.

    Longer description providing more details about what the function
    does and how to use it.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter with default value.

    Returns:
        A list of strings containing the results.

    Raises:
        ValueError: If param1 is empty.
        TypeError: If param2 is not an integer.

    Example:
        Basic usage example:

        >>> result = example_function("hello", 5)
        >>> print(result)
        ['hello', 'world']
    """
    ...
```

### Testing

All new code must include tests:

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_specific.py

# Run with coverage
python -m pytest --cov=src --cov-report=html
```

**Testing Guidelines:**
- Write unit tests for all new functions
- Include integration tests for complex features
- Test error conditions and edge cases
- Maintain test coverage above 80%

### Security

Security is paramount in IVEXES:

**Security Requirements:**
- Never commit secrets or API keys
- Validate all user inputs
- Use secure defaults
- Follow principle of least privilege
- Document security considerations

**Security Review Process:**
- All security-related changes require review
- Threat modeling for new features
- Penetration testing for major releases

## 🔄 Contribution Process

### 1. Issue First

For significant changes, please open an issue first:

```markdown
**Title:** Clear, descriptive title

**Type:** Bug Report / Feature Request / Documentation

**Description:**
- What is the problem or improvement?
- Why is this important?
- How would you solve it?

**Additional Context:**
- Environment details
- Related issues
- Example use cases
```

### 2. Development

**Workflow:**
1. Assign yourself to the issue
2. Create a feature branch
3. Implement your changes
4. Write/update tests
5. Update documentation
6. Ensure all checks pass

**Commit Guidelines:**
```bash
# Use conventional commit format
git commit -m "feat: add new vulnerability detection feature"
git commit -m "fix: resolve memory leak in sandbox container"
git commit -m "docs: improve API documentation for agents module"
git commit -m "test: add integration tests for code browser"
```

### 3. Pull Request

Create a pull request with:

**Title:** Clear, descriptive title
**Description:**
```markdown
## Summary
Brief description of changes

## Changes
- [ ] Feature/fix implementation
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Changelog updated

## Testing
- Describe how you tested the changes
- Include any relevant test results

## Screenshots/Logs
- Include relevant visual aids if applicable

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests pass
- [ ] Documentation updated
```

### 4. Review Process

**What to Expect:**
- Initial review within 48 hours
- Constructive feedback and suggestions
- Possible requests for changes
- Approval and merge when ready

**Review Criteria:**
- Code quality and style
- Test coverage and quality
- Documentation completeness
- Security considerations
- Performance impact

## 🎯 Contribution Areas

### Priority Areas

1. **Agent Improvements**
   - New agent types for specialized analysis
   - Enhanced coordination algorithms
   - Performance optimizations

2. **Analysis Components**
   - Additional language support
   - New vulnerability detection patterns
   - Integration with security tools

3. **Knowledge Base**
   - Additional security frameworks
   - Improved search capabilities
   - Better knowledge representation

4. **User Experience**
   - Better error messages
   - Improved CLI interface
   - Enhanced documentation

### Good First Issues

Look for issues labeled `good-first-issue`:

- Documentation improvements
- Simple bug fixes
- Test case additions
- Code style improvements

### Advanced Contributions

For experienced contributors:

- Core architecture improvements
- New analysis algorithms
- Performance optimizations
- Security enhancements

## 📚 Resources

### Development Resources

- **[Python Documentation](https://docs.python.org/3/)**
- **[Pydantic Documentation](https://docs.pydantic.dev/)**
- **[Docker Documentation](https://docs.docker.com/)**
- **[MITRE ATT&CK](https://attack.mitre.org/)**

### Security Resources

- **[OWASP Guidelines](https://owasp.org/)**
- **[CWE Database](https://cwe.mitre.org/)**
- **[NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)**

### AI/ML Resources

- **[OpenAI API Documentation](https://platform.openai.com/docs)**
- **[Langchain Documentation](https://docs.langchain.com/)**
- **[ChromaDB Documentation](https://docs.trychroma.com/)**

## ❓ FAQ

### General Questions

**Q: How do I get help with development?**
A: Open a GitHub issue with the `question` label, or join our discussions.

**Q: What Python version should I use?**
A: Python 3.11 is recommended for development, minimum 3.8 for compatibility.

**Q: How do I test my changes?**
A: Run the test suite with `pytest` and ensure all checks pass.

### Contribution Questions

**Q: What size contributions are welcome?**
A: All sizes! From typo fixes to major features.

**Q: Do I need to sign a CLA?**
A: No, but contributions must be compatible with GPL-3.0-or-later.

**Q: How long does review take?**
A: Initial review within 48 hours, full review depends on complexity.

### Technical Questions

**Q: How do I add a new agent type?**
A: Inherit from `BaseAgent` and implement required methods. See existing agents for examples.

**Q: How do I add new vulnerability detection?**
A: Add patterns to the appropriate analysis component and include test cases.

**Q: How do I integrate a new security tool?**
A: Create a new tool module following the existing patterns in `src/ivexes/tools/`.

## 🎉 Recognition

Contributors are recognized in:

- **[Contributors file](https://github.com/LetsDrinkSomeTea/ivexes/graphs/contributors)**
- **Release notes** for significant contributions
- **Documentation** for major feature additions
- **Academic citations** where appropriate

## 📞 Contact

- **GitHub Issues**: For bugs, features, and questions
- **Discussions**: For general conversation and ideas
- **Security Issues**: Email maintainers directly for security vulnerabilities

---

**Thank you for contributing to IVEXES!** Your efforts help advance cybersecurity research and education.