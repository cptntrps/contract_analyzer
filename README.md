# Contract Analyzer

An enterprise-grade contract analysis application that compares contracts against templates using AI/LLM analysis and generates professional reports in multiple formats.

## Architecture

This application follows a **Domain-Driven Design (DDD)** architecture with clean separation of concerns:

- **Domain Layer**: Core business entities and logic
- **Application Layer**: Use cases and orchestration
- **Infrastructure Layer**: External dependencies and integrations
- **Presentation Layer**: API endpoints and web interface

## Project Structure

```
contract-analyzer/
├── app/                           # Main application code
│   ├── core/                     # Domain layer
│   │   ├── models/               # Domain entities
│   │   │   ├── contract.py       # Contract entity
│   │   │   └── analysis_result.py # Analysis result aggregates
│   │   └── services/             # Core business services
│   │       ├── analyzer.py       # Contract analysis orchestrator
│   │       ├── document_processor.py # Document processing
│   │       └── comparison_engine.py  # Text comparison
│   ├── api/                      # Presentation layer
│   │   ├── routes/               # REST API endpoints
│   │   │   ├── contracts.py      # Contract management
│   │   │   ├── analysis.py       # Analysis workflows
│   │   │   ├── reports.py        # Report generation
│   │   │   ├── health.py         # Health monitoring
│   │   │   └── prompts.py        # Prompt management
│   │   ├── middleware/           # Request/response middleware
│   │   └── schemas/              # API schemas and validation
│   ├── services/                 # Infrastructure layer
│   │   ├── llm/                  # LLM integration
│   │   │   └── providers/        # LLM provider implementations
│   │   │       ├── base.py       # Abstract provider
│   │   │       └── openai.py     # OpenAI implementation
│   │   ├── reports/              # Report generation
│   │   │   ├── formatters/       # Format-specific generators
│   │   │   │   ├── excel.py      # Excel report formatter
│   │   │   │   ├── word.py       # Word document formatter
│   │   │   │   └── pdf.py        # PDF report formatter
│   │   │   └── generator.py      # Report orchestrator
│   │   └── storage/              # Storage management
│   │       └── file_manager.py   # File operations
│   ├── config/                   # Configuration management
│   │   ├── settings.py           # Environment-based config
│   │   ├── environments/         # Environment-specific settings
│   │   └── user_settings.py      # User preferences
│   ├── utils/                    # Cross-cutting concerns
│   │   ├── logging/              # Logging configuration
│   │   ├── security/             # Security validation
│   │   └── cache/                # Caching utilities
│   └── main.py                   # Application factory
├── tests/                        # Comprehensive test suite
│   ├── unit/                     # Unit tests for all components
│   ├── integration/              # Integration tests
│   ├── e2e/                      # End-to-end workflow tests
│   └── conftest.py               # Test configuration and fixtures
├── data/                         # Application data
│   ├── uploads/                  # Contract uploads
│   ├── templates/                # Contract templates
│   └── reports/                  # Generated reports
├── scripts/                      # Development and utility scripts
│   ├── start_dev.py              # Development server
│   ├── test_openai_models.py     # LLM testing
│   └── select_openai_model.py    # Model selection
├── docs/                         # Documentation
│   ├── api/                      # API documentation
│   ├── setup/                    # Setup and deployment guides
│   ├── technical/                # Technical documentation
│   ├── architecture/             # Architecture documentation
│   └── user/                     # User guides
├── deployment/                   # Deployment configurations
│   ├── docker/                   # Docker configurations
│   ├── k8s/                      # Kubernetes manifests
│   └── Dockerfile               # Main Docker image
├── static/                       # Web assets
│   ├── css/                      # Stylesheets
│   └── js/                       # JavaScript files
├── templates/                    # HTML templates
│   └── dashboard.html            # Main dashboard
└── [Configuration Files]
    ├── requirements.txt          # Python dependencies
    ├── pyproject.toml           # Project metadata
    ├── pytest.ini              # Test configuration
    ├── docker-compose.yml       # Local development stack
    └── .env.example             # Environment template
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install python-json-logger  # For enhanced logging
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

3. **Start the application:**
   ```bash
   python scripts/start_dev.py
   ```

4. **Access the application:**
   - **Dashboard**: http://localhost:5000/
   - **Health Check**: http://localhost:5000/api/health
   - **API Documentation**: http://localhost:5000/api/

5. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

## Key Features

### Core Functionality
- **AI-Powered Analysis**: Uses OpenAI GPT-4o for intelligent contract comparison
- **Multi-Format Reports**: Generate professional PDF, Excel, and Word documents
- **Template Matching**: Smart template selection and comparison
- **Change Classification**: Automatic categorization of changes as Critical, Significant, or Inconsequential
- **Risk Assessment**: Built-in risk level calculation and recommendations

### Technical Features
- **Modular Architecture**: Domain-driven design with clean separation of concerns
- **RESTful API**: Comprehensive API for all operations
- **Security**: Input validation, audit logging, and secure file handling
- **Testing**: 37+ unit tests with comprehensive coverage
- **Configuration**: Environment-based configuration management
- **Logging**: Structured JSON logging with multiple levels
- **Docker Support**: Full containerization for deployment

### Business Features
- **Contract Lifecycle**: Upload, analyze, and track contract changes
- **Executive Reporting**: Summary reports for stakeholder review
- **Audit Trail**: Complete tracking of all analysis activities
- **Batch Processing**: Handle multiple contracts efficiently
- **Template Management**: Organize and manage contract templates

## API Endpoints

### Core Operations
- `POST /api/contracts/upload` - Upload contract files
- `POST /api/analysis/start` - Start contract analysis
- `POST /api/reports/generate` - Generate analysis reports
- `GET /api/contracts` - List uploaded contracts
- `GET /api/health` - Application health check

### Management
- `GET /api/status` - Detailed system status
- `GET /api/templates` - Available contract templates
- `POST /api/contracts/clear` - Clear uploaded contracts
- `GET /api/prompts` - Analysis prompt management

## Configuration

Configuration is managed through multiple layers:

1. **Environment Variables** (`.env` file)
   - `OPENAI_API_KEY` - Required for AI analysis
   - `FLASK_ENV` - Environment (development/production)
   - `DEBUG` - Debug mode toggle

2. **User Settings** (`app/config/user_config.json`)
   - LLM model selection and parameters
   - Analysis settings and thresholds
   - UI preferences

3. **Environment-Specific** (`app/config/environments/`)
   - Development, production, and testing configurations
   - Environment-specific overrides

## Development

### Running in Development
```bash
# Start development server with hot reload
python scripts/start_dev.py

