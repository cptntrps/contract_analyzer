# Contract Analyzer Test Suite

This directory contains comprehensive tests for the Contract Analyzer application.

## Test Structure

```
tests/
├── unit/                   # Unit tests for individual components
│   ├── test_analyzer.py   # Tests for ContractAnalyzer class
│   ├── test_llm_handler.py # Tests for LLMHandler and enhanced redlining
│   └── ...
├── integration/           # Integration tests for component interactions
│   ├── test_api_endpoints.py # Tests for REST API endpoints
│   └── ...
├── e2e/                   # End-to-end tests for complete workflows
│   ├── test_contract_workflow.py # Complete contract analysis workflows
│   └── ...
├── fixtures/              # Test data and fixtures
├── conftest.py           # Pytest configuration and fixtures
└── README.md             # This file
```

## Running Tests

### Quick Start

```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py unit
python run_tests.py integration
python run_tests.py e2e

# Run with coverage
python run_tests.py --coverage

# Run in parallel
python run_tests.py --parallel
```

### Using pytest directly

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_analyzer.py

# Run specific test class
pytest tests/unit/test_analyzer.py::TestContractAnalyzer

# Run specific test method
pytest tests/unit/test_analyzer.py::TestContractAnalyzer::test_init

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run with verbose output
pytest tests/ -v

# Run in parallel
pytest tests/ -n auto
```

### Test Markers

Tests are organized using pytest markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests  
pytest -m integration

# Run only e2e tests
pytest -m e2e

# Run only slow tests
pytest -m slow

# Run only LLM tests
pytest -m llm

# Run only security tests
pytest -m security

# Skip slow tests
pytest -m "not slow"
```

## Test Dependencies

Install test dependencies:

```bash
pip install -r test-requirements.txt
```

Key testing libraries:
- **pytest**: Test framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities
- **pytest-xdist**: Parallel test execution
- **pytest-html**: HTML test reports
- **pytest-json-report**: JSON test reports
- **factory-boy**: Test data generation
- **faker**: Fake data generation
- **freezegun**: Time manipulation for tests
- **responses**: HTTP request mocking

## Test Categories

### Unit Tests (`tests/unit/`)

Test individual components in isolation:

- **ContractAnalyzer**: Document processing and text comparison
- **LLMHandler**: AI analysis and multi-stakeholder redlining
- **LLMProviders**: OpenAI and Ollama provider implementations
- **SecurityValidator**: Input validation and security checks
- **EnhancedReportGenerator**: Report generation in multiple formats
- **UserConfigManager**: Configuration management

### Integration Tests (`tests/integration/`)

Test component interactions:

- **API Endpoints**: REST API functionality
- **Database Operations**: Data persistence and retrieval
- **File Operations**: Upload, storage, and processing
- **Report Generation**: End-to-end report creation
- **Security Integration**: Authentication and authorization
- **Model Management**: LLM provider switching

### End-to-End Tests (`tests/e2e/`)

Test complete workflows:

- **Contract Analysis Workflow**: Upload → Analysis → Report Generation
- **Multi-Stakeholder Analysis**: Complex procurement contract analysis
- **Batch Processing**: Multiple contract analysis
- **Error Recovery**: Handling failures and edge cases
- **Model Switching**: Changing LLM providers during analysis
- **Configuration Management**: System configuration changes

## Test Data and Fixtures

The test suite uses various fixtures and test data:

### Fixtures (`conftest.py`)

- `client`: Flask test client
- `dashboard_server`: Dashboard server instance
- `mock_llm_handler`: Mocked LLM handler
- `test_docx_file`: Sample DOCX file
- `test_template_file`: Sample template file
- `sample_contract_data`: Sample contract metadata
- `sample_analysis_data`: Sample analysis results

### Test Data Generation

```python
# Generate test contract text
contract_text = generate_test_contract_text({
    'company_name': 'Test Company',
    'date': '2025-01-01',
    'amount': '$1,000'
})

# Generate test template text
template_text = generate_test_template_text()
```

## Writing Tests

### Test Structure

