#!/usr/bin/env python3
"""
Flask Web Application for Contract Analyzer
"""

from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
import os
import json
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
from contract_analyzer_demo import ContractAnalyzerDemo

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'docx'}

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('reports', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Initialize analyzer
analyzer = ContractAnalyzerDemo()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/templates')
def get_templates():
    """Get list of available templates"""
    templates = []
    template_dir = Path('templates')
    
    if template_dir.exists():
        for template_file in template_dir.glob('*.docx'):
            templates.append({
                'name': template_file.name,
                'size': template_file.stat().st_size,
                'modified': datetime.fromtimestamp(template_file.stat().st_mtime).isoformat()
            })
    
    return jsonify({
        'templates': templates,
        'count': len(templates)
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_contract():
    """Analyze a single contract"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only .docx files are allowed'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Analyze contract
        result = analyzer.analyze_contract(filepath, 'reports')
        
        if result:
            # Add additional info for frontend
            result['original_filename'] = filename
            result['upload_time'] = datetime.now().isoformat()
            result['report_url'] = url_for('download_report', filename=Path(result['report']).name)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'result': result
            })
        else:
            os.remove(filepath)
            return jsonify({
                'success': False,
                'error': 'Could not analyze contract. Please check if it contains proper vendor/type keywords.'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze-batch', methods=['POST'])
def analyze_batch():
    """Analyze multiple contracts"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files selected'}), 400
    
    results = []
    errors = []
    
    for file in files:
        if file and allowed_file(file.filename):
            try:
                # Save file
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                
                # Analyze
                result = analyzer.analyze_contract(filepath, 'reports')
                
                if result:
                    result['original_filename'] = filename
                    result['upload_time'] = datetime.now().isoformat()
                    result['report_url'] = url_for('download_report', filename=Path(result['report']).name)
                    results.append(result)
                else:
                    errors.append({
                        'filename': filename,
                        'error': 'Could not classify or analyze'
                    })
                
                # Clean up
                os.remove(filepath)
                
            except Exception as e:
                errors.append({
                    'filename': file.filename,
                    'error': str(e)
                })
        else:
            errors.append({
                'filename': file.filename,
                'error': 'Invalid file type'
            })
    
    # Generate summary
    summary = {
        'total_files': len(files),
        'successful': len(results),
        'failed': len(errors),
        'by_category': {},
        'by_template': {},
        'total_changes': 0
    }
    
    for result in results:
        # Count by category
        cat = result['category']
        if cat not in summary['by_category']:
            summary['by_category'][cat] = 0
        summary['by_category'][cat] += 1
        
        # Count by template
        tmpl = result['template']
        if tmpl not in summary['by_template']:
            summary['by_template'][tmpl] = {'count': 0, 'changes': 0}
        summary['by_template'][tmpl]['count'] += 1
        summary['by_template'][tmpl]['changes'] += result['changes']
        
        summary['total_changes'] += result['changes']
    
    return jsonify({
        'success': True,
        'results': results,
        'errors': errors,
        'summary': summary
    })

@app.route('/api/upload-template', methods=['POST'])
def upload_template():
    """Upload a new template"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Check filename format
    filename = secure_filename(file.filename)
    if not (filename.upper().startswith('VENDOR_') or filename.upper().startswith('TYPE_')):
        return jsonify({
            'error': 'Invalid template name. Must start with VENDOR_ or TYPE_'
        }), 400
    
    try:
        filepath = os.path.join('templates', filename)
        file.save(filepath)
        
        # Reload templates
        analyzer.load_templates()
        
        return jsonify({
            'success': True,
            'message': f'Template {filename} uploaded successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reports/<filename>')
def download_report(filename):
    """Download a generated report"""
    try:
        return send_file(
            os.path.join('reports', filename),
            as_attachment=True,
            download_name=filename
        )
    except FileNotFoundError:
        return jsonify({'error': 'Report not found'}), 404

@app.route('/api/stats')
def get_stats():
    """Get analysis statistics"""
    stats = {
        'templates_count': len(analyzer.templates),
        'reports_count': len(list(Path('reports').glob('*.docx'))) if Path('reports').exists() else 0,
        'categories': list(set(analyzer.vendor_keywords.values()) | set(analyzer.type_keywords.values()))
    }
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
