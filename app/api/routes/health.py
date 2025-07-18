"""
Health check and system status routes
"""

from flask import Blueprint, jsonify
from ...main import get_app_info
from ...utils.logging.setup import get_logger

logger = get_logger(__name__)

health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health_check():
    """Basic health check endpoint"""
    try:
        app_info = get_app_info()
        
        health_data = {
            **app_info,
            'status': 'healthy',
            'message': 'Application is running'
        }
        
        return jsonify(health_data), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'message': 'Health check failed',
            'error': str(e)
        }), 500


@health_bp.route('/status')
def system_status():
    """Detailed system status"""
    try:
        # TODO: Add more detailed system checks
        # - Database connectivity
        # - LLM provider status
        # - File system status
        # - Memory usage
        
        status_data = {
            'application': get_app_info(),
            'system': {
                'status': 'operational',
                # TODO: Add system metrics
            },
            'services': {
                'llm_provider': 'unknown',  # TODO: Check LLM provider
                'file_storage': 'operational',  # TODO: Check file storage
            }
        }
        
        return jsonify(status_data), 200
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Status check failed',
            'error': str(e)
        }), 500