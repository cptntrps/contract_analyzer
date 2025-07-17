# Contract Analyzer

An enterprise-grade contract analysis application that compares contracts against templates using AI/LLM analysis and generates professional reports in multiple formats.

## Project Structure

```
contract-analyzer/
├── src/                           # Source code
│   ├── analyzer.py               # Contract analysis engine
│   ├── config.py                 # Configuration management
│   ├── dashboard_server.py       # Flask web server
│   ├── enhanced_report_generator.py # Report generation
│   ├── llm_handler.py           # LLM integration
│   ├── llm_providers.py         # LLM provider implementations
│   ├── security.py              # Security validation
│   ├── user_config_manager.py   # User configuration
│   └── utils/                   # Utility modules
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
├── data/                         # Data directories
│   ├── uploads/                 # Contract uploads
│   ├── templates/               # Contract templates
│   └── reports/                 # Generated reports
├── output/                       # Generated output files
│   ├── logs/                    # Application logs
│   ├── test-results/            # Test results and reports
│   ├── coverage/                # Coverage reports
│   └── artifacts/               # Build artifacts
├── scripts/                      # Utility scripts
│   ├── start_dashboard.py       # Main startup script
│   ├── run_tests.py             # Test runner
│   └── *.py                     # Other utility scripts
├── config/                       # Configuration files
│   ├── pytest.ini              # Test configuration
│   ├── requirements.txt         # Dependencies
│   └── *.json                   # User configurations
├── docs/                         # Documentation
│   ├── api/                     # API documentation
│   ├── setup/                   # Setup guides
│   └── technical/               # Technical documentation
├── deployment/                   # Deployment files
│   ├── Dockerfile              # Docker configuration
│   └── Procfile                # Heroku deployment
├── static/                       # Web assets
│   ├── css/                     # Stylesheets
│   └── js/                      # JavaScript files
├── templates/                    # HTML templates
└── [Root Files]                  # Essential project files
    ├── .gitignore               # Git ignore patterns
    ├── CHANGELOG.md             # Version history
    ├── README.md                # This file
    ├── VERSION                  # Version identifier
    ├── start_dashboard.py       # Startup wrapper
    ├── run_tests.py             # Test runner wrapper
    └── pytest.ini               # Test configuration (copied for discovery)
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r config/requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

3. **Start the application:**
   ```bash
   python start_dashboard.py
   ```

4. **Run tests:**
   ```bash
   python run_tests.py
   ```

## Key Features

- **OpenAI Integration**: Uses GPT-4o for contract analysis
- **Multi-format Reports**: PDF, Excel, and Word document generation
- **Security**: Comprehensive input validation and audit logging
- **Web Interface**: Flask-based dashboard for easy management
- **Testing**: Full test suite with unit, integration, and e2e tests

## Configuration

All configuration is managed through environment variables. See `docs/technical/ENVIRONMENT_VARIABLES.md` for details.

## Development

- **Source code**: All application code is in `src/`
- **Tests**: Run with `python run_tests.py`
- **Logs**: Check `output/logs/` for application logs
- **Coverage**: Generate with `python run_tests.py --coverage`

## Documentation

- **API**: See `docs/api/` for API documentation
- **Setup**: See `docs/setup/` for detailed setup instructions
- **Technical**: See `docs/technical/` for technical documentation

## Support

For issues and questions, check the documentation in the `docs/` directory or review the codebase structure above.