# Run specific test categories
pytest tests/unit/ -v           # Unit tests
pytest tests/integration/ -v    # Integration tests
pytest tests/e2e/ -v           # End-to-end tests

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Code Organization
- **Domain Models**: `app/core/models/` - Business entities (Contract, AnalysisResult, Change)
- **Core Services**: `app/core/services/` - Business logic (DocumentProcessor, ComparisonEngine, ContractAnalyzer)
- **Infrastructure**: `app/services/` - External integrations (LLM, Reports, Storage)
- **API Layer**: `app/api/routes/` - REST endpoints and request handling

### Architecture Benefits
- **Testability**: Modular design with dependency injection
- **Maintainability**: Single responsibility principle throughout
- **Extensibility**: Easy to add new LLM providers, report formats, etc.
- **Type Safety**: Comprehensive type hints and validation

## Documentation

### Available Documentation
- **Setup Guide**: `docs/setup/DEPLOYMENT.md` - Comprehensive deployment instructions
- **API Reference**: `docs/api/` - Complete API documentation with examples
- **Architecture**: `docs/architecture/` - System design and patterns
- **Technical**: `docs/technical/` - In-depth technical documentation
- **User Guide**: `docs/user/` - End-user documentation

### Key Documentation Files
- **Environment Variables**: `docs/technical/ENVIRONMENT_VARIABLES.md`
- **Model Selection**: `docs/setup/MODEL_SWITCHING_GUIDE.md`
- **Docker Deployment**: `deployment/README.md`
- **Word COM Setup**: `docs/setup/WORD_COM_SETUP.md` (Windows only)

## Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Production deployment
docker build -t contract-analyzer .
docker run -p 5000:5000 contract-analyzer
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set production environment
export FLASK_ENV=production
export DEBUG=false

# Start application
python -m app.main
```

## Support and Troubleshooting

### Common Issues
1. **Import Errors**: Ensure you're running from the project root directory
2. **Missing Dependencies**: Run `pip install -r requirements.txt`
3. **OpenAI API**: Verify your API key is set in `.env`
4. **Port Conflicts**: Application runs on port 5000 by default

### Getting Help
- Check the `docs/` directory for comprehensive documentation
- Review the test suite in `tests/` for usage examples
- Examine the API endpoints in `app/api/routes/`
- Check application logs in `output/logs/`

### Health Monitoring
- **Health Check**: http://localhost:5000/api/health
- **System Status**: http://localhost:5000/api/status
- **Log Files**: `output/logs/dashboard.log`