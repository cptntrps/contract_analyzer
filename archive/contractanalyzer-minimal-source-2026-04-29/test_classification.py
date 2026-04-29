#!/usr/bin/env python3
"""
Test the improved classification algorithm
"""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

try:
    from contract_analyzer import ContractAnalyzer
    
    # Initialize analyzer
    analyzer = ContractAnalyzer(use_ml=False)
    
    # Test with change order document
    contract_path = 'test_contracts/Contract_006_Generic_ChangeOrder_20240201.docx'
    
    print(f"Testing classification for: {contract_path}")
    
    # Extract text and classify
    text = analyzer.extract_text_from_docx(contract_path)
    if text:
        print(f"Extracted {len(text)} characters of text")
        category = analyzer.classify_document(text)
        print(f"Final classification: {category}")
    else:
        print("Failed to extract text")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
