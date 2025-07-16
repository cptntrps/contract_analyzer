# app/routes.py
from flask import request, jsonify, render_template, send_file, current_app
import os
import werkzeug
from werkzeug.utils import secure_filename
from . import analyzer
from . import llm_handler
import json

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def classify_contract_type(contract_text):
    """
    Structured contract type classification with priority order:
    1. Check for vendor names (epam, capgemini, blue optima) in content
    2. Check for SOW keywords in content
    3. Check for CO keywords in content
    4. If none match, it's probably not a vendor contract
    
    Args:
        contract_text (str): Extracted text from the uploaded contract
        
    Returns:
        str: Template filename to use for comparison, or None if not a vendor contract
    """
    contract_text_lower = contract_text.lower()
    
    # STEP 1: Check for vendor-specific keywords in content
    if "epam" in contract_text_lower:
        return "epam_msa.docx"
    
    if "capgemini" in contract_text_lower:
        return "capgemini_tm.docx"
    
    if "blue optima" in contract_text_lower:
        return "blue_optima.docx"
    
    # STEP 2: Check for SOW keywords in content
    sow_keywords = ["sow", "statement of work", "statement_of_work", "statement-of-work"]
    if any(keyword in contract_text_lower for keyword in sow_keywords):
        return "general_sow.docx"
    
    # STEP 3: Check for CO (Change Order) keywords in content
    co_keywords = ["change order", "change_order", "change-order", "changeorder", "change request", "change_request"]
    if any(keyword in contract_text_lower for keyword in co_keywords):
        return "general_change_order.docx"
    
    # STEP 4: No vendor contract patterns found - may be resume or non-vendor document
    return None

# This function is no longer needed as we use render_template

def init_routes(app):
    """Initialize all routes for the application."""
    
    # @app.route('/')
    # def index():
    #     """Main dashboard page."""
    #     return render_template('index.html')

    @app.route('/api/analyze', methods=['POST'])
    def analyze_contract():
        """
        Main API endpoint for contract analysis.
        Executes the complete workflow:
        1. File upload and validation
        2. Text extraction
        3. Contract type classification
        4. Template comparison
        5. LLM analysis of changes
        6. Report generation
        """
        try:
            # Check if file was uploaded
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type. Only .docx files are allowed.'}), 400
            
            # Secure the filename and save the file
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            
            # Step 1: Extract text from uploaded file
            contract_text = analyzer.extract_text_from_docx(upload_path)
            if not contract_text:
                return jsonify({'error': 'Could not extract text from the uploaded file'}), 400
            
            # Step 2: Classify contract type
            selected_template = classify_contract_type(contract_text)
            if not selected_template:
                return jsonify({'error': 'Could not classify contract type. Please ensure the document contains relevant keywords.'}), 400
            
            # Step 3: Get template path and extract template text
            template_path = os.path.join(app.config['TEMPLATES_FOLDER'], selected_template)
            if not os.path.exists(template_path):
                return jsonify({'error': f'Template {selected_template} not found. Please ensure all templates are available.'}), 400
            
            template_text = analyzer.extract_text_from_docx(template_path)
            if not template_text:
                return jsonify({'error': 'Could not extract text from the template file'}), 400
            
            # Step 4: Compare texts and get differences
            changes = analyzer.compare_texts(template_text, contract_text)
            if not changes:
                return jsonify({'message': 'No differences found between the contract and template'}), 200
            
            # Step 5: Analyze changes with LLM
            analysis_results = []
            for operation, text in changes:
                if operation == 'delete':
                    # Find corresponding insert operation
                    deleted_text = text
                    inserted_text = ""
                    # Look for corresponding insert in the next few changes
                    for i, (next_op, next_text) in enumerate(changes[changes.index((operation, text)):changes.index((operation, text))+3]):
                        if next_op == 'insert':
                            inserted_text = next_text
                            break
                    
                    if deleted_text.strip() and inserted_text.strip():
                        analysis = llm_handler.get_change_analysis(deleted_text, inserted_text)
                        analysis_results.append(analysis)
            
            # Step 6: Generate commented document
            base_name = os.path.splitext(filename)[0]
            commented_doc_path = os.path.join(app.config['REPORTS_FOLDER'], f"{base_name}_analyzed.docx")
            
            success = analyzer.create_commented_docx(upload_path, analysis_results, commented_doc_path)
            if not success:
                return jsonify({'error': 'Failed to generate commented document'}), 500
            
            # Step 7: Save metadata
            metadata_path = analyzer.save_analysis_metadata(
                filename, selected_template, analysis_results, app.config['REPORTS_FOLDER']
            )
            
            # Step 8: Prepare response
            significant_changes = [r for r in analysis_results if r.get('classification') == 'SIGNIFICANT']
            
            response_data = {
                'uploaded_filename': filename,
                'selected_template': selected_template,
                'total_changes': len(analysis_results),
                'significant_changes_count': len(significant_changes),
                'inconsequential_changes_count': len(analysis_results) - len(significant_changes),
                'analysis_results': analysis_results,
                'commented_document_path': commented_doc_path,
                'metadata_path': metadata_path,
                'risk_level': 'HIGH' if len(significant_changes) > 0 else 'LOW'
            }
            
            return jsonify(response_data), 200
            
        except Exception as e:
            print(f"Error in contract analysis: {str(e)}")
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500

    @app.route('/api/download/<filename>')
    def download_report(filename):
        """
        Download the analyzed document.
        
        Args:
            filename (str): Name of the file to download
        """
        try:
            file_path = os.path.join(app.config['REPORTS_FOLDER'], filename)
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True)
            else:
                return jsonify({'error': 'File not found'}), 404
        except Exception as e:
            return jsonify({'error': f'Error downloading file: {str(e)}'}), 500

    @app.route('/api/health')
    def health_check():
        """Health check endpoint."""
        try:
            # Test Ollama connection
            ollama_status = llm_handler.test_ollama_connection()
            
            return jsonify({
                'status': 'healthy',
                'ollama_connected': ollama_status,
                'templates_available': os.path.exists(app.config['TEMPLATES_FOLDER'])
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 500

# The index route is already defined above 