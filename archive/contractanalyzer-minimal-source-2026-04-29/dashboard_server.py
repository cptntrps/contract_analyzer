#!/usr/bin/env python3
"""
Flask server for Contract Analyzer Dashboard
Provides web interface for contract analysis and management
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import docx

from contract_analyzer import ContractAnalyzer

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEMPLATES_FOLDER'] = 'templates'
app.config['REPORTS_FOLDER'] = 'reports'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure required directories exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['TEMPLATES_FOLDER'], app.config['REPORTS_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Initialize contract analyzer with exact text comparison (like Word)
print("Initializing Text-based Contract Analyzer (like Word track changes)...")
try:
    analyzer = ContractAnalyzer(template_dir=app.config['TEMPLATES_FOLDER'], use_ml=False)
    print("✅ Text-based analyzer initialized successfully")
except Exception as e:
    print(f"⚠️  Text analyzer initialization failed, falling back to demo version: {e}")
    from contract_analyzer_demo import ContractAnalyzerDemo
    analyzer = ContractAnalyzerDemo(template_dir=app.config['TEMPLATES_FOLDER'])

@app.route('/')
def dashboard():
    """Serve the main dashboard page"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files (CSS, JS, images)"""
    return send_from_directory('static', filename)

# ===== API Routes =====

@app.route('/api/analysis-results')
def get_analysis_results():
    """Get all contract analysis results"""
    try:
        # Read analysis summary if it exists
        summary_path = Path(app.config['REPORTS_FOLDER']) / 'analysis_summary.json'
        if summary_path.exists():
            with open(summary_path, 'r') as f:
                data = json.load(f)
                
            # Add compliance status to each result
            for result in data.get('results', []):
                result['status'] = get_compliance_status(result.get('changes', 0))
                
            return jsonify(data.get('results', []))
        else:
            return jsonify([])
    except Exception as e:
        app.logger.error(f"Error loading analysis results: {e}")
        return jsonify([])

@app.route('/api/templates')
def get_templates():
    """Get all available templates"""
    try:
        templates = []
        template_dir = Path(app.config['TEMPLATES_FOLDER'])
        
        for template_file in template_dir.glob('*.docx'):
            stat = template_file.stat()
            template_type = 'Vendor Specific' if template_file.name.startswith('VENDOR_') else 'Document Type'
            
            templates.append({
                'name': template_file.name,
                'type': template_type,
                'lastModified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d'),
                'size': format_file_size(stat.st_size)
            })
            
        return jsonify(templates)
    except Exception as e:
        app.logger.error(f"Error loading templates: {e}")
        return jsonify([])

@app.route('/api/contracts')
def get_contracts():
    """Get all uploaded contracts"""
    try:
        contracts = []
        upload_dir = Path(app.config['UPLOAD_FOLDER'])
        
        # Also check test_contracts directory
        test_contracts_dir = Path('test_contracts')
        
        for contracts_dir in [upload_dir, test_contracts_dir]:
            if contracts_dir.exists():
                for contract_file in contracts_dir.glob('*.docx'):
                    stat = contract_file.stat()
                    
                    # Check if this contract has been analyzed
                    analysis_status = 'pending'
                    summary_path = Path(app.config['REPORTS_FOLDER']) / 'analysis_summary.json'
                    if summary_path.exists():
                        with open(summary_path, 'r') as f:
                            data = json.load(f)
                        
                        # Check if this file appears in results
                        for result in data.get('results', []):
                            if contract_file.name in result.get('file', ''):
                                analysis_status = 'analyzed'
                                break
                    
                    contracts.append({
                        'name': contract_file.name,
                        'uploadDate': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d'),
                        'status': analysis_status,
                        'size': format_file_size(stat.st_size),
                        'path': str(contract_file)
                    })
                    
        return jsonify(contracts)
    except Exception as e:
        app.logger.error(f"Error loading contracts: {e}")
        return jsonify([])

