# Column Names Update - Contract Analysis Reports

## Overview
The column names in all contract analysis reports have been updated as requested:

## Changes Made

### Previous Column Names:
- **"What was"** / **"Before"** / **"Original Text"** → **"Template"**
- **"How it got"** / **"After"** / **"New Text"** → **"Document"**  
- **"Why that matters"** / **"Explanation"** → **"Relevance"**

### New Column Names:
- **"Template"** - Content from the template document
- **"Document"** - Content from the contract document
- **"Relevance"** - Explanation of why the change matters

## Files Updated

### 1. Enhanced Report Generator (`enhanced_report_generator.py`)
- **Changes Table (.xlsx)**: Updated Excel headers to use new column names
- **Changes Table (.docx)**: Updated Word table headers to use new column names
- **Summary Report (.pdf)**: Added detailed tables by criticality with new column names
- **Summary Report (.docx)**: Added detailed tables by criticality with new column names
- **Review Document (.docx)**: Updated "BEFORE/AFTER" labels to "TEMPLATE/DOCUMENT"

### 2. Report Generator (`generate_reports.py`)
- **Comparison Table Report**: Updated table headers to use new column names
- **Text Analysis Report**: Updated BEFORE/AFTER labels to TEMPLATE/DOCUMENT
- **Template vs Contract Comparison**: Updated Contract label to Document

## New Report Structure

### Summary Report Enhanced Features
The Summary Report now includes a new section: **"Detailed Changes by Criticality"**

This section organizes changes into tables by criticality level:
- **Critical Changes** (Red theme)
- **Significant Changes** (Yellow theme)
- **Inconsequential Changes** (Green theme)

Each table contains:
- **#** - Change number
- **Template** - Original template content
- **Document** - Modified document content
- **Relevance** - Explanation of why the change matters

## Implementation Details

### Color Coding
- **Critical**: Red headers (#dc3545) with light red rows (#ffe6e6)
- **Significant**: Yellow headers (#ffc107) with light yellow rows (#fff4e6)
- **Inconsequential**: Green headers (#28a745) with light green rows (#e6f4ea)

### Text Truncation
- **Template/Document columns**: 100 characters max with "..." indicator
- **Relevance column**: 150 characters max with "..." indicator

### Styling
- **PDF Reports**: Professional table styling with ReportLab
- **Word Reports**: Table Grid style with color-coded headers
- **Excel Reports**: Structured data with color-coded cells

## Benefits

1. **Clearer Terminology**: "Template" and "Document" are more descriptive than "Before" and "After"
2. **Better Context**: "Relevance" explains why changes matter rather than just describing them
3. **Organized Structure**: Changes grouped by criticality for better analysis
4. **Visual Clarity**: Color coding helps identify risk levels quickly
5. **Consistent Naming**: All reports now use the same terminology

## Usage

The updated column names are automatically applied to all generated reports:
- Review Documents (.docx)
- Changes Tables (.xlsx and .docx)
- Summary Reports (.pdf and .docx)

Users will see the new column names in:
- Table headers
- Export files
- Dashboard displays
- Analysis reports

The changes maintain backward compatibility while providing clearer, more meaningful labels for contract analysis data. 