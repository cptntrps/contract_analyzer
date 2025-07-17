"""
Dashboard Server for Contract Analyzer
Enhanced with configuration management and security features
"""

import os
import json
import datetime
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from flask import Flask, request, jsonify, send_file, render_template

# Import enhanced modules
from config import config
from security import (
    validate_file_upload, validate_path, sanitize_input, 
    audit_security_event, get_security_headers,
    FileValidationError, PathTraversalError, ContentValidationError
)
from analyzer import ContractAnalyzer
from llm_handler import LLMHandler
from enhanced_report_generator import EnhancedReportGenerator
from user_config_manager import user_config
from llm_providers import create_llm_provider

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DashboardServer:
    """
    Main dashboard server for Contract Analyzer application.
    
    Provides a Flask-based web interface for contract analysis,
    template management, and report generation with enhanced
    security features and configuration management.
    """
    
    def __init__(self):
        """Initialize the Dashboard Server with Flask app and components."""
        self.app = Flask(__name__, 
                        template_folder=config.TEMPLATE_FOLDER, 
                        static_folder=config.STATIC_FOLDER)
        
        # Configure Flask app from config
        self.app.config.update({
            'SECRET_KEY': config.SECRET_KEY,
            'UPLOAD_FOLDER': config.UPLOAD_FOLDER,
            'TEMPLATES_FOLDER': config.TEMPLATES_FOLDER,
            'REPORTS_FOLDER': config.REPORTS_FOLDER,
            'MAX_CONTENT_LENGTH': config.MAX_CONTENT_LENGTH,
            'DEBUG': config.DEBUG,
            'ENV': config.ENV
        })
        
        # Validate configuration
        config_errors = config.validate_config()
        if config_errors:
            logger.error(f"Configuration validation failed: {config_errors}")
            raise ValueError(f"Invalid configuration: {config_errors}")
        
        # Initialize components
        self.analyzer = ContractAnalyzer()
        self.llm_handler = LLMHandler()
        self.report_generator = EnhancedReportGenerator()
        
        # Create directories
        self.ensure_directories()
        
        # Setup routes
        self.setup_routes()
        
        # In-memory storage for demo (use database in production)
        self.analysis_results = []
        self.contracts = []
        self.templates = []
        
        # Load existing data
        self.load_existing_data()
        
        # Log startup
        logger.info(f"Dashboard server initialized with config: {config.get_summary()}")
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.app.config['UPLOAD_FOLDER'],
            self.app.config['TEMPLATES_FOLDER'],
            self.app.config['REPORTS_FOLDER']
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.debug(f"Directory ensured: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                raise
    
    def add_security_headers(self, response):
        """Add security headers to response"""
        headers = get_security_headers()
        for header, value in headers.items():
            response.headers[header] = value
        return response
    
    def create_error_response(self, message: str, status_code: int = 500, additional_data: Optional[Dict] = None):
        """Create standardized error response"""
        error_data = {
            'success': False,
            'error': message,
            'status_code': status_code
        }
        if additional_data:
            error_data.update(additional_data)
        return jsonify(error_data), status_code
    
    def create_success_response(self, data: Optional[Dict] = None, message: Optional[str] = None):
        """Create standardized success response"""
        response_data = {'success': True}
        if data:
            response_data.update(data)
        if message:
            response_data['message'] = message
        return jsonify(response_data), 200
    
    def load_existing_data(self):
        """Load existing contracts and templates from filesystem"""
        try:
            # Load contracts
            contracts_dir = Path(self.app.config['UPLOAD_FOLDER'])
            if contracts_dir.exists():
                for contract_file in contracts_dir.glob('*.docx'):
                    contract_info = {
                        'id': contract_file.stem,
                        'name': contract_file.name,
                        'type': self.determine_contract_type(contract_file.name),
                        'size': self.format_file_size(contract_file.stat().st_size),
                        'uploaded': contract_file.stat().st_mtime,
                        'status': 'pending',
                        'path': str(contract_file)
                    }
                    self.contracts.append(contract_info)

            # Load templates
            templates_dir = Path(self.app.config['TEMPLATES_FOLDER'])
            if templates_dir.exists():
                for template_file in templates_dir.glob('*.docx'):
                    template_info = {
                        'id': template_file.stem,
                        'name': template_file.name,
                        'category': self.determine_template_category(template_file.name),
                        'version': '1.0',
                        'lastModified': template_file.stat().st_mtime,
                        'path': str(template_file)
                    }
                    self.templates.append(template_info)

            # Load analysis results if they exist
            results_file = Path('analysis_results.json')
            if results_file.exists():
                try:
                    with open(results_file, 'r') as f:
                        self.analysis_results = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load analysis results: {e}")
                    self.analysis_results = []

            logger.info(f"Loaded {len(self.contracts)} contracts, {len(self.templates)} templates, {len(self.analysis_results)} analysis results")

        except Exception as e:
            logger.error(f"Error loading existing data: {e}")
            # Don't raise exception, just log and continue with empty data
    
    def setup_routes(self):
        """Setup all Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('dashboard.html')
        
        @self.app.route('/api/health')
        def health_check():
            """Health check endpoint"""
            try:
                health_status = self.llm_handler.get_health_status()
                return jsonify(health_status), 200
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return self.create_error_response(str(e), 500, {'status': 'error'})
        
        @self.app.route('/api/available-models')
        def get_available_models():
            """Get list of available LLM models"""
            try:
                models = self.llm_handler.get_available_models()
                return jsonify({
                    'success': True,
                    'models': models,
                    'current_model': self.llm_handler.get_current_model()
                }), 200
            except Exception as e:
                logger.error(f"Failed to get available models: {e}")
                return self.create_error_response(str(e), 500, {'models': []})
        
        @self.app.route('/api/change-model', methods=['POST'])
        def change_model():
            """Change the current LLM model"""
            try:
                data = request.get_json()
                if not data or 'model' not in data:
                    return jsonify({
                        'success': False,
                        'message': 'Model name is required'
                    }), 400
                
                new_model = sanitize_input(data['model'])
                result = self.llm_handler.change_model(new_model)
                
                # Log the model change for audit
                audit_security_event('model_changed', {
                    'previous_model': result.get('previous_model'),
                    'new_model': result.get('current_model'),
                    'success': result.get('success', False),
                    'user_ip': request.remote_addr
                })
                
                status_code = 200 if result['success'] else 400
                return jsonify(result), status_code
                
            except Exception as e:
                logger.error(f"Model change failed: {e}")
                return jsonify({
                    'success': False,
                    'message': str(e),
                    'current_model': self.llm_handler.get_current_model()
                }), 500
        
        @self.app.route('/api/model-info')
        def get_model_info():
            """Get detailed information about the current model"""
            try:
                model_info = self.llm_handler.get_model_info()
                return jsonify(model_info), 200
            except Exception as e:
                logger.error(f"Failed to get model info: {e}")
                return jsonify({
                    'name': self.llm_handler.get_current_model(),
                    'error': str(e)
                }), 500

        @self.app.route('/api/user-config')
        def get_user_config():
            """Get user configuration settings"""
            try:
                config_data = user_config.get_all_settings()
                return jsonify({
                    'success': True,
                    'config': config_data
                }), 200
            except Exception as e:
                logger.error(f"Failed to get user config: {e}")
                return self.create_error_response(str(e), 500)

        @self.app.route('/api/user-config', methods=['POST'])
        def update_user_config():
            """Update user configuration settings"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'success': False, 'error': 'No data provided'}), 400
                
                # Update specific settings
                for section, settings in data.items():
                    if isinstance(settings, dict):
                        for key, value in settings.items():
                            user_config.set_setting(section, key, value)
                
                # Audit log
                audit_security_event('config_updated', {
                    'sections': list(data.keys()),
                    'user_ip': request.remote_addr
                })
                
                return jsonify({
                    'success': True,
                    'message': 'Configuration updated successfully'
                }), 200
                
            except Exception as e:
                logger.error(f"Failed to update user config: {e}")
                return self.create_error_response(str(e), 500)

        @self.app.route('/api/openai-models')
        def get_openai_models():
            """Get available OpenAI models with descriptions"""
            try:
                # Create a temporary OpenAI provider to get model info
                provider_config = user_config.get_llm_config()
                if provider_config.get('provider') == 'openai' and provider_config.get('api_key'):
                    provider = create_llm_provider('openai', provider_config)
                    models = provider.get_available_models()
                    recommendations = provider.get_model_recommendations()
                    
                    return jsonify({
                        'success': True,
                        'models': models,
                        'recommendations': recommendations,
                        'current_model': user_config.get_openai_model()
                    }), 200
                else:
                    # Return static model info if no API key
                    from llm_providers import OpenAIProvider
                    models = []
                    for model_key, model_info in OpenAIProvider.AVAILABLE_MODELS.items():
                        models.append({
                            'name': model_info['name'],
                            'description': model_info['description'],
                            'context_window': model_info['context_window'],
                            'recommended': model_info['recommended'],
                            'tier': model_info['tier'],
                            'current': model_info['name'] == user_config.get_openai_model(),
                            'provider': 'openai'
                        })
                    
                    return jsonify({
                        'success': True,
                        'models': models,
                        'current_model': user_config.get_openai_model(),
                        'api_key_required': True
                    }), 200
                    
            except Exception as e:
                logger.error(f"Failed to get OpenAI models: {e}")
                return self.create_error_response(str(e), 500)

        @self.app.route('/api/update-openai-model', methods=['POST'])
        def update_openai_model():
            """Update the OpenAI model selection"""
            try:
                data = request.get_json()
                if not data or 'model' not in data:
                    return jsonify({'success': False, 'error': 'Model name is required'}), 400
                
                new_model = sanitize_input(data['model'])
                
                # Validate model
                from llm_providers import OpenAIProvider
                if new_model not in OpenAIProvider.AVAILABLE_MODELS:
                    return jsonify({
                        'success': False,
                        'error': f'Invalid model: {new_model}',
                        'available_models': list(OpenAIProvider.AVAILABLE_MODELS.keys())
                    }), 400
                
                # Update the model
                success = user_config.update_openai_model(new_model)
                
                if success:
                    # Audit log
                    audit_security_event('openai_model_changed', {
                        'new_model': new_model,
                        'user_ip': request.remote_addr
                    })
                    
                    return jsonify({
                        'success': True,
                        'message': f'Model updated to {new_model}',
                        'model': new_model
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to update model'
                    }), 500
                    
            except Exception as e:
                logger.error(f"Failed to update OpenAI model: {e}")
                return self.create_error_response(str(e), 500)

        @self.app.route('/api/llm-provider')
        def get_llm_provider():
            """Get current LLM provider and configuration"""
            try:
                provider_config = user_config.get_llm_config()
                
                return jsonify({
                    'success': True,
                    'provider': provider_config.get('provider', 'openai'),
                    'model': provider_config.get('model', 'gpt-4o'),
                    'temperature': provider_config.get('temperature', 0.1),
                    'max_tokens': provider_config.get('max_tokens', 1024),
                    'api_key_configured': bool(provider_config.get('api_key'))
                }), 200
                
            except Exception as e:
                logger.error(f"Failed to get LLM provider info: {e}")
                return self.create_error_response(str(e), 500)

        @self.app.route('/api/update-llm-settings', methods=['POST'])
        def update_llm_settings():
            """Update LLM settings like temperature and max tokens"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'success': False, 'error': 'No data provided'}), 400
                
                updated_settings = {}
                
                # Update temperature
                if 'temperature' in data:
                    temp = float(data['temperature'])
                    if user_config.update_temperature(temp):
                        updated_settings['temperature'] = temp
                
                # Update max tokens
                if 'max_tokens' in data:
                    max_tokens = int(data['max_tokens'])
                    if user_config.update_max_tokens(max_tokens):
                        updated_settings['max_tokens'] = max_tokens
                
                # Audit log
                audit_security_event('llm_settings_updated', {
                    'settings': updated_settings,
                    'user_ip': request.remote_addr
                })
                
                return jsonify({
                    'success': True,
                    'message': 'LLM settings updated successfully',
                    'updated_settings': updated_settings
                }), 200
                
            except Exception as e:
                logger.error(f"Failed to update LLM settings: {e}")
                return self.create_error_response(str(e), 500)

        @self.app.route('/api/config-validation')
        def validate_user_config():
            """Validate current user configuration"""
            try:
                validation_result = user_config.validate_config()
                return jsonify({
                    'success': True,
                    'validation': validation_result
                }), 200
                
            except Exception as e:
                logger.error(f"Failed to validate config: {e}")
                return self.create_error_response(str(e), 500)

        @self.app.route('/api/contracts')
        def get_contracts():
            """Get list of available contracts"""
            try:
                return jsonify(self.contracts), 200
            except Exception as e:
                logger.error(f"Failed to get contracts: {e}")
                return jsonify([]), 500

        @self.app.route('/api/templates')
        def get_templates():
            """Get list of available templates"""
            try:
                return jsonify(self.templates), 200
            except Exception as e:
                logger.error(f"Failed to get templates: {e}")
                return jsonify([]), 500

        @self.app.route('/api/analysis-results')
        def get_analysis_results():
            """Get list of analysis results"""
            try:
                return jsonify(self.analysis_results), 200
            except Exception as e:
                logger.error(f"Failed to get analysis results: {e}")
                return jsonify([]), 500

        @self.app.route('/api/upload-contract', methods=['POST'])
        def upload_contract():
            """Upload a new contract"""
            try:
                if 'file' not in request.files:
                    return jsonify({'error': 'No file provided'}), 400
                
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                # Security validation
                try:
                    validate_file_upload(file)
                except (FileValidationError, ContentValidationError) as e:
                    return jsonify({'error': str(e)}), 400
                
                # Save file securely
                filename = secure_filename(file.filename)
                file_path = os.path.join(config.UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                # Create contract entry
                contract = {
                    'id': f"Contract_{len(self.contracts)+1:03d}",
                    'name': filename,
                    'path': file_path,
                    'uploaded_at': datetime.datetime.now().isoformat(),
                    'size': os.path.getsize(file_path)
                }
                
                self.contracts.append(contract)
                
                # Audit log
                audit_security_event('contract_uploaded', {
                    'filename': filename,
                    'size': contract['size'],
                    'user_ip': request.remote_addr
                })
                
                return jsonify({
                    'success': True,
                    'message': 'Contract uploaded successfully',
                    'contract': contract
                }), 200
                
            except Exception as e:
                logger.error(f"Contract upload failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/upload-template', methods=['POST'])
        def upload_template():
            """Upload a new template"""
            try:
                if 'file' not in request.files:
                    return jsonify({'error': 'No file provided'}), 400
                
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                # Security validation
                try:
                    validate_file_upload(file)
                except (FileValidationError, ContentValidationError) as e:
                    return jsonify({'error': str(e)}), 400
                
                # Save file securely
                filename = secure_filename(file.filename)
                file_path = os.path.join(config.TEMPLATES_FOLDER, filename)
                file.save(file_path)
                
                # Create template entry
                template = {
                    'id': f"Template_{len(self.templates)+1:03d}",
                    'name': filename,
                    'path': file_path,
                    'uploaded_at': datetime.datetime.now().isoformat(),
                    'size': os.path.getsize(file_path)
                }
                
                self.templates.append(template)
                
                # Audit log
                audit_security_event('template_uploaded', {
                    'filename': filename,
                    'size': template['size'],
                    'user_ip': request.remote_addr
                })
                
                return jsonify({
                    'success': True,
                    'message': 'Template uploaded successfully',
                    'template': template
                }), 200
                
            except Exception as e:
                logger.error(f"Template upload failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/analyze-contract', methods=['POST'])
        def analyze_contract():
            """Analyze a contract against templates"""
            try:
                data = request.get_json()
                if not data or 'contract_id' not in data:
                    return jsonify({'error': 'Contract ID is required'}), 400
                
                contract_id = sanitize_input(data['contract_id'])
                
                # Find contract
                contract = next((c for c in self.contracts if c['id'] == contract_id), None)
                if not contract:
                    return jsonify({'error': 'Contract not found'}), 404
                
                # Run analysis
                result = self.run_contract_analysis(contract)
                self.analysis_results.append(result)
                
                # Audit log
                audit_security_event('contract_analyzed', {
                    'contract_id': contract_id,
                    'result_id': result['id']
                })
                
                return jsonify({
                    'success': True,
                    'message': 'Contract analyzed successfully',
                    'result': result
                }), 200
                
            except Exception as e:
                logger.error(f"Contract analysis failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/batch-analyze', methods=['POST'])
        def batch_analyze():
            """Analyze multiple contracts"""
            try:
                results = []
                for contract in self.contracts:
                    try:
                        result = self.run_contract_analysis(contract)
                        self.analysis_results.append(result)
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Analysis failed for {contract['name']}: {e}")
                        continue
                
                # Audit log
                audit_security_event('batch_analysis', {
                    'contract_count': len(self.contracts),
                    'results_count': len(results)
                })
                
                return jsonify({
                    'success': True,
                    'message': f'Analyzed {len(results)} contracts',
                    'results': results
                }), 200
                
            except Exception as e:
                logger.error(f"Batch analysis failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/generate-redlined-document', methods=['POST'])
        def generate_redlined_document():
            """Generate redlined document for a result"""
            try:
                data = request.get_json()
                if not data or 'result_id' not in data:
                    return jsonify({'error': 'Result ID is required'}), 400
                
                result_id = sanitize_input(data['result_id'])
                
                # Find result
                result = next((r for r in self.analysis_results if r['id'] == result_id), None)
                if not result:
                    return jsonify({'error': 'Analysis result not found'}), 404
                
                # Generate document using the correct method name
                file_path = self.report_generator.generate_review_document(result, result_id)
                
                return jsonify({
                    'success': True,
                    'message': 'Redlined document generated successfully',
                    'file_path': file_path
                }), 200
                
            except Exception as e:
                logger.error(f"Redlined document generation failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/generate-changes-table', methods=['POST'])
        def generate_changes_table():
            """Generate changes table for a result"""
            try:
                data = request.get_json()
                if not data or 'result_id' not in data:
                    return jsonify({'error': 'Result ID is required'}), 400
                
                result_id = sanitize_input(data['result_id'])
                
                # Find result
                result = next((r for r in self.analysis_results if r['id'] == result_id), None)
                if not result:
                    return jsonify({'error': 'Analysis result not found'}), 404
                
                # Generate table using the correct method name
                file_path = self.report_generator.generate_changes_table_xlsx(result, result_id)
                
                return jsonify({
                    'success': True,
                    'message': 'Changes table generated successfully',
                    'file_path': file_path
                }), 200
                
            except Exception as e:
                logger.error(f"Changes table generation failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/generate-summary-report', methods=['POST'])
        def generate_summary_report():
            """Generate summary report for a result"""
            try:
                data = request.get_json()
                if not data or 'result_id' not in data:
                    return jsonify({'error': 'Result ID is required'}), 400
                
                result_id = sanitize_input(data['result_id'])
                
                # Find result
                result = next((r for r in self.analysis_results if r['id'] == result_id), None)
                if not result:
                    return jsonify({'error': 'Analysis result not found'}), 404
                
                # Generate report using the correct method name
                file_path = self.report_generator.generate_summary_report_pdf(result, result_id)
                
                return jsonify({
                    'success': True,
                    'message': 'Summary report generated successfully',
                    'file_path': file_path
                }), 200
                
            except Exception as e:
                logger.error(f"Summary report generation failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/generate-word-com-redlined', methods=['POST'])
        def generate_word_com_redlined():
            """Generate Word COM redlined document for a result"""
            try:
                data = request.get_json()
                if not data or 'result_id' not in data:
                    return jsonify({'error': 'Result ID is required'}), 400
                
                result_id = sanitize_input(data['result_id'])
                
                # Find result
                result = next((r for r in self.analysis_results if r['id'] == result_id), None)
                if not result:
                    return jsonify({'error': 'Analysis result not found'}), 404
                
                # Generate document
                template_path = result.get('template_path')
                if not template_path:
                    return jsonify({'error': 'Template path not found in analysis result. Please re-run the analysis.'}), 400
                
                file_path = self.report_generator.generate_word_com_redlined_document(result, template_path, result['id'])
                
                # Check if file was actually generated (might be None due to COM cleanup issues)
                expected_file_path = os.path.join(config.REPORTS_FOLDER, f"{result['id']}_word_com_redlined.docx")
                
                if file_path is None:
                    # Check if file exists despite method returning None (COM cleanup error)
                    if os.path.exists(expected_file_path):
                        logger.info(f"Word COM document generated successfully despite cleanup warning: {expected_file_path}")
                        return jsonify({
                            'success': True,
                            'message': 'Word COM redlined document generated successfully',
                            'file_path': expected_file_path
                        }), 200
                    else:
                        return jsonify({
                            'success': False,
                            'error': 'Failed to generate Word COM redlined document. Check logs for details.'
                        }), 500
                
                return jsonify({
                    'success': True,
                    'message': 'Word COM redlined document generated successfully',
                    'file_path': file_path
                }), 200
                
            except Exception as e:
                logger.error(f"Word COM redlined document generation failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/download-redlined-document')
        def download_redlined_document():
            """Download redlined document"""
            try:
                result_id = request.args.get('id')
                if not result_id:
                    return jsonify({'error': 'Result ID is required'}), 400
                
                # Find the file - match the actual generated filename pattern
                file_path = os.path.join(config.REPORTS_FOLDER, f"{result_id}_redlined_document.docx")
                if not os.path.exists(file_path):
                    return jsonify({'error': 'File not found'}), 404
                
                return send_file(file_path, as_attachment=True)
                
            except Exception as e:
                logger.error(f"Download failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/download-changes-table')
        def download_changes_table():
            """Download changes table"""
            try:
                result_id = request.args.get('id')
                if not result_id:
                    return jsonify({'error': 'Result ID is required'}), 400
                
                # Find the file - match the actual generated filename pattern
                file_path = os.path.join(config.REPORTS_FOLDER, f"{result_id}_changes_table.xlsx")
                if not os.path.exists(file_path):
                    return jsonify({'error': 'File not found'}), 404
                
                return send_file(file_path, as_attachment=True)
                
            except Exception as e:
                logger.error(f"Download failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/download-summary-report')
        def download_summary_report():
            """Download summary report"""
            try:
                result_id = request.args.get('id')
                if not result_id:
                    return jsonify({'error': 'Result ID is required'}), 400
                
                # Find the file - match the actual generated filename pattern
                file_path = os.path.join(config.REPORTS_FOLDER, f"{result_id}_summary_report.pdf")
                if not os.path.exists(file_path):
                    return jsonify({'error': 'File not found'}), 404
                
                return send_file(file_path, as_attachment=True)
                
            except Exception as e:
                logger.error(f"Download failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/download-word-com-redlined')
        def download_word_com_redlined():
            """Download Word COM redlined document"""
            try:
                result_id = request.args.get('id')
                if not result_id:
                    return jsonify({'error': 'Result ID is required'}), 400
                
                # Find the file
                file_path = os.path.join(config.REPORTS_FOLDER, f"{result_id}_word_com_redlined.docx")
                if not os.path.exists(file_path):
                    return jsonify({'error': 'File not found'}), 404
                
                return send_file(file_path, as_attachment=True)
                
            except Exception as e:
                logger.error(f"Download failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/download-report')
        def download_report():
            """Download analysis report"""
            try:
                result_id = request.args.get('id')
                if not result_id:
                    return jsonify({'error': 'Result ID is required'}), 400
                
                # Find the file
                file_path = os.path.join(config.REPORTS_FOLDER, f"{result_id}_analysis.docx")
                if not os.path.exists(file_path):
                    return jsonify({'error': 'File not found'}), 404
                
                return send_file(file_path, as_attachment=True)
                
            except Exception as e:
                logger.error(f"Download failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/clear-cache', methods=['POST'])
        def clear_cache():
            """Clear various caches"""
            try:
                data = request.get_json()
                cache_type = data.get('type', 'all') if data else 'all'
                
                result = self.clear_cache(cache_type)
                
                # Audit log
                audit_security_event('cache_cleared', {
                    'cache_type': cache_type,
                    'user_ip': request.remote_addr
                })
                
                return jsonify(result), 200
                
            except Exception as e:
                logger.error(f"Cache clearing failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/cache-stats')
        def get_cache_stats():
            """Get cache statistics"""
            try:
                stats = self.get_cache_stats()
                return jsonify(stats), 200
            except Exception as e:
                logger.error(f"Cache stats failed: {e}")
                return jsonify({'error': str(e)}), 500

        # Add security headers to all responses
        @self.app.after_request
        def add_security_headers(response):
            headers = get_security_headers()
            for key, value in headers.items():
                response.headers[key] = value
            return response

        # Error handlers
        @self.app.errorhandler(413)
        def too_large(e):
            return jsonify({'error': 'File too large'}), 413

        @self.app.errorhandler(404)
        def not_found(e):
            return jsonify({'error': 'Endpoint not found'}), 404

        @self.app.errorhandler(500)
        def internal_error(e):
            logger.error(f"Internal server error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def run_contract_analysis(self, contract):
        """Run analysis on a contract with timeout and error handling"""
        try:
            # Find best matching template
            template = self.find_best_template(contract)
            if not template:
                raise Exception("Not a vendor contract - no matching template found. Contract must contain vendor names (epam, capgemini, blue optima) or be SOW/CO type. This may be a resume or non-vendor document.")
            
            # Extract text from contract and template
            contract_text = self.analyzer.extract_text_from_docx(contract['path'])
            template_text = self.analyzer.extract_text_from_docx(template['path'])
            
            # Find changes
            changes = self.analyzer.find_changes(template_text, contract_text)
            
            # Analyze with LLM (with enhanced error handling)
            analysis = self.llm_handler.analyze_changes(changes)
            
            # Calculate similarity
            similarity = self.analyzer.calculate_similarity(template_text, contract_text)
            
            # Determine status
            status = self.determine_status(changes, similarity)
            
            # Create result
            result = {
                'id': f"{contract['id']}_{int(datetime.datetime.now().timestamp())}",
                'contract': contract['name'],
                'contract_path': contract['path'],  # Add original contract path
                'template': template['name'],
                'template_path': template['path'],
                'status': status,
                'changes': len(changes),
                'similarity': round(similarity * 100, 1),
                'date': datetime.datetime.now().isoformat(),
                'analysis': analysis,
                'detailed_changes': changes
            }
            
            # Generate report
            self.generate_report(result, contract, template)
            
            return result
            
        except Exception as e:
            logger.error(f"Contract analysis failed: {e}")
            raise
    
    def find_best_template(self, contract):
        """
        Find the best matching template for a contract using structured keyword matching
        
        Priority order:
        1. Check for vendor names (epam, capgemini, blue optima) in content
        2. Check for SOW keywords in title and content
        3. Check for CO keywords in title and content
        4. If none match, it's probably not a vendor contract (resume, etc.)
        """
        if not self.templates:
            return None
        
        # Extract contract text and filename for keyword matching
        try:
            contract_text = self.analyzer.extract_text_from_docx(contract['path'])
            contract_text_lower = contract_text.lower()
            contract_filename_lower = contract['name'].lower()
        except Exception as e:
            logger.error(f"Could not extract contract text for template matching: {e}")
            # Fallback to filename-based matching only
            contract_text_lower = contract['name'].lower()
            contract_filename_lower = contract['name'].lower()
        
        # STEP 1: Check for vendor-specific keywords in content
        logger.debug(f"Checking vendor keywords in contract content...")
        
        if "epam" in contract_text_lower:
            logger.debug("Found EPAM vendor keyword")
            for template in self.templates:
                if "epam" in template['name'].lower():
                    logger.info(f"Matched contract to EPAM template: {template['name']}")
                    return template
        
        if "capgemini" in contract_text_lower:
            logger.debug("Found Capgemini vendor keyword")
            for template in self.templates:
                if "capgemini" in template['name'].lower():
                    logger.info(f"Matched contract to Capgemini template: {template['name']}")
                    return template
        
        if "blue optima" in contract_text_lower:
            logger.debug("Found Blue Optima vendor keyword")
            for template in self.templates:
                template_name_lower = template['name'].lower()
                if "blue optima" in template_name_lower or "blue_optima" in template_name_lower:
                    logger.info(f"Matched contract to Blue Optima template: {template['name']}")
                    return template
        
        # STEP 2: Check for SOW keywords in title and content
        logger.debug("Checking SOW keywords in title and content...")
        sow_keywords = ["sow", "statement of work", "statement_of_work", "statement-of-work"]
        
        sow_found_in_title = any(keyword in contract_filename_lower for keyword in sow_keywords)
        sow_found_in_content = any(keyword in contract_text_lower for keyword in sow_keywords)
        
        if sow_found_in_title or sow_found_in_content:
            logger.debug(f"Found SOW keywords - Title: {sow_found_in_title}, Content: {sow_found_in_content}")
            for template in self.templates:
                template_name_lower = template['name'].lower()
                if "sow" in template_name_lower and "standard" in template_name_lower:
                    logger.info(f"Matched contract to SOW template: {template['name']}")
                    return template
        
        # STEP 3: Check for CO (Change Order) keywords in title and content
        logger.debug("Checking CO keywords in title and content...")
        co_keywords = ["change order", "change_order", "change-order", "changeorder", "change request", "change_request", "co"]
        
        co_found_in_title = any(keyword in contract_filename_lower for keyword in co_keywords)
        co_found_in_content = any(keyword in contract_text_lower for keyword in co_keywords)
        
        if co_found_in_title or co_found_in_content:
            logger.debug(f"Found CO keywords - Title: {co_found_in_title}, Content: {co_found_in_content}")
            for template in self.templates:
                template_name_lower = template['name'].lower()
                if "changeorder" in template_name_lower or "change" in template_name_lower:
                    logger.info(f"Matched contract to CO template: {template['name']}")
                    return template
        
        # STEP 4: No vendor contract patterns found
        logger.warning(f"No vendor contract patterns found in '{contract['name']}' - this may be a resume or non-vendor document")
        return None
    
    def determine_status(self, changes, similarity):
        """Determine contract review status based on changes and similarity"""
        change_count = len(changes)
        
        if change_count == 0:
            return 'No changes'
        elif change_count <= 5:
            return 'Changes - Minor'
        elif change_count <= 15:
            return 'Changes - Moderate'
        elif change_count <= 30:
            return 'Changes - Major'
        else:
            return 'Changes - Extensive'
    
    def determine_contract_type(self, filename):
        """Determine contract type from filename using simplified logic"""
        filename_lower = filename.lower()
        if 'epam' in filename_lower:
            return 'EPAM'
        elif 'capgemini' in filename_lower:
            return 'Capgemini'
        elif 'blue' in filename_lower and 'optima' in filename_lower:
            return 'Blue Optima'
        elif 'sow' in filename_lower:
            return 'Generic SOW'
        elif 'co' in filename_lower or 'change' in filename_lower:
            return 'Change Order'
        else:
            return 'Unknown'
    
    def determine_template_category(self, filename):
        """Determine template category from filename using simplified logic"""
        filename_lower = filename.lower()
        if 'epam' in filename_lower:
            return 'EPAM'
        elif 'capgemini' in filename_lower:
            return 'Capgemini'
        elif 'blue' in filename_lower and 'optima' in filename_lower:
            return 'Blue Optima'
        elif 'generic' in filename_lower and 'sow' in filename_lower:
            return 'Generic SOW'
        elif 'co' in filename_lower or 'change' in filename_lower:
            return 'Change Order'
        else:
            return 'Unknown'
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def get_recent_activity(self):
        """Get recent activity for dashboard"""
        try:
            # Get last 5 analysis results
            recent_results = sorted(self.analysis_results, 
                                  key=lambda x: x.get('date', ''), 
                                  reverse=True)[:5]
            
            return [
                {
                    'type': 'analysis',
                    'description': f"Analyzed {r['contract']}",
                    'timestamp': r.get('date', ''),
                    'status': r.get('status', 'unknown')
                }
                for r in recent_results
            ]
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
    
    def get_disk_usage(self):
        """Get disk usage statistics"""
        try:
            import shutil
            usage = shutil.disk_usage(config.BASE_DIR)
            total = usage.total
            used = usage.used
            free = usage.free
            
            return {
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'free_gb': round(free / (1024**3), 2),
                'used_percent': round(used / total * 100, 1),
                'available_percent': round(free / total * 100, 1)
            }
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            return {'error': str(e)}
    
    def generate_report(self, result, contract, template):
        """Generate detailed analysis report and all report types"""
        try:
            # Generate the basic analysis file (copy of contract)
            report_path = os.path.join(self.app.config['REPORTS_FOLDER'], f"{result['id']}_analysis.docx")
            import shutil
            shutil.copy2(contract['path'], report_path)
            
            # Generate all report types using EnhancedReportGenerator
            base_name = result['id']
            
            # Generate redlined document
            redlined_path = self.report_generator.generate_review_document(result, base_name)
            logger.info(f"Redlined document generated: {redlined_path}")
            
            # Generate changes table
            changes_path = self.report_generator.generate_changes_table_xlsx(result, base_name)
            logger.info(f"Changes table generated: {changes_path}")
            
            # Generate summary report
            summary_path = self.report_generator.generate_summary_report_pdf(result, base_name)
            logger.info(f"Summary report generated: {summary_path}")
            
            logger.info(f"All reports generated for analysis: {result['id']}")
            
        except Exception as e:
            logger.error(f"Error generating reports: {e}")
            # Don't fail the entire analysis if report generation fails
            logger.warning("Analysis completed but some reports may be missing")
    
    def save_analysis_results(self):
        """Save analysis results to file"""
        try:
            with open('analysis_results.json', 'w') as f:
                json.dump(self.analysis_results, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving analysis results: {e}")

    def clear_cache(self, cache_type='all'):
        """
        Clear various types of cache
        
        Args:
            cache_type (str): Type of cache to clear
                - 'memory': Clear only in-memory cache
                - 'files': Clear only file cache
                - 'all': Clear both memory and file cache
                - 'reports': Clear only report files
                - 'analysis': Clear only analysis results
        
        Returns:
            dict: Status and details of cache clearing
        """
        try:
            cleared_items = []
            
            if cache_type in ['memory', 'all', 'analysis']:
                # Clear in-memory analysis results
                analysis_count = len(self.analysis_results)
                self.analysis_results = []
                cleared_items.append(f"In-memory analysis results ({analysis_count} items)")
                
            if cache_type in ['files', 'all', 'analysis']:
                # Clear analysis results JSON file
                if os.path.exists('analysis_results.json'):
                    os.remove('analysis_results.json')
                    cleared_items.append("Analysis results JSON file")
                    
            if cache_type in ['files', 'all', 'reports']:
                # Clear reports directory
                reports_dir = Path(self.app.config['REPORTS_FOLDER'])
                if reports_dir.exists():
                    report_files = list(reports_dir.glob('*.docx'))
                    json_files = list(reports_dir.glob('*.json'))
                    
                    for file in report_files + json_files:
                        try:
                            file.unlink()
                        except Exception as e:
                            logger.warning(f"Failed to delete {file}: {e}")
                    
                    cleared_items.append(f"Report files ({len(report_files)} .docx, {len(json_files)} .json)")
                    
            # Optional: Clear contract and template cache if requested
            if cache_type == 'all':
                # Note: We don't clear actual uploaded files, just the cache
                # The files remain in uploads/ and templates/ directories
                pass
            
            logger.info(f"Cache cleared: {', '.join(cleared_items)}")
            
            return {
                'success': True,
                'message': f"Cache cleared successfully",
                'cleared_items': cleared_items,
                'cache_type': cache_type
            }
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return {
                'success': False,
                'message': f"Error clearing cache: {str(e)}",
                'cache_type': cache_type
            }
    
    def get_cache_stats(self):
        """
        Get statistics about current cache usage
        
        Returns:
            dict: Cache statistics
        """
        try:
            stats = {
                'memory': {
                    'analysis_results': len(self.analysis_results),
                    'contracts': len(self.contracts),
                    'templates': len(self.templates)
                },
                'files': {
                    'analysis_json_exists': os.path.exists('analysis_results.json'),
                    'analysis_json_size': 0,
                    'reports_count': 0,
                    'reports_size_mb': 0
                }
            }
            
            # Get analysis JSON file size
            if os.path.exists('analysis_results.json'):
                stats['files']['analysis_json_size'] = os.path.getsize('analysis_results.json')
            
            # Get reports directory stats
            reports_dir = Path(self.app.config['REPORTS_FOLDER'])
            if reports_dir.exists():
                report_files = list(reports_dir.glob('*.docx')) + list(reports_dir.glob('*.json'))
                stats['files']['reports_count'] = len(report_files)
                
                total_size = sum(f.stat().st_size for f in report_files)
                stats['files']['reports_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'error': str(e)}

    def run(self, host=None, port=None, debug=None):
        """Run the dashboard server with configuration"""
        host = host or config.HOST
        port = port or config.PORT
        debug = debug if debug is not None else config.DEBUG
        
        logger.info(f"Starting dashboard server on {host}:{port} (debug={debug})")
        
        # Security audit
        audit_security_event('server_started', {
            'host': host,
            'port': port,
            'debug': debug
        })
        
        self.app.run(host=host, port=port, debug=debug) 