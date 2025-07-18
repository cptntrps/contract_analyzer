# Contract Analyzer API Reference

## Overview

The Contract Analyzer provides a comprehensive RESTful API for contract analysis operations. All endpoints return JSON responses and follow standard HTTP conventions.

**Base URL**: `http://localhost:5000/api`  
**Content-Type**: `application/json`  
**Authentication**: None (currently open access)

## API Endpoints

### Health and Status

#### GET `/health`
Basic health check endpoint.

**Response:**
```json
{
  "name": "Contract Analyzer",
  "version": "1.0.0",
  "status": "healthy",
  "message": "Application is running"
}
```

#### GET `/status`
Detailed system status with service health information.

**Response:**
```json
{
  "application": {
    "name": "Contract Analyzer",
    "version": "1.0.0",
    "status": "healthy"
  },
  "system": {
    "status": "operational"
  },
  "services": {
    "llm_provider": "operational",
    "file_storage": "operational"
  }
}
```

### Contract Management

#### POST `/contracts/upload`
Upload a contract file for analysis.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Form data with file upload

**Form Fields:**
- `file`: Contract file (required, .docx or .doc)
- `name`: Custom contract name (optional)

**Example cURL:**
```bash
curl -X POST http://localhost:5000/api/contracts/upload \
  -F "file=@contract.docx" \
  -F "name=Q1 2025 Service Agreement"
```

**Response (Success - 201):**
```json
{
  "success": true,
  "message": "Contract uploaded successfully",
  "contract": {
    "id": "contract_123",
    "filename": "contract_123.docx",
    "original_name": "Q1 2025 Service Agreement.docx",
    "upload_timestamp": "2025-01-18T10:30:00Z",
    "file_size": 245760,
    "status": "uploaded"
  }
}
```

**Response (Error - 400):**
```json
{
  "success": false,
  "error": "Invalid file type. Only .docx and .doc files are supported.",
  "details": {
    "allowed_extensions": [".docx", ".doc"],
    "max_file_size": "50MB"
  }
}
```

#### GET `/contracts`
List all uploaded contracts.

**Query Parameters:**
- `status`: Filter by status (uploaded, processing, analyzed, error)
- `limit`: Number of results to return (default: 20)
- `offset`: Number of results to skip (default: 0)

**Example:**
```bash
curl "http://localhost:5000/api/contracts?status=analyzed&limit=10"
```

