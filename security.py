"""
Security validation and sanitization module for Contract Analyzer
Provides comprehensive input validation and security checks
"""

import os
import re
import mimetypes
import hashlib
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from config import config
import time
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
    magic = None

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Base security validation error"""
    pass

class FileValidationError(SecurityError):
    """File validation error"""
    pass

class PathTraversalError(SecurityError):
    """Path traversal attack detected"""
    pass

class ContentValidationError(SecurityError):
    """Content validation error"""
    pass

class SecurityValidator:
    """
    Comprehensive security validator for file uploads and user input
    """
    
    def __init__(self):
        self.allowed_extensions = set(config.ALLOWED_EXTENSIONS)
        self.max_file_size = config.MAX_CONTENT_LENGTH
        self.max_filename_length = config.MAX_FILENAME_LENGTH
        self.secure_filename_enabled = config.SECURE_FILENAME_ENABLED
        self.path_traversal_protection = config.PATH_TRAVERSAL_PROTECTION
        self.file_validation_enabled = config.FILE_VALIDATION_ENABLED
        self.content_type_validation = config.CONTENT_TYPE_VALIDATION
        
        # Dangerous filename patterns
        self.dangerous_patterns = [
            r'\.\.[\\/]',  # Path traversal attempts
            r'^\.\.[\\/]',  # Path traversal at start
            r'[\\/]\.\.[\\/]',  # Path traversal in middle
            r'[\\/]\.\.$',  # Path traversal at end
            r'[<>:"|?*]',  # Windows forbidden characters
            r'[\x00-\x1f\x7f-\x9f]',  # Control characters
            r'^\.',  # Hidden files (starting with dot)
            r'^\s',  # Leading whitespace
            r'\s$',  # Trailing whitespace
        ]
        
        # Suspicious filename patterns
        self.suspicious_patterns = [
            r'\.exe$',  # Executable files
            r'\.bat$',  # Batch files
            r'\.cmd$',  # Command files
            r'\.com$',  # COM files
            r'\.scr$',  # Screen saver files
            r'\.pif$',  # Program information files
            r'\.vbs$',  # VB Script files
            r'\.js$',   # JavaScript files
            r'\.jar$',  # Java archives
            r'\.php$',  # PHP files
            r'\.asp$',  # ASP files
            r'\.jsp$',  # JSP files
        ]
        
        # Expected MIME types for allowed extensions
        self.expected_mime_types = {
            'docx': [
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/octet-stream',  # Sometimes detected as generic binary
                'application/zip',  # DOCX is basically a zip file
            ]
        }
        
        logger.info("Security validator initialized")
    
    def validate_filename(self, filename: str) -> str:
        """
        Validate and sanitize filename with comprehensive security checks
        
        Args:
            filename: Original filename
            
        Returns:
            str: Sanitized filename
            
        Raises:
            FileValidationError: If filename is invalid or dangerous
        """
        if not filename:
            raise FileValidationError("Empty filename not allowed")
        
        # Check filename length
        if len(filename) > self.max_filename_length:
            raise FileValidationError(f"Filename too long (max {self.max_filename_length} characters)")
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                raise FileValidationError(f"Dangerous filename pattern detected: {filename}")
        
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                raise FileValidationError(f"Suspicious filename pattern detected: {filename}")
        
        # Validate file extension
        if not self._has_allowed_extension(filename):
            allowed_str = ', '.join(self.allowed_extensions)
            raise FileValidationError(f"File extension not allowed. Allowed: {allowed_str}")
        
        # Sanitize filename if enabled
        if self.secure_filename_enabled:
            sanitized = secure_filename(filename)
            if not sanitized:
                raise FileValidationError("Filename could not be sanitized")
            
            # Ensure extension is preserved
            original_ext = self._get_file_extension(filename)
            sanitized_ext = self._get_file_extension(sanitized)
            
            if original_ext != sanitized_ext:
                # Re-add the original extension
                sanitized = f"{sanitized.rsplit('.', 1)[0] if '.' in sanitized else sanitized}.{original_ext}"
            
            return sanitized
        
        return filename
    
    def validate_file_upload(self, file: FileStorage) -> Dict[str, Any]:
        """
        Comprehensive file upload validation
        
        Args:
            file: Uploaded file object
            
        Returns:
            Dict: Validation results and metadata
            
        Raises:
            FileValidationError: If file validation fails
        """
        if not file:
            raise FileValidationError("No file provided")
        
        if not file.filename:
            raise FileValidationError("No filename provided")
        
        # Validate filename
        sanitized_filename = self.validate_filename(file.filename)
        
        # Check file size
        if hasattr(file, 'content_length') and file.content_length:
            if file.content_length > self.max_file_size:
                raise FileValidationError(f"File too large (max {self.max_file_size // (1024*1024)}MB)")
        
        # Read file content for validation
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        actual_size = len(file_content)
        if actual_size > self.max_file_size:
            raise FileValidationError(f"File too large (max {self.max_file_size // (1024*1024)}MB)")
        
        if actual_size == 0:
            raise FileValidationError("Empty file not allowed")
        
        # Validate content type
        if self.content_type_validation:
            self._validate_content_type(file, file_content, sanitized_filename)
        
        # Calculate file hash for integrity
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        return {
            'original_filename': file.filename,
            'sanitized_filename': sanitized_filename,
            'file_size': actual_size,
            'content_type': file.content_type,
            'file_hash': file_hash,
            'validation_passed': True
        }
    
    def validate_path(self, path: str, base_directory: str) -> str:
        """
        Validate file path to prevent directory traversal attacks
        
        Args:
            path: File path to validate
            base_directory: Base directory that files should be within
            
        Returns:
            str: Validated absolute path
            
        Raises:
            PathTraversalError: If path traversal is detected
        """
        if not self.path_traversal_protection:
            return path
        
        try:
            # Normalize paths
            base_path = Path(base_directory).resolve()
            file_path = Path(base_directory, path).resolve()
            
            # Check if file path is within base directory
            if not str(file_path).startswith(str(base_path)):
                raise PathTraversalError(f"Path traversal detected: {path}")
            
            # Additional checks for dangerous path components
            path_parts = Path(path).parts
            for part in path_parts:
                if part in ['..', '.', '']:
                    continue
                if any(re.search(pattern, part, re.IGNORECASE) for pattern in self.dangerous_patterns):
                    raise PathTraversalError(f"Dangerous path component: {part}")
            
            return str(file_path)
            
        except Exception as e:
            if isinstance(e, PathTraversalError):
                raise
            raise PathTraversalError(f"Path validation failed: {e}")
    
    def sanitize_string_input(self, input_string: str, max_length: int = 1000) -> str:
        """
        Sanitize string input to prevent various attacks
        
        Args:
            input_string: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            str: Sanitized string
            
        Raises:
            ContentValidationError: If input is invalid
        """
        if not isinstance(input_string, str):
            raise ContentValidationError("Input must be a string")
        
        if len(input_string) > max_length:
            raise ContentValidationError(f"Input too long (max {max_length} characters)")
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', input_string)
        
        # Remove potentially dangerous patterns
        dangerous_patterns = [
            r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'data:',  # Data URLs
            r'vbscript:',  # VBScript URLs
            r'on\w+\s*=',  # Event handlers
            r'<%.*?%>',  # Server-side includes
            r'<\?.*?\?>',  # PHP tags
        ]
        
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        return sanitized
    
    def validate_json_input(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate JSON input for API requests
        
        Args:
            json_data: JSON data to validate
            
        Returns:
            Dict: Validated JSON data
            
        Raises:
            ContentValidationError: If JSON is invalid
        """
        if not isinstance(json_data, dict):
            raise ContentValidationError("JSON input must be an object")
        
        # Recursively validate all string values
        def validate_dict_values(obj, path=""):
            if isinstance(obj, dict):
                validated = {}
                for key, value in obj.items():
                    # Validate key
                    if not isinstance(key, str):
                        raise ContentValidationError(f"Invalid key type at {path}: {type(key)}")
                    
                    validated_key = self.sanitize_string_input(key, 100)
                    validated[validated_key] = validate_dict_values(value, f"{path}.{key}")
                return validated
            elif isinstance(obj, list):
                return [validate_dict_values(item, f"{path}[{i}]") for i, item in enumerate(obj)]
            elif isinstance(obj, str):
                return self.sanitize_string_input(obj, 10000)
            elif isinstance(obj, (int, float, bool)) or obj is None:
                return obj
            else:
                raise ContentValidationError(f"Invalid value type at {path}: {type(obj)}")
        
        return validate_dict_values(json_data)
    
    def _has_allowed_extension(self, filename: str) -> bool:
        """Check if filename has allowed extension"""
        extension = self._get_file_extension(filename)
        return extension in self.allowed_extensions
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase"""
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    def _validate_content_type(self, file: FileStorage, content: bytes, filename: str) -> None:
        """
        Validate file content type matches expected type for extension
        
        Args:
            file: File object
            content: File content bytes
            filename: Sanitized filename
            
        Raises:
            FileValidationError: If content type validation fails
        """
        extension = self._get_file_extension(filename)
        expected_types = self.expected_mime_types.get(extension, [])
        
        if not expected_types:
            return  # No specific validation for this extension
        
        # Check declared content type
        declared_type = file.content_type
        if declared_type not in expected_types:
            logger.warning(f"Declared content type {declared_type} doesn't match expected for .{extension}")
        
        # Check actual content type using python-magic if available
        if HAS_MAGIC:
            try:
                actual_type = magic.from_buffer(content, mime=True)
                if actual_type not in expected_types:
                    # Be more lenient with actual content type detection
                    logger.warning(f"Detected content type {actual_type} for file {filename}")
            except Exception as e:
                logger.warning(f"Could not detect content type: {e}")
        else:
            logger.debug("python-magic not available, skipping content type detection")
        
        # For DOCX files, check for ZIP signature
        if extension == 'docx':
            if not content.startswith(b'PK'):
                raise FileValidationError("Invalid DOCX file: missing ZIP signature")
    
    def get_security_headers(self) -> Dict[str, str]:
        """
        Get security headers for HTTP responses
        
        Returns:
            Dict: Security headers
        """
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                "img-src 'self' data:; "
                "font-src 'self' https://cdnjs.cloudflare.com; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            ),
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'
        }
    
    def audit_log(self, event: str, details: Dict[str, Any], user_id: str = "anonymous") -> None:
        """
        Log security-related events for auditing
        
        Args:
            event: Event type
            details: Event details
            user_id: User identifier
        """
        # Try to get IP address from Flask request context if available
        try:
            from flask import request
            ip_address = request.remote_addr
        except:
            ip_address = 'unknown'
        
        audit_entry = {
            'timestamp': time.time(),
            'event': event,
            'user_id': user_id,
            'details': details,
            'ip_address': ip_address
        }
        
        logger.info(f"SECURITY_AUDIT: {event} - {details}")
        
        # In production, send to SIEM or security log system
        # For now, just log to file
        try:
            audit_file = Path('security_audit.log')
            with open(audit_file, 'a') as f:
                f.write(f"{audit_entry}\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

# Global security validator instance
security_validator = SecurityValidator()

def validate_file_upload(file: FileStorage) -> Dict[str, Any]:
    """Convenience function for file upload validation"""
    return security_validator.validate_file_upload(file)

def validate_path(path: str, base_directory: str) -> str:
    """Convenience function for path validation"""
    return security_validator.validate_path(path, base_directory)

def sanitize_input(input_string: str, max_length: int = 1000) -> str:
    """Convenience function for string sanitization"""
    return security_validator.sanitize_string_input(input_string, max_length)

def validate_json(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for JSON validation"""
    return security_validator.validate_json_input(json_data)

def get_security_headers() -> Dict[str, str]:
    """Convenience function for security headers"""
    return security_validator.get_security_headers()

def audit_security_event(event: str, details: Dict[str, Any], user_id: str = "anonymous") -> None:
    """Convenience function for security auditing"""
    return security_validator.audit_log(event, details, user_id) 