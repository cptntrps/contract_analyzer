"""
Contract analysis routes

Handles contract analysis operations and results.
"""

import os
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app

from ...core.services.analyzer import create_contract_analyzer, ContractAnalysisError
from ...core.models.contract import Contract
from ...utils.security.audit import SecurityAuditor
from ...utils.logging.setup import get_logger

# Import contracts store from contracts routes
from .contracts import contracts_store

logger = get_logger(__name__)
analysis_bp = Blueprint('analysis', __name__)

# Initialize security auditor
security_auditor = SecurityAuditor()

# Store analysis results (in production, use database)
analysis_results_store = {}


@analysis_bp.route('/analysis')
def list_analysis_results():
    """List all analysis results"""
    try:
        results_list = []
        
        for analysis_result in analysis_results_store.values():
            results_list.append(analysis_result.get_summary())
        
        # Sort by analysis date (newest first)
        results_list.sort(key=lambda x: x['analysis_date'], reverse=True)
        
        return jsonify({
            'success': True,
            'analysis_results': results_list,
            'total': len(results_list)
        })
        
    except Exception as e:
        logger.error(f"Error listing analysis results: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to list analysis results'
        }), 500


@analysis_bp.route('/analysis/start', methods=['POST'])
def start_analysis():
    """Start contract analysis"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No request data provided'
            }), 400
        
        contract_id = data.get('contract_id')
        template_filename = data.get('template')
        include_llm = data.get('include_llm_analysis', True)
        
        # Validate required fields
        if not contract_id:
            return jsonify({
                'success': False,
                'error': 'Contract ID is required'
            }), 400
        
        if not template_filename:
            return jsonify({
                'success': False,
                'error': 'Template filename is required'
            }), 400
        
        # Get contract
        if contract_id not in contracts_store:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        contract = contracts_store[contract_id]
        
        # Validate contract file exists
        if not Path(contract.file_path).exists():
            return jsonify({
                'success': False,
                'error': 'Contract file not found on disk'
            }), 404
        
        # Find template file
        templates_dir = Path(current_app.config.get('TEMPLATES_FOLDER', 'data/templates'))
        template_path = templates_dir / template_filename
        
        if not template_path.exists():
            return jsonify({
                'success': False,
                'error': f'Template file {template_filename} not found'
            }), 404
        
        # Initialize analyzer
        config = {
            'llm_settings': current_app.config.get('LLM_SETTINGS', {}),
            'analysis_settings': current_app.config.get('ANALYSIS_SETTINGS', {})
        }
        
        analyzer = create_contract_analyzer(config)
        
        # Log analysis start
        security_auditor.log_security_event(
            event_type='analysis_started',
            details={
                'contract_id': contract_id,
                'template': template_filename,
                'include_llm': include_llm
            },
            request=request
        )
        
        # Perform analysis
        logger.info(f"Starting analysis for contract {contract_id} with template {template_filename}")
        
        analysis_result = analyzer.analyze_contract(
            contract=contract,
            template_path=str(template_path),
            include_llm_analysis=include_llm
        )
        
        # Store analysis result
        analysis_results_store[analysis_result.analysis_id] = analysis_result
        
        # Log analysis completion
        security_auditor.log_security_event(
            event_type='analysis_completed',
            details={
                'analysis_id': analysis_result.analysis_id,
                'contract_id': contract_id,
                'total_changes': analysis_result.total_changes,
                'risk_level': analysis_result.overall_risk_level,
                'processing_time': analysis_result.processing_time_seconds
            },
            request=request
        )
        
        logger.info(
            f"Analysis {analysis_result.analysis_id} completed - "
            f"Changes: {analysis_result.total_changes}, Risk: {analysis_result.overall_risk_level}"
        )
        
        return jsonify({
            'success': True,
            'analysis_result': analysis_result.get_summary(),
            'message': 'Analysis completed successfully'
        })
        
    except ContractAnalysisError as e:
        logger.error(f"Contract analysis error: {e}")
        security_auditor.log_security_event(
            event_type='analysis_failed',
            details={'error': str(e)},
            request=request
        )
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        security_auditor.log_security_event(
            event_type='analysis_error',
            details={'error': str(e)},
            request=request
        )
        return jsonify({
            'success': False,
            'error': 'Failed to start analysis'
        }), 500


@analysis_bp.route('/analysis/<analysis_id>')
def get_analysis_result(analysis_id):
    """Get detailed analysis result by ID"""
    try:
        if analysis_id not in analysis_results_store:
            return jsonify({
                'success': False,
                'error': 'Analysis result not found'
            }), 404
        
        analysis_result = analysis_results_store[analysis_id]
        
        # Return detailed analysis data
        detailed_result = analysis_result.to_dict()
        
        return jsonify({
            'success': True,
            'analysis_result': detailed_result
        })
        
    except Exception as e:
        logger.error(f"Error retrieving analysis result {analysis_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve analysis result'
        }), 500


@analysis_bp.route('/analysis/<analysis_id>/changes')
def get_analysis_changes(analysis_id):
    """Get detailed changes for an analysis"""
    try:
        if analysis_id not in analysis_results_store:
            return jsonify({
                'success': False,
                'error': 'Analysis result not found'
            }), 404
        
        analysis_result = analysis_results_store[analysis_id]
        
        # Group changes by classification
        changes_by_type = {
            'critical': [change.to_dict() for change in analysis_result.get_critical_changes()],
            'significant': [change.to_dict() for change in analysis_result.get_significant_changes()],
            'inconsequential': [change.to_dict() for change in analysis_result.get_inconsequential_changes()]
        }
        
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'changes_by_type': changes_by_type,
            'total_changes': analysis_result.total_changes,
            'risk_level': analysis_result.overall_risk_level
        })
        
    except Exception as e:
        logger.error(f"Error retrieving changes for analysis {analysis_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve analysis changes'
        }), 500


@analysis_bp.route('/templates')
def list_templates():
    """List available template files"""
    try:
        templates_dir = Path(current_app.config.get('TEMPLATES_FOLDER', 'data/templates'))
        
        if not templates_dir.exists():
            return jsonify({
                'success': True,
                'templates': [],
                'message': 'Templates directory not found'
            })
        
        templates = []
        for template_file in templates_dir.glob('*.docx'):
            try:
                stat = template_file.stat()
                templates.append({
                    'filename': template_file.name,
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'display_name': template_file.stem.replace('_', ' ').title()
                })
            except Exception as e:
                logger.warning(f"Error reading template {template_file}: {e}")
        
        # Sort by filename
        templates.sort(key=lambda x: x['filename'])
        
        return jsonify({
            'success': True,
            'templates': templates,
            'total': len(templates)
        })
        
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to list templates'
        }), 500


@analysis_bp.route('/analysis/<analysis_id>', methods=['DELETE'])
def delete_analysis_result(analysis_id):
    """Delete an analysis result"""
    try:
        if analysis_id not in analysis_results_store:
            return jsonify({
                'success': False,
                'error': 'Analysis result not found'
            }), 404
        
        analysis_result = analysis_results_store[analysis_id]
        contract_id = analysis_result.contract_id
        
        # Remove from store
        del analysis_results_store[analysis_id]
        
        # Log deletion
        security_auditor.log_security_event(
            event_type='analysis_deleted',
            details={'analysis_id': analysis_id, 'contract_id': contract_id},
            request=request
        )
        
        return jsonify({
            'success': True,
            'message': f'Analysis result {analysis_id} deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting analysis result {analysis_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete analysis result'
        }), 500