**Response:**
```json
{
  "success": true,
  "contracts": [
    {
      "id": "contract_123",
      "filename": "Q1 2025 Service Agreement.docx",
      "status": "analyzed",
      "upload_date": "2025-01-18T10:30:00Z",
      "analysis_date": "2025-01-18T10:35:00Z",
      "file_size": 245760,
      "changes_count": 15,
      "similarity_score": 87.5,
      "risk_level": "MEDIUM"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

#### DELETE `/contracts/{contract_id}`
Delete a specific contract and its associated data.

**Example:**
```bash
curl -X DELETE http://localhost:5000/api/contracts/contract_123
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Contract deleted successfully",
  "contract_id": "contract_123"
}
```

#### POST `/contracts/clear`
Delete all uploaded contracts and associated data.

**Response:**
```json
{
  "success": true,
  "message": "All contracts cleared successfully",
  "deleted_count": 5
}
```

#### GET `/contracts/{contract_id}/validate`
Validate a specific contract file.

**Response:**
```json
{
  "success": true,
  "valid": true,
  "contract_id": "contract_123",
  "validation": {
    "file_exists": true,
    "file_readable": true,
    "valid_format": true,
    "file_size_ok": true,
    "has_content": true
  },
  "metadata": {
    "file_size": 245760,
    "word_count": 1250,
    "character_count": 8750,
    "paragraph_count": 45
  }
}
```

### Analysis Operations

#### POST `/analysis/start`
Start contract analysis against a template.

**Request Body:**
```json
{
  "contract_id": "contract_123",
  "template_id": "template_456",
  "include_llm_analysis": true,
  "analysis_options": {
    "similarity_threshold": 0.5,
    "include_inconsequential": false,
    "batch_size": 15
  }
}
```

**Response (Success - 202):**
```json
{
  "success": true,
  "message": "Analysis started successfully",
  "analysis_id": "analysis_789",
  "contract_id": "contract_123",
  "template_id": "template_456",
  "estimated_duration": 120,
  "status": "processing"
}
```

#### GET `/analysis/{analysis_id}`
Get analysis status and results.

**Response (In Progress - 202):**
```json
{
  "success": true,
  "analysis_id": "analysis_789",
  "status": "processing",
  "progress": 75,
  "estimated_remaining": 30,
  "current_step": "LLM analysis"
}
```

**Response (Complete - 200):**
```json
{
  "success": true,
  "analysis_id": "analysis_789",
  "status": "completed",
  "contract_id": "contract_123",
  "template_id": "template_456",
  "analysis_timestamp": "2025-01-18T10:35:00Z",
  "similarity_score": 87.5,
  "total_changes": 15,
  "processing_time": 125.4,
  "overall_risk_level": "MEDIUM",
  "summary": {
    "critical_changes": 2,
    "significant_changes": 8,
    "inconsequential_changes": 5
  }
}
```

#### GET `/analysis/{analysis_id}/changes`
Get detailed analysis changes.

**Query Parameters:**
- `classification`: Filter by classification (CRITICAL, SIGNIFICANT, INCONSEQUENTIAL)
- `category`: Filter by category (FINANCIAL, LEGAL, BUSINESS, ADMINISTRATIVE)
- `limit`: Number of results (default: 50)
- `offset`: Results offset (default: 0)

**Response:**
```json
{
  "success": true,
  "analysis_id": "analysis_789",
  "changes": [
    {
      "change_id": "change_001",
      "change_type": "MODIFICATION",
      "classification": "CRITICAL",
      "category": "FINANCIAL",
      "deleted_text": "Payment terms: Net 30 days",
      "inserted_text": "Payment terms: Net 60 days",
      "explanation": "Payment terms extended from 30 to 60 days, significantly impacting cash flow",
      "confidence": 0.95,
      "risk_impact": "High impact on cash flow and working capital requirements",
      "recommendation": "Legal review required - significant financial impact",
      "position": 1250
    }
  ],
  "total_changes": 15,
  "filters_applied": {
    "classification": null,
    "category": null
  }
}
```

### Report Generation

#### POST `/reports/generate`
Generate analysis reports in multiple formats.

**Request Body:**
```json
{
  "analysis_id": "analysis_789",
  "formats": ["excel", "pdf", "word"],
  "options": {
    "include_summary": true,
    "include_details": true,
    "include_recommendations": true,
    "custom_title": "Q1 2025 Service Agreement Analysis"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Reports generated successfully",
  "analysis_id": "analysis_789",
  "reports": {
    "excel": {
      "filename": "Q1_2025_Service_Agreement_Analysis.xlsx",
      "download_url": "/api/reports/download/excel_report_123",
      "file_size": 156780
    },
    "pdf": {
      "filename": "Q1_2025_Service_Agreement_Analysis.pdf",
      "download_url": "/api/reports/download/pdf_report_124",
      "file_size": 234560
    },
    "word": {
      "filename": "Q1_2025_Service_Agreement_Analysis.docx",
      "download_url": "/api/reports/download/word_report_125",
      "file_size": 198450
    }
  },
  "generation_time": 5.2
}
```

#### GET `/reports/download/{report_id}`
Download a generated report file.

**Response:** Binary file download with appropriate Content-Type headers.

**Headers:**
- `Content-Type`: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (Excel)
- `Content-Type`: `application/pdf` (PDF)  
- `Content-Type`: `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (Word)
- `Content-Disposition`: `attachment; filename="report.xlsx"`

### Template Management

#### GET `/templates`
List available contract templates.

**Response:**
```json
{
  "success": true,
  "templates": [
    {
      "id": "template_sow_standard",
      "name": "Standard Statement of Work",
      "category": "SOW",
      "vendor": "Generic",
      "filename": "TYPE_SOW_Standard_v1.docx",
      "file_size": 125680,
      "created_date": "2024-12-01T00:00:00Z",
      "usage_count": 45
    },
    {
      "id": "template_capgemini_sow",
      "name": "Capgemini SOW Template",
      "category": "SOW", 
      "vendor": "Capgemini",
      "filename": "VENDOR_CAPGEMINI_SOW_v1.docx",
      "file_size": 134590,
      "created_date": "2024-12-01T00:00:00Z",
      "usage_count": 12
    }
  ],
  "total": 2
}
```

### Prompt Management

#### GET `/prompts`
Get available analysis prompts and their current configuration.

**Response:**
```json
{
  "success": true,
  "prompts": {
    "analysis_prompt": {
      "name": "Contract Analysis Prompt",
      "description": "Main prompt for contract change analysis",
      "version": "2.1",
      "last_updated": "2025-01-15T00:00:00Z"
    },
    "classification_prompt": {
      "name": "Change Classification Prompt", 
      "description": "Prompt for classifying change significance",
      "version": "1.5",
      "last_updated": "2025-01-10T00:00:00Z"
    }
  }
}
```

## Error Handling

All API endpoints follow consistent error response format:

### Error Response Format
```json
{
  "success": false,
  "error": "Human readable error message",
  "error_code": "SPECIFIC_ERROR_CODE",
  "details": {
    "field": "Additional error details",
    "suggestion": "How to fix the error"
  },
  "timestamp": "2025-01-18T10:30:00Z",
  "request_id": "req_abc123"
}
```

### Common Error Codes

#### 400 Bad Request
- `INVALID_FILE_TYPE`: Unsupported file format
- `FILE_TOO_LARGE`: File exceeds size limit
- `MISSING_REQUIRED_FIELD`: Required parameter missing
- `INVALID_PARAMETER`: Parameter format incorrect

#### 404 Not Found
- `CONTRACT_NOT_FOUND`: Contract ID not found
- `ANALYSIS_NOT_FOUND`: Analysis ID not found
- `TEMPLATE_NOT_FOUND`: Template ID not found

#### 422 Unprocessable Entity
- `VALIDATION_FAILED`: Request validation failed
- `INVALID_CONTRACT_STATE`: Contract not in correct state for operation

#### 500 Internal Server Error
- `PROCESSING_ERROR`: Error during analysis processing
- `LLM_ERROR`: Error communicating with LLM provider
- `STORAGE_ERROR`: File system or storage error

### Example Error Response
```json
{
  "success": false,
  "error": "Invalid file type. Only .docx and .doc files are supported.",
  "error_code": "INVALID_FILE_TYPE",
  "details": {
    "uploaded_extension": ".pdf",
    "allowed_extensions": [".docx", ".doc"],
    "suggestion": "Please upload a Microsoft Word document (.docx or .doc)"
  },
  "timestamp": "2025-01-18T10:30:00Z",
  "request_id": "req_abc123"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. For production deployments, consider implementing:
- Request rate limiting per IP
- File upload size and frequency limits
- LLM API request throttling

## Authentication

The current version does not implement authentication. For production use, consider:
- API key authentication
- JWT token authentication
- OAuth 2.0 integration
- Basic HTTP authentication

## SDK and Integration Examples

### Python SDK Example
```python
import requests
import json

class ContractAnalyzerClient:
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
    
    def upload_contract(self, file_path, name=None):
        """Upload a contract file"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'name': name} if name else {}
            response = requests.post(f"{self.base_url}/contracts/upload", 
                                   files=files, data=data)
        return response.json()
    
    def start_analysis(self, contract_id, template_id):
        """Start contract analysis"""
        data = {
            "contract_id": contract_id,
            "template_id": template_id,
            "include_llm_analysis": True
        }
        response = requests.post(f"{self.base_url}/analysis/start", 
                               json=data)
        return response.json()
    
    def get_analysis_results(self, analysis_id):
        """Get analysis results"""
        response = requests.get(f"{self.base_url}/analysis/{analysis_id}")
        return response.json()

# Usage example
client = ContractAnalyzerClient()

# Upload contract
result = client.upload_contract("contract.docx", "Q1 Service Agreement")
contract_id = result["contract"]["id"]

# Start analysis
analysis = client.start_analysis(contract_id, "template_sow_standard")
analysis_id = analysis["analysis_id"]

# Get results
results = client.get_analysis_results(analysis_id)
```

### JavaScript SDK Example
```javascript
class ContractAnalyzerClient {
    constructor(baseUrl = 'http://localhost:5000/api') {
        this.baseUrl = baseUrl;
    }

    async uploadContract(file, name = null) {
        const formData = new FormData();
        formData.append('file', file);
        if (name) formData.append('name', name);

        const response = await fetch(`${this.baseUrl}/contracts/upload`, {
            method: 'POST',
            body: formData
        });
        return response.json();
    }

    async startAnalysis(contractId, templateId) {
        const response = await fetch(`${this.baseUrl}/analysis/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contract_id: contractId,
                template_id: templateId,
                include_llm_analysis: true
            })
        });
        return response.json();
    }

    async getAnalysisResults(analysisId) {
        const response = await fetch(`${this.baseUrl}/analysis/${analysisId}`);
        return response.json();
    }
}

// Usage example
const client = new ContractAnalyzerClient();

// Upload and analyze
document.getElementById('upload').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    const uploadResult = await client.uploadContract(file, 'My Contract');
    const contractId = uploadResult.contract.id;
    
    const analysis = await client.startAnalysis(contractId, 'template_sow_standard');
    const results = await client.getAnalysisResults(analysis.analysis_id);
    
    console.log('Analysis complete:', results);
});
```

## WebSocket Events (Future)

The API is designed to support real-time updates via WebSocket connections:

```javascript
// Future WebSocket support
const ws = new WebSocket('ws://localhost:5000/api/ws');

ws.on('analysis_progress', (data) => {
    console.log(`Analysis ${data.analysis_id}: ${data.progress}% complete`);
});

ws.on('analysis_complete', (data) => {
    console.log(`Analysis ${data.analysis_id} completed with ${data.total_changes} changes`);
});
```

## OpenAPI Specification

The API follows OpenAPI 3.0 specification. A complete OpenAPI spec file will be available at `/api/openapi.json` in future versions for automated client generation.