Follow the AAA pattern (Arrange, Act, Assert):

```python
def test_example_function(self, fixture_name):
    # Arrange
    input_data = "test input"
    expected_output = "expected result"
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
```

### Mocking

Use pytest-mock for mocking:

```python
def test_with_mock(self, mocker):
    # Mock external dependency
    mock_llm = mocker.patch('module.llm_handler.LLMHandler')
    mock_llm.return_value.analyze.return_value = "mocked result"
    
    # Test code that uses the mocked dependency
    result = function_that_uses_llm()
    assert result == "mocked result"
```

### Parametrized Tests

Test multiple scenarios:

```python
@pytest.mark.parametrize("input_value,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
    ("test3", "result3"),
])
def test_multiple_scenarios(self, input_value, expected):
    result = function_under_test(input_value)
    assert result == expected
```

### Test Markers

Mark tests appropriately:

```python
@pytest.mark.unit
def test_unit_functionality():
    pass

@pytest.mark.integration
def test_integration_functionality():
    pass

@pytest.mark.slow
def test_slow_functionality():
    pass

@pytest.mark.llm
def test_llm_dependent_functionality():
    pass
```

## Coverage Reports

Generate coverage reports:

```bash
# Generate HTML coverage report
pytest tests/ --cov=. --cov-report=html

# Generate terminal coverage report
pytest tests/ --cov=. --cov-report=term-missing

# Set coverage threshold
pytest tests/ --cov=. --cov-fail-under=80
```

Coverage reports are generated in:
- HTML: `reports/coverage/index.html`
- Terminal: Displayed after test run

## Test Reports

Generate detailed test reports:

```bash
# Generate HTML test report
pytest tests/ --html=reports/test_report.html

# Generate JSON test report
pytest tests/ --json-report --json-report-file=reports/test_report.json
```

## Best Practices

### Test Organization

1. **Group related tests** in classes
2. **Use descriptive test names** that explain what is being tested
3. **Keep tests independent** - each test should be able to run in isolation
4. **Use fixtures** for common setup and teardown
5. **Mock external dependencies** to isolate the code under test

### Test Data

1. **Use factories** for generating test data
2. **Create minimal test data** that covers the scenario
3. **Use meaningful test data** that reflects real-world usage
4. **Clean up test data** after each test

### Performance

1. **Run tests in parallel** for faster execution
2. **Use fixtures with appropriate scope** (function, class, module, session)
3. **Mock expensive operations** like file I/O and network calls
4. **Mark slow tests** so they can be skipped during development

### Debugging

1. **Use verbose output** (`-v`) to see detailed test results
2. **Run specific tests** when debugging
3. **Use print statements** or debugger for complex issues
4. **Check test logs** for additional information

## Continuous Integration

The test suite is designed to work in CI/CD environments:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    python -m pytest tests/ --cov=. --cov-report=xml
    
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v1
  with:
    file: ./coverage.xml
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
2. **File not found**: Check that test files exist in the correct location
3. **Mock errors**: Verify mock paths and return values
4. **Timeout errors**: Increase timeout for slow tests

### Debug Commands

```bash
# Run tests with maximum verbosity
pytest tests/ -vvv

# Run tests and drop into debugger on failure
pytest tests/ --pdb

# Run tests and show local variables on failure
pytest tests/ -l

# Run tests and show warnings
pytest tests/ --disable-warnings=false
```

## Contributing

When adding new tests:

1. **Follow the existing structure** and naming conventions
2. **Add appropriate test markers** for categorization
3. **Update fixtures** if new test data is needed
4. **Document complex test scenarios** with comments
5. **Ensure tests pass** before submitting pull requests

## Test Coverage Goals

- **Unit tests**: 90%+ coverage of individual components
- **Integration tests**: 80%+ coverage of component interactions
- **E2E tests**: 70%+ coverage of complete workflows
- **Overall**: 85%+ total test coverage

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Factory Boy documentation](https://factoryboy.readthedocs.io/)
- [Faker documentation](https://faker.readthedocs.io/)
- [Testing best practices](https://docs.python-guide.org/writing/tests/)