# Changelog

## [1.0.2] - 2025-07-16

### Code Organization (Phase 1)
- ✅ **Documentation restructuring**: Organized loose documentation files into logical directories
- ✅ **Directory structure**: Created `docs/` with subdirectories: `setup/`, `technical/`, `features/`, `archive/`, `samples/`
- ✅ **File organization**: Moved 12 documentation files from root to appropriate categorized locations
- ✅ **Sample files**: Relocated contract samples and test documents to `docs/samples/`
- ✅ **Obsolete cleanup**: Archived outdated test files (`test_sprint_improvements.py`, `test_tabs.js`)

### Quality Assurance
- ✅ **Full functionality testing**: Comprehensive validation of all endpoints and features
- ✅ **Zero regression**: All functionality verified working after reorganization
- ✅ **Performance validation**: Server startup, analysis, downloads, and uploads tested
- ✅ **Security verification**: All security headers and validation confirmed active

### Technical Improvements
- **Cleaner root directory**: Reduced clutter by 15+ files while maintaining functionality
- **Logical documentation structure**: Improved developer navigation and maintenance
- **Better organization**: Setup guides, technical docs, and feature documentation properly categorized
- **Preserved functionality**: No impact on core application features or performance

## [1.0.1] - 2025-07-16

### Bug Fixes
- ✅ **Settings page model loading**: Fixed infinite "Loading models..." state
- ✅ **Model switching functionality**: Corrected endpoint URL and request parameters
- ✅ **File upload validation**: Removed invalid max_size parameter causing errors
- ✅ **Drag and drop enhancements**: Better event handling and visual feedback
- ✅ **Code cleanup**: Removed duplicate functions and improved error handling

### Enhanced Features
- **Model dropdown**: Now loads available models automatically with sizes
- **Model switching**: Proper user feedback and error handling
- **Client-side validation**: DOCX file type and 16MB size limit checks
- **Drag/drop improvements**: Added handleDragLeave and stopPropagation
- **Better notifications**: Type-specific messages for contracts vs templates
- **Element validation**: Proper null checks with console logging

### Technical Improvements
- Fixed `/api/change-model` endpoint integration
- Enhanced drag event handling with proper cleanup
- Improved error messages and user feedback
- Consistent validation patterns across upload functions
- Clean code structure with no duplicate implementations

## [1.0.0] - 2025-07-16

### Major Features
- ✅ **Contract Analysis Engine**: AI-powered contract comparison with LLM integration
- ✅ **Multi-format Report Generation**: Redlined documents, changes tables, and summary reports
- ✅ **Web Dashboard**: Complete UI with tab navigation, file uploads, and download functionality
- ✅ **Security Framework**: Comprehensive input validation, CSP, and audit logging
- ✅ **File Management**: Secure upload/download with validation and sanitization

### Core Functionality
- **Contract Upload & Analysis**: Support for DOCX contract files with template matching
- **AI-Powered Change Detection**: LLM analysis with confidence scoring and classification
- **Report Generation**: 
  - Redlined documents with track changes formatting
  - Excel changes tables with detailed breakdowns
  - PDF summary reports with executive overview
  - Word COM integration for true track changes (Windows)
- **Dashboard Interface**: Real-time analysis results, system status, and file management
- **Download System**: Secure file serving with proper error handling

### Technical Implementation
- **Backend**: Flask server with enhanced security and configuration management
- **Frontend**: Responsive JavaScript dashboard with real-time updates
- **AI Integration**: Ollama LLM integration with timeout and error handling
- **Security**: CSP headers, input sanitization, path traversal protection
- **File Processing**: DOCX text extraction, similarity calculation, change detection

### Fixed Issues
- ✅ Tab switching functionality in dashboard
- ✅ Model status display (no longer shows "Loading...")
- ✅ Report generation endpoint integration
- ✅ Download endpoint file naming consistency
- ✅ Content Security Policy for external resources
- ✅ Automatic report generation during analysis
- ✅ Error handling and user feedback

### Known Limitations
- Requires Ollama LLM service to be running
- DOCX format only for contracts and templates
- In-memory storage for analysis results (not persisted across restarts)
- Windows-only Word COM integration for true track changes

### System Requirements
- Python 3.8+
- Ollama with compatible LLM model
- Required Python packages (see requirements.txt)
- Modern web browser with JavaScript enabled