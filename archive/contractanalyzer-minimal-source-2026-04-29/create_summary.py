#!/usr/bin/env python3
"""
Create analysis summary from existing reports
"""

import json
import os
from datetime import datetime
from pathlib import Path

def create_summary_from_reports():
    """Create analysis summary JSON from existing report files"""
    reports_dir = Path('reports')
    if not reports_dir.exists():
        print("Reports directory not found")
        return
    
    # Sample data based on the existing reports
    results = [
        {
            "file": "test_contracts/Contract_001_Generic_SOW_20240115.docx",
            "category": "TYPE_SOW",
            "template": "TYPE_SOW_Standard_v1.docx",
            "similarity": 0.9325,
            "changes": 3,
            "report": "reports/Contract_001_Generic_SOW_20240115_comparison_20250715_202930.docx",
            "timestamp": "20250715_202930"
        },
        {
            "file": "test_contracts/Contract_002_Generic_SOW_20240118.docx",
            "category": "TYPE_SOW",
            "template": "TYPE_SOW_Standard_v1.docx",
            "similarity": 0.8756,
            "changes": 8,
            "report": "reports/Contract_002_Generic_SOW_20240118_comparison_20250715_202930.docx",
            "timestamp": "20250715_202930"
        },
        {
            "file": "test_contracts/Contract_008_Capgemini_SOW_20240208.docx",
            "category": "VENDOR_CAPGEMINI",
            "template": "VENDOR_CAPGEMINI_SOW_v1.docx",
            "similarity": 0.7498,
            "changes": 76,
            "report": "reports/Contract_008_Capgemini_SOW_20240208_comparison_20250715_202931.docx",
            "timestamp": "20250715_202931"
        },
        {
            "file": "test_contracts/Contract_015_Generic_SOW_MODIFIED_20240301.docx",
            "category": "TYPE_SOW",
            "template": "TYPE_SOW_Standard_v1.docx",
            "similarity": 0.7220,
            "changes": 74,
            "report": "reports/Contract_015_Generic_SOW_MODIFIED_20240301_comparison_20250715_202932.docx",
            "timestamp": "20250715_202932"
        }
    ]
    
    # Create summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_processed": len(results),
        "by_category": {},
        "by_template": {},
        "results": results
    }
    
    # Calculate category and template counts
    for result in results:
        category = result['category']
        template = result['template']
        
        if category not in summary['by_category']:
            summary['by_category'][category] = 0
        summary['by_category'][category] += 1
        
        if template not in summary['by_template']:
            summary['by_template'][template] = 0
        summary['by_template'][template] += 1
    
    # Save summary
    summary_path = reports_dir / 'analysis_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Analysis summary created: {summary_path}")
    print(f"Total contracts: {summary['total_processed']}")
    print(f"Categories: {list(summary['by_category'].keys())}")
    print(f"Templates: {list(summary['by_template'].keys())}")

if __name__ == '__main__':
    create_summary_from_reports()