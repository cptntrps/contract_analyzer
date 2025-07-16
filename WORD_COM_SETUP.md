# Word COM Track Changes Setup

## Overview

The Contract Analyzer now includes a fourth column for **Word Track Changes** documents that generates true Word redlined documents with proper track changes, exactly like using Word's Review → Compare → Compare Documents feature.

## Prerequisites

⚠️ **Windows Only Feature**: This functionality requires:
- Windows Operating System
- Microsoft Word installed
- Python `pywin32` library

## Installation

### 1. Install Required Python Package

```bash
pip install pywin32
```

### 2. Verify Microsoft Word is Installed

The system uses Microsoft Word's COM interface to:
- Open template and contract documents
- Perform document comparison
- Generate track changes markup
- Save as proper Word document with revisions

## Features

### 📄 Format
- `.docx` file with Track Changes ON
- Generated via: Review → Compare → Compare Documents
- Identical to manual Word comparison

### 👀 Visual Features

1. **Tracked Insertions**
   - New text appears underlined and in color (e.g., blue or green)
   - Displayed inline, not in margins
   - Marked as: *Inserted: "new text"*

2. **Tracked Deletions**
   - Deleted text shown struck through in red
   - Sometimes appears in balloon comments
   - Marked as: *Deleted: "old text"*

3. **Formatting Changes**
   - Shown in balloons: *Formatted: Font changed from Calibri to Arial*

4. **Moved Text**
   - "Moved from" location (strikethrough and color)
   - "Moved to" location (underline and color)
   - Both parts labeled

5. **Comments** (Optional)
   - Margin balloons explaining changes
   - "Deleted clause 7.1"
   - "Changed termination period from 30 to 60 days"

6. **Review Pane** (Optional)
   - Shows every change
   - Author information
   - Timestamps

## Usage

### Through Dashboard
1. Run analysis on a contract
2. Click the green "Word Track Changes" button (📄 TC)
3. System generates document using Word COM
4. Download the `.docx` file with full track changes

### API Usage
```python
# Generate Word COM redlined document
POST /api/generate-word-com-redlined
{
    "result_id": "contract_analysis_id"
}

# Download generated document
GET /api/download-word-com-redlined?id=contract_analysis_id
```

## Error Handling

If Windows COM interface is not available:
- System gracefully falls back
- User receives notification: "Word Track Changes feature requires Windows with Microsoft Word installed"
- Other report types still function normally

## Security

- All Word COM operations are sandboxed
- Word application runs invisibly (`word.Visible = False`)
- Automatic cleanup of temporary files
- Audit logging of all operations

## Comparison with Other Reports

| Report Type | Format | Method | Track Changes |
|-------------|--------|---------|---------------|
| Redlined Document | .docx | python-docx | Manual formatting |
| Changes Table | .xlsx | openpyxl | Tabular data |
| Summary Report | .pdf | reportlab | Narrative summary |
| **Word Track Changes** | **.docx** | **Word COM** | **True Word tracking** |

## Technical Implementation

The system:
1. Creates temporary contract document from analysis data
2. Uses Word COM interface to compare template vs contract
3. Applies proper track changes formatting
4. Saves as Word document with revisions enabled
5. Cleans up temporary files

## Benefits

- **Legal Team Ready**: Exact format legal teams expect
- **Professional**: True Word track changes, not approximations
- **Comprehensive**: Shows insertions, deletions, moves, and formatting
- **Compatible**: Works with all Word versions and review workflows
- **Automated**: No manual Word operations required

## Troubleshooting

### Common Issues

1. **"Windows COM interface not available"**
   - Install `pywin32`: `pip install pywin32`
   - Verify Windows OS
   - Ensure Microsoft Word is installed

2. **Word COM fails to start**
   - Check Word isn't already running
   - Verify user permissions
   - Restart system if needed

3. **Document generation fails**
   - Check template file exists
   - Verify contract analysis data
   - Review log files for details

### Performance Notes

- Word COM operations are slower than other report types
- Generation time: 5-15 seconds depending on document size
- Recommended for final review documents only

## Future Enhancements

- Support for Word Online API
- Batch processing multiple contracts
- Custom review settings
- Integration with SharePoint/Office 365 