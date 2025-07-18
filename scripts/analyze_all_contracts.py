#!/usr/bin/env python3
"""
CLI script to analyze all contracts and demonstrate intelligent template matching.

This script will:
1. Load all contracts from the uploads directory
2. Apply intelligent template matching rules
3. Run analysis on each contract
4. Display results showing which templates were selected and why
"""

import sys
import os
from pathlib import Path
import requests
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

def analyze_all_contracts():
    """Analyze all contracts via the API and display results"""
    
    base_url = "http://localhost:5000/api"
    
    print("=" * 80)
    print("CONTRACT ANALYZER - BULK ANALYSIS WITH INTELLIGENT TEMPLATE MATCHING")
    print("=" * 80)
    print()
    
    # Get all contracts
    try:
        contracts_response = requests.get(f"{base_url}/contracts")
        contracts_response.raise_for_status()
        contracts_data = contracts_response.json()
        contracts = contracts_data.get('contracts', [])
    except Exception as e:
        print(f"❌ Error getting contracts: {e}")
        return
    
    print(f"📋 Found {len(contracts)} contracts to analyze")
    print()
    
    results = []
    
    for i, contract in enumerate(contracts, 1):
        contract_id = contract['id']
        contract_name = contract['filename']
        
        print(f"🔍 Analyzing {i}/{len(contracts)}: {contract_name}")
        print(f"   Contract ID: {contract_id}")
        
        # Analyze the contract
        try:
            analyze_response = requests.post(
                f"{base_url}/analyze-contract",
                json={'contract_id': contract_id},
                timeout=60
            )
            analyze_response.raise_for_status()
            result = analyze_response.json()
            
            if result.get('success'):
                analysis = result['result']
                
                # Extract key information
                template_used = analysis.get('template', 'Unknown')
                similarity = analysis.get('similarity', 0)
                changes = analysis.get('changes', 0)
                status = analysis.get('status', 'Unknown')
                
                print(f"   ✅ Template Selected: {template_used}")
                print(f"   📊 Similarity: {similarity}%")
                print(f"   📝 Changes: {changes}")
                print(f"   ⚠️  Status: {status}")
                
                # Determine template selection method
                if 'Capgemini' in contract_name and 'CAPGEMINI' in template_used:
                    selection_method = "🎯 Vendor Match (Capgemini)"
                elif 'BlueOptima' in contract_name and 'BLUEOPTIMA' in template_used:
                    selection_method = "🎯 Vendor Match (Blue Optima)"
                elif 'EPAM' in contract_name and 'EPAM' in template_used:
                    selection_method = "🎯 Vendor Match (EPAM)"
                elif 'ChangeOrder' in contract_name and 'CHANGEORDER' in template_used:
                    selection_method = "📄 Document Type Match (Change Order)"
                elif 'SOW' in contract_name and 'SOW' in template_used:
                    selection_method = "📄 Document Type Match (SOW)"
                else:
                    selection_method = "🔍 Similarity-Based Match"
                
                print(f"   🧠 Selection Method: {selection_method}")
                
                # Store result
                results.append({
                    'contract': contract_name,
                    'template': template_used,
                    'similarity': similarity,
                    'changes': changes,
                    'status': status,
                    'selection_method': selection_method
                })
                
                print("   ✅ Analysis completed successfully")
                
            else:
                print(f"   ❌ Analysis failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Error analyzing contract: {e}")
        
        print()
    
    # Display summary
    print("=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    print()
    
    # Group by template selection method
    method_counts = {}
    for result in results:
        method = result['selection_method']
        method_counts[method] = method_counts.get(method, 0) + 1
    
    print("📊 Template Selection Methods:")
    for method, count in sorted(method_counts.items()):
        print(f"   {method}: {count} contracts")
    print()
    
    # Show high/low similarity matches
    high_similarity = [r for r in results if r['similarity'] > 70]
    low_similarity = [r for r in results if r['similarity'] < 30]
    
    print(f"🎯 High Similarity Matches (>70%): {len(high_similarity)}")
    for result in high_similarity:
        print(f"   📈 {result['contract']} → {result['template']} ({result['similarity']}%)")
    
    print()
    print(f"⚠️  Low Similarity Matches (<30%): {len(low_similarity)}")
    for result in low_similarity:
        print(f"   📉 {result['contract']} → {result['template']} ({result['similarity']}%)")
    
    print()
    print("=" * 80)
    print("INTELLIGENT TEMPLATE MATCHING DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("🧠 The system applied these rules in order:")
    print("1. 🎯 Vendor-specific matching (Capgemini, Blue Optima, EPAM)")
    print("2. 📄 Document type matching (SOW vs Change Order)")
    print("3. 🔍 Similarity-based matching (best fit from all templates)")
    print()
    print("This ensures each contract is compared against the most appropriate template!")

if __name__ == "__main__":
    analyze_all_contracts()