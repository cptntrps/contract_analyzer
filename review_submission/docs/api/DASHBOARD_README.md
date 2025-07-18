# Contract Analyzer Dashboard

A modern web-based dashboard for the Contract Analyzer tool, providing an intuitive interface for contract analysis, template management, and compliance monitoring.

## Features

### 📊 Dashboard Overview
- **Real-time metrics** showing compliance rates and analysis statistics
- **Recent analysis** table with detailed contract information
- **Visual indicators** for compliance status (compliant, warnings, critical)
- **Template management** overview

### 📝 Contract Management
- **Upload contracts** via drag-and-drop interface
- **Batch analysis** of multiple contracts
- **Status tracking** for each contract (pending, analyzed)
- **File management** with upload history

### 📋 Template Management
- **Template library** with vendor-specific and document-type templates
- **Upload new templates** for analysis
- **Template categorization** (Vendor Specific, Document Type)
- **Template metadata** (last modified, file size)

### 📈 Analysis Reports
- **Download reports** in Word format with track changes
- **Filter reports** by compliance status
- **Report metadata** (similarity scores, change counts)
- **Visual compliance indicators**

### ⚙️ Settings & Configuration
- **Similarity thresholds** for template matching
- **Change thresholds** for compliance levels
- **Notification settings** for alerts
- **System preferences**

## Quick Start

### Option 1: Web Dashboard (Recommended)

1. **Install dependencies:**
   ```bash
   source venv/bin/activate
   pip install flask
   ```

2. **Start the dashboard:**
   ```bash
   python start_dashboard.py
   ```

3. **Open your browser:**
   - Dashboard automatically opens at `http://localhost:5000`
   - Or manually navigate to the URL

### Option 2: Static Dashboard

1. **Open directly in browser:**
   ```bash
   open dashboard.html  # macOS
   xdg-open dashboard.html  # Linux
   ```

2. **Note:** Static version has limited functionality (no file uploads or real-time data)

## Dashboard Structure

```
contractanalyzer/
├── dashboard.html              # Main dashboard HTML
├── dashboard_server.py         # Flask backend server
├── start_dashboard.py          # Startup script
├── static/
│   ├── css/
│   │   └── dashboard.css       # Dashboard styling
│   └── js/
│       └── dashboard.js        # Dashboard functionality
├── templates/                  # Contract templates (.docx)
├── reports/                    # Analysis reports
├── uploads/                    # Uploaded contracts
└── test_contracts/            # Sample contracts
```

## API Endpoints

The Flask backend provides RESTful API endpoints:

### Data Endpoints
- `GET /api/analysis-results` - Get all analysis results
- `GET /api/templates` - Get available templates
- `GET /api/contracts` - Get uploaded contracts
- `GET /api/dashboard-stats` - Get dashboard statistics

### Action Endpoints
- `POST /api/upload-contract` - Upload new contract
- `POST /api/upload-template` - Upload new template
- `POST /api/analyze-contract` - Analyze specific contract
- `POST /api/batch-analyze` - Batch analyze contracts
- `GET /api/download-report` - Download analysis report

## Dashboard Features

### 🎨 Modern UI/UX
- **Responsive design** - Works on desktop, tablet, and mobile
- **Dark mode support** - Automatic based on system preference
- **Professional styling** - Clean, corporate-friendly interface
- **Interactive elements** - Hover effects, animations, transitions

### 📊 Data Visualization
- **Metrics cards** with real-time statistics
- **Status badges** with color-coded compliance levels
- **Progress indicators** for file uploads
- **Data tables** with sorting and filtering

### 🔒 Security Features
- **File validation** - Only .docx files accepted
- **Path security** - Prevents directory traversal
- **File size limits** - 16MB maximum upload
- **Secure filenames** - Sanitized file naming

### 🚀 Performance
- **Lazy loading** - Content loaded as needed
- **Async operations** - Non-blocking file uploads
- **Efficient rendering** - Minimal DOM updates
- **Caching** - Static assets cached by browser

## Compliance Status Indicators

The dashboard uses a three-tier compliance system:

### ✅ Compliant (Green)
- **0 changes** detected from template
- No unauthorized modifications
- Ready for approval

### ⚠️ Minor Changes (Orange)
- **1-10 changes** detected
- Minor modifications requiring review
- May be acceptable with approval

### ❌ Major Changes (Red)
- **11+ changes** detected
- Significant modifications requiring thorough review
- Likely non-compliant with policies

## Usage Tips

### 📁 File Organization
- Keep templates in the `templates/` directory
- Use descriptive filenames for contracts
- Follow naming convention: `VENDOR_NAME_TYPE_VERSION.docx`

### 🔍 Analysis Workflow
1. **Upload templates** first if not already present
2. **Upload contracts** to analyze
3. **Run analysis** (automatic or manual)
4. **Review reports** and compliance status
5. **Download detailed reports** as needed

### 📊 Monitoring
- Check dashboard metrics regularly
- Monitor compliance rates over time
- Set up alerts for critical changes
- Review templates periodically

## Troubleshooting

### Common Issues

**Dashboard won't start:**
- Check if Flask is installed: `pip install flask`
- Ensure port 5000 is available
- Check for Python path issues

**No templates found:**
- Verify `.docx` files in `templates/` directory
- Check file permissions
- Ensure files are not corrupted

**Upload fails:**
- Check file size (max 16MB)
- Ensure file is `.docx` format
- Verify upload directory permissions

**Analysis errors:**
- Check template compatibility
- Verify contract file integrity
- Review error logs in console

### Getting Help

1. **Check logs** - Look for errors in browser console or terminal
2. **File permissions** - Ensure read/write access to directories
3. **Dependencies** - Verify all Python packages installed
4. **Sample data** - Use test contracts to verify functionality

## Technical Details

### Frontend Stack
- **HTML5** with semantic markup
- **CSS3** with modern features (Grid, Flexbox, Custom Properties)
- **Vanilla JavaScript** (ES6+) for interactivity
- **Font Awesome** for icons

### Backend Stack
- **Flask** web framework
- **Python 3.7+** runtime
- **python-docx** for document processing
- **Werkzeug** for file handling

### Browser Support
- **Chrome/Edge** 88+
- **Firefox** 85+
- **Safari** 14+
- **Mobile browsers** (iOS Safari, Chrome Mobile)

## Development

### Extending the Dashboard

To add new features:

1. **Frontend**: Modify `static/js/dashboard.js` and `static/css/dashboard.css`
2. **Backend**: Add routes to `dashboard_server.py`
3. **UI**: Update `dashboard.html` structure
4. **API**: Follow RESTful conventions for new endpoints

### Custom Styling

The dashboard uses CSS custom properties for easy theming:

```css
:root {
    --primary-color: #2563eb;
    --success-color: #059669;
    --warning-color: #d97706;
    --danger-color: #dc2626;
}
```

Modify these values in `static/css/dashboard.css` to customize colors.