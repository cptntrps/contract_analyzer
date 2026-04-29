# Contract Analyzer

An intelligent contract analysis tool that compares vendor contracts against approved templates to detect unauthorized changes.

## Features

- **Automatic Classification**: Identifies contract type and vendor from content
- **Template Matching**: Finds the best matching template for comparison
- **Change Detection**: Highlights all modifications from the approved template
- **Batch Processing**: Analyze multiple contracts simultaneously
- **Multiple Output Formats**: Terminal summary, inline view, and Word documents with tracked changes

## Quick Start

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install python-docx
```

For full ML-powered analysis (optional):
```bash
pip install -r requirements.txt
```

### 2. Generate Templates and Test Contracts

Use the provided prompt with any AI assistant:
```bash
cat generate_templates_and_contracts_prompt.md
```

This will help you create:
- 5 master templates (the approved versions)
- 20 test contracts (mix of compliant and non-compliant)

Place templates in the `templates/` directory.

### 3. Run Analysis

#### Demo Mode
```bash
python contract_analyzer_demo.py --demo
```

#### Single Contract
```bash
python contract_analyzer_demo.py Contract_001_Capgemini_SOW_20240115.docx
```

#### Batch Processing
```bash
python contract_analyzer_demo.py contracts/*.docx
```

## How It Works

1. **Text Extraction**: Skips title pages and metadata tables to focus on contract body
2. **Classification**: Identifies vendor (Capgemini, Blue Optima, EPAM) or type (SOW, Change Order)
3. **Template Matching**: Compares against relevant templates only
4. **Report Generation**: Creates detailed comparison showing all changes

## Expected Results

The analyzer will detect:
- ✅ Contracts that perfectly match templates (no unauthorized changes)
- ⚠️ Contracts with modifications (vendor changed terms)
- ❌ Contracts that don't match any template (unknown format)

## Output Files

- `reports/`: Generated directory containing comparison reports
- `reports/analysis_summary.json`: Generated batch processing summary with statistics
- `Comparison_Report_*.docx`: Generated individual contract comparison documents

Generated outputs are intentionally excluded from the source set. A fresh copy
only needs the Python/HTML/CSS/JS source files, `requirements*.txt`, the
`templates/` master documents, and the `test_contracts/` sample fixtures.

## Template Naming Convention

Templates must follow this pattern:
- `VENDOR_[NAME]_[TYPE]_[VERSION].docx`
- `TYPE_[TYPE]_[DESCRIPTION]_[VERSION].docx`

Examples:
- `VENDOR_CAPGEMINI_SOW_v1.docx`
- `TYPE_CHANGEORDER_Standard_v1.docx`