@app.route('/api/upload-contract', methods=['POST'])
def upload_contract():
    """Upload a new contract file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        app.logger.error(f"Error uploading contract: {e}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/api/upload-template', methods=['POST'])
def upload_template():
    """Upload a new template file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['TEMPLATES_FOLDER'], filename)
            file.save(filepath)
            
            # Reload analyzer templates
            analyzer.load_templates()
            
            return jsonify({
                'message': 'Template uploaded successfully',
                'filename': filename
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        app.logger.error(f"Error uploading template: {e}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/api/analyze-contract', methods=['POST'])
def analyze_contract():
    """Analyze a specific contract"""
    try:
        data = request.get_json()
        contract_name = data.get('contract_name')
        
        if not contract_name:
            return jsonify({'error': 'Contract name required'}), 400
            
        # Find the contract file
        contract_path = None
        for search_dir in [app.config['UPLOAD_FOLDER'], 'test_contracts']:
            potential_path = Path(search_dir) / contract_name
            if potential_path.exists():
                contract_path = str(potential_path)
                break
                
        if not contract_path:
            return jsonify({'error': 'Contract file not found'}), 404
            
        # Analyze the contract
        result = analyzer.analyze_single_contract(contract_path, app.config['REPORTS_FOLDER'])
        
        if result:
            # Update summary file with this single result
            summary_path = Path(app.config['REPORTS_FOLDER']) / 'analysis_summary.json'
            update_analysis_summary(result, summary_path)
            
            # Convert AnalysisResult dataclass to dict
            result_dict = {
                'file': result.input_file,
                'category': result.category,
                'template': result.matched_template,
                'similarity': result.similarity_score,
                'changes': result.differences_count,
                'report': result.report_path,
                'timestamp': result.timestamp,
                'status': get_compliance_status(result.differences_count)
            }
            return jsonify({
                'message': 'Analysis completed successfully',
                'result': result_dict
            })
        else:
            return jsonify({'error': 'Analysis failed'}), 500
            
    except Exception as e:
        app.logger.error(f"Error analyzing contract: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@app.route('/download-report')
def download_report():
    """Download a specific analysis report"""
    try:
        report_path = request.args.get('path')
        if not report_path:
            return jsonify({'error': 'Report path required'}), 400
            
        # Security check - ensure path is within reports directory
        full_path = Path(report_path)
        if full_path.exists() and 'reports' in str(full_path):
            return send_file(full_path, as_attachment=True, download_name=full_path.name)
        else:
            return jsonify({'error': 'Report not found'}), 404
            
    except Exception as e:
        app.logger.error(f"Error downloading report: {e}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/view-report')
def view_report():
    """Provide information about viewing reports"""
    try:
        report_path = request.args.get('path')
        if not report_path:
            return jsonify({'error': 'Report path required'}), 400
            
        # Security check - ensure path is within reports directory  
        full_path = Path(report_path)
        if not full_path.exists() or 'reports' not in str(full_path):
            return jsonify({'error': 'Report not found'}), 404
            
        # Get file info
        file_stat = full_path.stat()
        file_size = format_file_size(file_stat.st_size)
        modified_time = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Contract Analysis Report - {full_path.name}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 800px; margin: 0 auto; padding: 40px 20px; background: #f8fafc; }}
                .container {{ background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .header h1 {{ color: #2563eb; margin-bottom: 10px; }}
                .header p {{ color: #64748b; font-size: 18px; }}
                .info-card {{ background: #f1f5f9; padding: 30px; border-radius: 8px; margin: 30px 0; }}
                .info-item {{ display: flex; justify-content: space-between; margin: 15px 0; padding: 10px 0; border-bottom: 1px solid #e2e8f0; }}
                .info-item:last-child {{ border-bottom: none; }}
                .info-label {{ font-weight: 600; color: #374151; }}
                .info-value {{ color: #6b7280; }}
                .warning-box {{ background: #fef3c7; border: 1px solid #f59e0b; padding: 20px; border-radius: 8px; margin: 30px 0; }}
                .warning-box h3 {{ color: #d97706; margin-top: 0; }}
                .action-buttons {{ text-align: center; margin: 40px 0; }}
                .btn {{ display: inline-block; padding: 12px 24px; margin: 0 10px; border-radius: 6px; text-decoration: none; font-weight: 600; transition: all 0.3s; }}
                .btn-primary {{ background: #2563eb; color: white; }}
                .btn-primary:hover {{ background: #1d4ed8; }}
                .btn-secondary {{ background: #6b7280; color: white; }}
                .btn-secondary:hover {{ background: #4b5563; }}
                .close-btn {{ position: fixed; top: 20px; right: 20px; background: #dc2626; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
                .track-changes-info {{ background: #ecfdf5; border: 1px solid #10b981; padding: 20px; border-radius: 8px; margin: 30px 0; }}
                .track-changes-info h3 {{ color: #059669; margin-top: 0; }}
                .feature-list {{ list-style: none; padding: 0; }}
                .feature-list li {{ padding: 8px 0; }}
                .feature-list li:before {{ content: "✓ "; color: #10b981; font-weight: bold; }}
            </style>
        </head>
        <body>
            <button class="close-btn" onclick="window.close()">✕</button>
            
            <div class="container">
                <div class="header">
                    <h1>📄 Contract Analysis Report</h1>
                    <p>Professional Word Document with Track Changes</p>
                </div>
                
                <div class="info-card">
                    <div class="info-item">
                        <span class="info-label">Report File:</span>
                        <span class="info-value">{full_path.name}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">File Size:</span>
                        <span class="info-value">{file_size}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Generated:</span>
                        <span class="info-value">{modified_time}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Format:</span>
                        <span class="info-value">Microsoft Word Document (.docx)</span>
                    </div>
                </div>
                
                <div class="track-changes-info">
                    <h3>📝 Professional Track Changes Report</h3>
                    <p>This document contains advanced Word formatting with track changes that shows:</p>
                    <ul class="feature-list">
                        <li>Red strikethrough text for content removed from template</li>
                        <li>Green underlined text for content added to contract</li>
                        <li>Professional compliance assessment</li>
                        <li>Detailed change summary and statistics</li>
                        <li>Word's native track changes for legal review</li>
                    </ul>
                </div>
                
                <div class="warning-box">
                    <h3>⚠️ Why Download Instead of Browser View?</h3>
                    <p>This report uses Microsoft Word's advanced track changes formatting that cannot be accurately displayed in a web browser. The download provides:</p>
                    <ul>
                        <li><strong>Full formatting preservation</strong> - All colors, fonts, and track changes intact</li>
                        <li><strong>Legal compliance</strong> - Proper document formatting for official review</li>
                        <li><strong>Interactive features</strong> - Accept/reject changes in Word</li>
                        <li><strong>Print-ready format</strong> - Professional document layout</li>
                    </ul>
                </div>
                
                <div class="action-buttons">
                    <a href="/download-report?path={report_path}" class="btn btn-primary">
                        📥 Download Full Report (.docx)
                    </a>
                    <button onclick="window.close()" class="btn btn-secondary">
                        ← Back to Dashboard
                    </button>
                </div>
                
                <div style="text-align: center; margin-top: 40px; color: #9ca3af; font-size: 14px;">
                    <p>💡 <strong>Tip:</strong> The downloaded Word document will show exact differences between the approved template and submitted contract with professional track changes formatting.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        app.logger.error(f"Error viewing report: {e}")
        return f"<html><body><h1>Error</h1><p>Could not load report: {e}</p></body></html>", 500

@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    """Analyze multiple contracts in batch"""
    try:
        data = request.get_json()
        contract_files = data.get('contracts', [])
        
        if not contract_files:
            return jsonify({'error': 'No contracts specified'}), 400
            
        # Collect contract paths
        contract_paths = []
        for contract_name in contract_files:
            contract_path = None
            for search_dir in [app.config['UPLOAD_FOLDER'], 'test_contracts']:
                potential_path = Path(search_dir) / contract_name
                if potential_path.exists():
                    contract_path = str(potential_path)
                    break
            if contract_path:
                contract_paths.append(contract_path)
        
        if not contract_paths:
            return jsonify({'error': 'No valid contract files found'}), 400
            
        # Run batch analysis
        analysis_results = analyzer.analyze_batch(contract_paths, app.config['REPORTS_FOLDER'])
        
        # Generate and save summary
        summary_path = Path(app.config['REPORTS_FOLDER']) / 'analysis_summary.json'
        analyzer.generate_batch_summary(analysis_results, str(summary_path))
        
        # Convert results to dict format for response
        results = []
        for result in analysis_results:
            result_dict = {
                'file': result.input_file,
                'category': result.category,
                'template': result.matched_template,
                'similarity': result.similarity_score,
                'changes': result.differences_count,
                'report': result.report_path,
                'timestamp': result.timestamp,
                'status': get_compliance_status(result.differences_count)
            }
            results.append(result_dict)
                    
        return jsonify({
            'message': f'Batch analysis completed for {len(results)} contracts',
            'results': results
        })
        
    except Exception as e:
        app.logger.error(f"Error in batch analysis: {e}")
        return jsonify({'error': 'Batch analysis failed'}), 500

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """Clear analysis cache and reports"""
    try:
        import shutil
        import glob
        
        cleared_items = []
        
        # Clear analysis summary
        summary_path = Path(app.config['REPORTS_FOLDER']) / 'analysis_summary.json'
        if summary_path.exists():
            summary_path.unlink()
            cleared_items.append('Analysis summary')
            
        # Clear all report files
        reports_dir = Path(app.config['REPORTS_FOLDER'])
        if reports_dir.exists():
            report_files = list(reports_dir.glob('*.docx'))
            for report_file in report_files:
                report_file.unlink()
            if report_files:
                cleared_items.append(f'{len(report_files)} report files')
                
        # Clear uploaded contracts (optional - you might want to keep these)
        # upload_dir = Path(app.config['UPLOAD_FOLDER'])
        # if upload_dir.exists():
        #     upload_files = list(upload_dir.glob('*.docx'))
        #     for upload_file in upload_files:
        #         upload_file.unlink()
        #     if upload_files:
        #         cleared_items.append(f'{len(upload_files)} uploaded contracts')
        
        if cleared_items:
            message = f"Cleared: {', '.join(cleared_items)}"
        else:
            message = "No cache items found to clear"
            
        return jsonify({
            'message': message,
            'cleared_items': cleared_items
        })
        
    except Exception as e:
        app.logger.error(f"Error clearing cache: {e}")
        return jsonify({'error': f'Failed to clear cache: {str(e)}'}), 500

@app.route('/api/dashboard-stats')
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get analysis results
        summary_path = Path(app.config['REPORTS_FOLDER']) / 'analysis_summary.json'
        analysis_data = []
        
        if summary_path.exists():
            with open(summary_path, 'r') as f:
                data = json.load(f)
                analysis_data = data.get('results', [])
        
        # Calculate statistics
        total_analyzed = len(analysis_data)
        compliant_count = len([r for r in analysis_data if get_compliance_status(r.get('changes', 0)) == 'compliant'])
        warning_count = len([r for r in analysis_data if get_compliance_status(r.get('changes', 0)) == 'warning'])
        critical_count = len([r for r in analysis_data if get_compliance_status(r.get('changes', 0)) == 'critical'])
        
        compliance_rate = round((compliant_count / total_analyzed * 100)) if total_analyzed > 0 else 0
        
        # Get template count
        template_count = len(list(Path(app.config['TEMPLATES_FOLDER']).glob('*.docx')))
        
        return jsonify({
            'totalAnalyzed': total_analyzed,
            'complianceRate': compliance_rate,
            'compliantCount': compliant_count,
            'warningCount': warning_count,
            'criticalCount': critical_count,
            'templateCount': template_count
        })
        
    except Exception as e:
        app.logger.error(f"Error getting dashboard stats: {e}")
        return jsonify({'error': 'Failed to get statistics'}), 500

# ===== Utility Functions =====

def update_analysis_summary(new_result, summary_path):
    """Update analysis summary with a new result"""
    try:
        # Load existing summary or create new one
        if summary_path.exists():
            with open(summary_path, 'r') as f:
                summary = json.load(f)
        else:
            summary = {
                "timestamp": datetime.now().isoformat(),
                "total_processed": 0,
                "by_category": {},
                "by_template": {},
                "results": []
            }
        
        # Remove any existing result for the same file
        summary['results'] = [r for r in summary['results'] if r.get('file') != new_result.input_file]
        
        # Add new result
        summary['results'].append({
            "file": new_result.input_file,
            "category": new_result.category,
            "template": new_result.matched_template,
            "similarity": new_result.similarity_score,
            "changes": new_result.differences_count,
            "report": new_result.report_path,
            "timestamp": new_result.timestamp
        })
        
        # Update counts
        summary['total_processed'] = len(summary['results'])
        summary['timestamp'] = datetime.now().isoformat()
        
        # Recalculate category and template counts
        summary['by_category'] = {}
        summary['by_template'] = {}
        for result in summary['results']:
            category = result['category']
            template = result['template']
            
            if category not in summary['by_category']:
                summary['by_category'][category] = 0
            summary['by_category'][category] += 1
            
            if template not in summary['by_template']:
                summary['by_template'][template] = 0
            summary['by_template'][template] += 1
        
        # Save updated summary
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
            
    except Exception as e:
        app.logger.error(f"Error updating analysis summary: {e}")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'docx'

def get_compliance_status(changes):
    """Get compliance status based on number of changes"""
    if changes == 0:
        return 'compliant'
    elif changes <= 10:
        return 'warning'
    else:
        return 'critical'

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

# ===== Error Handlers =====

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def too_large_error(error):
    return jsonify({'error': 'File too large'}), 413

# ===== Main =====

if __name__ == '__main__':
    # Check if Flask is available
    try:
        print("Starting Contract Analyzer Dashboard...")
        print(f"Templates loaded: {len(analyzer.templates)}")
        print("Dashboard will be available at: http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to prevent double initialization
        )
    except ImportError:
        print("Flask not installed. Install with: pip install flask")
        print("Or use the simple dashboard by opening dashboard.html directly in a browser")
    except Exception as e:
        print(f"Error starting server: {e}")
        print("You can still use the dashboard by opening dashboard.html directly in a browser")
