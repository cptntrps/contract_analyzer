# Contract Analyzer Codebase Cleanup Plan

## Overview
This document outlines a comprehensive plan to clean and organize the Contract Analyzer codebase, removing technical debt and improving maintainability.

## Phase 1: Immediate Cleanup (High Priority)

### 1.1 Remove Generated Files and Bloat
- **Clean reports directory**: Remove 147 generated test files from `/reports/`
- **Clean uploads directory**: Remove test files and temporary uploads
- **Remove log files**: Move `dashboard.log`, `security_audit.log`, `server.log` to `.gitignore`
- **Remove coverage reports**: Move coverage directories to `.gitignore`

### 1.2 Fix Broken References
- **Remove Ollama references**: Update test files to remove references to removed Ollama provider
  - `tests/unit/test_llm_handler.py` (lines 15-21, 31-38)
  - `tests/conftest.py` (lines 21, 41-42, 45, 172-182)
  - `llm_handler.py` (remove Ollama imports)
- **Update requirements.txt**: Add missing dependencies
  - `python-dotenv`
  - `reportlab`
  - `openpyxl`
  - `pywin32` (Windows only)

### 1.3 Configuration Cleanup
- **Reset user_config.json**: Reset to clean defaults
- **Update environment docs**: Remove references to removed features
- **Clean deployment configs**: Keep only actively used deployment files

## Phase 2: Code Organization (Medium Priority)

### 2.1 Standardize Code Style
- **Import organization**: Standardize import ordering (stdlib, third-party, local)
- **Logging consistency**: Ensure all modules use consistent logging patterns
- **Error handling**: Standardize error handling patterns across the codebase
- **Docstring consistency**: Ensure all functions have proper docstrings

### 2.2 Test Organization
- **Fix broken tests**: Remove Ollama references and update test fixtures
- **Consolidate test utilities**: Create centralized test utilities
- **Test data management**: Implement proper test data management strategy
- **Update test configuration**: Remove references to removed features

### 2.3 Documentation Consolidation
- **Restructure docs/**: Consolidate overlapping documentation
  - Merge similar template matching docs in `features/`
  - Consolidate setup guides in `setup/`
  - Organize technical documentation
- **Remove outdated docs**: Clean up `archive/` directory
- **Update API documentation**: Create comprehensive API docs

## Phase 3: Long-term Improvements (Low Priority)

### 3.1 Automated Cleanup
- **Implement file retention policies**: Automatic cleanup of old reports/uploads
- **Add monitoring**: File size monitoring and cleanup alerts
- **Backup strategy**: Implement backup strategy for important files

### 3.2 Enhanced Documentation
- **API documentation**: Comprehensive endpoint documentation
- **Security documentation**: Document security implementation
- **Test strategy documentation**: Document testing approach and requirements

### 3.3 Development Tooling
- **Linting configuration**: Add `.pylintrc` or `pyproject.toml` for consistent linting
- **Pre-commit hooks**: Add pre-commit hooks for code quality
- **CI/CD improvements**: Enhance automated testing and deployment

## Implementation Order

### Step 1: File Cleanup (30 minutes)
1. Clean reports directory
2. Clean uploads directory
3. Remove log files from git
4. Update .gitignore

### Step 2: Code Fixes (45 minutes)
1. Fix test references to Ollama
2. Update requirements.txt
3. Remove unused imports
4. Fix broken test configurations

### Step 3: Style Standardization (60 minutes)
1. Standardize import ordering
2. Fix logging inconsistencies
3. Add missing docstrings
4. Standardize error handling

### Step 4: Documentation (45 minutes)
1. Consolidate docs directory
2. Update environment documentation
3. Remove outdated references
4. Update CLAUDE.md with changes

### Step 5: Testing and Validation (30 minutes)
1. Run test suite
2. Fix any broken tests
3. Validate application functionality
4. Run linting checks

## Success Metrics
- [ ] All tests pass
- [ ] No broken imports or references
- [ ] Consistent code style across all files
- [ ] Clean directory structure
- [ ] Updated documentation
- [ ] Reduced repository size
- [ ] Improved maintainability

## Risk Mitigation
- **Backup**: Create backup before major changes
- **Incremental**: Implement changes incrementally
- **Testing**: Test after each major change
- **Documentation**: Document all changes made

## Maintenance Plan
- **Monthly**: Review and clean generated files
- **Quarterly**: Review dependencies and update documentation
- **Annually**: Review overall architecture and organization

## Notes
- This plan focuses on improving maintainability without changing core functionality
- All changes should be tested thoroughly before implementation
- Consider creating a separate cleanup branch for major changes
- Maintain backward compatibility for configuration files where possible