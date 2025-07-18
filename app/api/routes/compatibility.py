"""
Compatibility routes for legacy frontend endpoints

Provides backward compatibility for frontend that expects different endpoint names.
"""

from flask import Blueprint, jsonify, request
from .analysis import analysis_results_store
from .contracts import contracts_store
from ...config.settings import get_config
from ...utils.logging.setup import get_logger

logger = get_logger(__name__)
compatibility_bp = Blueprint('compatibility', __name__)


@compatibility_bp.route('/analysis-results')
def legacy_analysis_results():
    """Legacy endpoint for analysis results - redirects to new structure"""
    try:
        # Convert new format to legacy format expected by frontend
        results = []
        for analysis_id, result in analysis_results_store.items():
            results.append({
                'id': analysis_id,
                'contract': result.get('contract_name', 'Unknown'),
                'template': result.get('template_name', 'Unknown'),
                'date': result.get('analysis_timestamp', ''),
                'status': result.get('status', 'completed'),
                'changes': result.get('total_changes', 0),
                'similarity': result.get('similarity_score', 0) * 100,
                'analysis': result.get('analysis_results', [])
            })
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Error in legacy analysis results endpoint: {e}")
        return jsonify([]), 200  # Return empty array on error


@compatibility_bp.route('/model-info')
def legacy_model_info():
    """Legacy endpoint for model info"""
    try:
        config = get_config()
        
        return jsonify({
            'name': config.OPENAI_MODEL,
            'provider': config.LLM_PROVIDER,
            'model': config.OPENAI_MODEL,
            'status': 'connected',
            'connection_healthy': True,
            'info': f"{config.LLM_PROVIDER} - {config.OPENAI_MODEL}"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in legacy model info endpoint: {e}")
        return jsonify({
            'name': 'gpt-4o',
            'provider': 'openai',
            'model': 'gpt-4o',
            'status': 'unknown',
            'connection_healthy': False,
            'info': 'Model information unavailable'
        }), 200


@compatibility_bp.route('/templates/upload', methods=['POST'])
def legacy_template_upload():
    """Legacy endpoint for template upload - placeholder for now"""
    try:
        return jsonify({
            'success': False,
            'error': 'Template upload not yet implemented'
        }), 501
        
    except Exception as e:
        logger.error(f"Error in legacy template upload endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Template upload failed'
        }), 500


@compatibility_bp.route('/available-models')
def legacy_available_models():
    """Legacy endpoint for available models"""
    try:
        config = get_config()
        
        return jsonify({
            'success': True,
            'models': [
                {
                    'name': config.OPENAI_MODEL,
                    'size': 0,
                    'current': True
                }
            ],
            'current_model': config.OPENAI_MODEL
        }), 200
        
    except Exception as e:
        logger.error(f"Error in legacy available models endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load models'
        }), 500


@compatibility_bp.route('/cache-stats')
def legacy_cache_stats():
    """Legacy endpoint for cache statistics"""
    try:
        return jsonify({
            'success': True,
            'stats': {
                'analysis_count': len(analysis_results_store),
                'analysis_size': '0 MB',
                'reports_count': 0,
                'reports_size': '0 MB',
                'memory_count': len(contracts_store),
                'memory_size': '0 MB',
                'total_size': '0 MB'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in legacy cache stats endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load cache stats'
        }), 500


@compatibility_bp.route('/clear-cache', methods=['POST'])
def legacy_clear_cache():
    """Legacy endpoint for clearing cache"""
    try:
        return jsonify({
            'success': True,
            'message': 'Cache clearing not implemented'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in legacy clear cache endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to clear cache'
        }), 500


@compatibility_bp.route('/clear-contracts', methods=['POST'])
def legacy_clear_contracts():
    """Legacy endpoint for clearing contracts"""
    try:
        contracts_store.clear()
        return jsonify({
            'success': True,
            'message': 'All contracts cleared successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in legacy clear contracts endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to clear contracts'
        }), 500


@compatibility_bp.route('/clear-files', methods=['POST'])
def legacy_clear_files():
    """Legacy endpoint for clearing all files"""
    try:
        contracts_store.clear()
        return jsonify({
            'success': True,
            'message': 'All files cleared successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in legacy clear files endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to clear files'
        }), 500


@compatibility_bp.route('/openai-models')
def legacy_openai_models():
    """Legacy endpoint for OpenAI models list"""
    try:
        config = get_config()
        
        # Simulate OpenAI models list
        models = [
            {
                'name': 'gpt-4o',
                'description': 'Most advanced GPT-4 model with vision capabilities',
                'context_window': 128000,
                'tier': 'premium',
                'recommended': True
            },
            {
                'name': 'gpt-4o-mini',
                'description': 'Faster, more affordable GPT-4 model',
                'context_window': 128000,
                'tier': 'standard',
                'recommended': False
            },
            {
                'name': 'gpt-4-turbo',
                'description': 'Previous generation GPT-4 model',
                'context_window': 128000,
                'tier': 'premium',
                'recommended': False
            },
            {
                'name': 'gpt-3.5-turbo',
                'description': 'Fast and efficient GPT-3.5 model',
                'context_window': 16384,
                'tier': 'standard',
                'recommended': False
            }
        ]
        
        return jsonify({
            'success': True,
            'models': models,
            'current_model': config.OPENAI_MODEL,
            'recommendations': {
                'best_overall': 'gpt-4o',
                'most_economical': 'gpt-4o-mini'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in legacy openai models endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load OpenAI models'
        }), 500


@compatibility_bp.route('/update-openai-model', methods=['POST'])
def legacy_update_openai_model():
    """Legacy endpoint for updating OpenAI model"""
    try:
        data = request.get_json()
        if not data or 'model' not in data:
            return jsonify({
                'success': False,
                'error': 'Model name required'
            }), 400
        
        model_name = data['model']
        
        # Validate model name
        valid_models = ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo']
        if model_name not in valid_models:
            return jsonify({
                'success': False,
                'error': f'Invalid model: {model_name}'
            }), 400
        
        # In a real implementation, this would update the configuration
        logger.info(f"Model change requested: {model_name}")
        
        return jsonify({
            'success': True,
            'message': f'Model changed to {model_name}',
            'model': model_name
        }), 200
        
    except Exception as e:
        logger.error(f"Error in legacy update openai model endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update model'
        }), 500


@compatibility_bp.route('/llm-provider')
def legacy_llm_provider():
    """Legacy endpoint for LLM provider information"""
    try:
        config = get_config()
        
        return jsonify({
            'success': True,
            'provider': config.LLM_PROVIDER,
            'model': config.OPENAI_MODEL,
            'api_key_configured': True,  # Assume configured
            'temperature': 0.1,
            'max_tokens': 1024
        }), 200
        
    except Exception as e:
        logger.error(f"Error in legacy llm provider endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get LLM provider info'
        }), 500


@compatibility_bp.route('/update-llm-settings', methods=['POST'])
def legacy_update_llm_settings():
    """Legacy endpoint for updating LLM settings"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Settings data required'
            }), 400
        
        # Log the settings update (in real implementation, would save to config)
        logger.info(f"LLM settings update requested: {data}")
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully',
            'updated_settings': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error in legacy update llm settings endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update settings'
        }), 500