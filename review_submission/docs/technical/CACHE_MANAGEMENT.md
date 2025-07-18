# Cache Management

The Contract Analyzer Dashboard includes comprehensive cache management functionality to help you control system performance and storage usage.

## Overview

The system maintains two types of cache:

1. **Memory Cache**: In-memory storage for analysis results, contracts, and templates
2. **File Cache**: Persistent storage including analysis results JSON and generated reports

## Cache Management Interface

### Accessing Cache Management

1. Open the dashboard at `http://localhost:5000`
2. Click on the "Settings" tab in the sidebar
3. Scroll down to the "Cache Management" section

### Cache Statistics

The cache statistics display shows:

- **Memory Cache**:
  - Analysis Results: Number of cached analysis results
  - Contracts: Number of loaded contracts
  - Templates: Number of loaded templates

- **File Cache**:
  - Analysis JSON: Whether analysis_results.json exists and its size
  - Report Files: Number of generated reports and total size

### Clear Cache Options

#### 1. Clear Analysis
- **What it does**: Removes all analysis results from memory and files
- **Files affected**: 
  - Clears `analysis_results.json`
  - Clears in-memory analysis results
- **Use when**: You want to remove all analysis data but keep reports

#### 2. Clear Reports
- **What it does**: Removes all generated report files
- **Files affected**:
  - All `.docx` files in the `reports/` directory
  - All `.json` metadata files in the `reports/` directory
- **Use when**: You want to free up disk space by removing reports

#### 3. Clear Memory
- **What it does**: Clears only in-memory cache
- **Files affected**: None (only RAM cache)
- **Use when**: You want to refresh the dashboard without losing files

#### 4. Clear All
- **What it does**: Comprehensive cache clearing
- **Files affected**:
  - All in-memory cache
  - `analysis_results.json`
  - All files in `reports/` directory
- **Use when**: You want to start fresh or troubleshoot issues

## API Endpoints

### Get Cache Statistics
```
GET /api/cache-stats
```

Returns detailed cache statistics in JSON format.

### Clear Cache
```
POST /api/clear-cache
Content-Type: application/json

{
  "cache_type": "all|memory|files|reports|analysis"
}
```

#### Parameters
- `cache_type` (string): Type of cache to clear
  - `all`: Clear everything
  - `memory`: Clear only memory cache
  - `files`: Clear only file cache
  - `reports`: Clear only report files
  - `analysis`: Clear only analysis results

#### Response
```json
{
  "success": true,
  "message": "Cache cleared successfully",
  "cleared_items": [
    "In-memory analysis results (5 items)",
    "Analysis results JSON file",
    "Report files (3 .docx, 2 .json)"
  ],
  "cache_type": "all"
}
```

## Safety Features

1. **Confirmation Dialog**: UI prompts for confirmation before clearing cache
2. **Audit Logging**: All cache operations are logged for security
3. **Selective Clearing**: Choose exactly what to clear
4. **File Preservation**: Original uploaded contracts and templates are never deleted

## Troubleshooting

### Dashboard Not Loading
- Try clearing memory cache first
- If that doesn't work, clear all cache

### Old Analysis Results Appearing
- Clear analysis cache to remove outdated results

### Disk Space Issues
- Clear reports to free up space
- Check cache statistics to identify large files

### Performance Issues
- Clear memory cache to refresh the system
- Consider clearing all cache if problems persist

## Best Practices

1. **Regular Maintenance**: Clear cache periodically to maintain performance
2. **Before Important Analysis**: Clear cache before processing critical contracts
3. **Disk Space Monitoring**: Use cache statistics to monitor disk usage
4. **Selective Clearing**: Use specific cache types rather than "Clear All" when possible

## Security Notes

- All cache operations are logged in the security audit log
- Cache clearing requires appropriate permissions
- Original contract and template files are never affected by cache operations
- Only analysis results and generated reports are cleared

## Integration

The cache management system integrates with:
- Dashboard refresh functionality
- Security audit logging
- File system monitoring
- Performance metrics

For technical support or questions about cache management, check the system logs or contact the development team. 