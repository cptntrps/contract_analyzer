"""
Unit tests for Contract domain model
"""

import pytest
from datetime import datetime
from pathlib import Path

from app.core.models.contract import Contract, validate_contract_file


class TestContract:
    """Test suite for Contract model"""

    def test_create_from_upload(self):
        """Test creating contract from upload"""
        contract = Contract.create_from_upload(
            contract_id="test_001",
            filename="test.docx",
            original_filename="original_test.docx",
            file_path="/test/path.docx",
            file_size=1024
        )
        
        assert contract.id == "test_001"
        assert contract.filename == "test.docx"
        assert contract.original_filename == "original_test.docx"
        assert contract.file_path == "/test/path.docx"
        assert contract.file_size == 1024
        assert contract.status == "uploaded"
        assert isinstance(contract.upload_timestamp, datetime)

    def test_init_validation(self):
        """Test contract initialization validation"""
        # Missing ID should raise error
        with pytest.raises(ValueError, match="Contract ID is required"):
            Contract(
                id="",
                filename="test.docx",
                original_filename="test.docx",
                file_path="/test/path.docx",
                file_size=1024,
                upload_timestamp=datetime.now()
            )
        
        # Missing filename should raise error
        with pytest.raises(ValueError, match="Contract filename is required"):
            Contract(
                id="test_001",
                filename="",
                original_filename="test.docx",
                file_path="/test/path.docx",
                file_size=1024,
                upload_timestamp=datetime.now()
            )

    def test_mark_processing(self):
        """Test marking contract as processing"""
        contract = Contract.create_from_upload(
            contract_id="test_001",
            filename="test.docx",
            original_filename="test.docx",
            file_path="/test/path.docx",
            file_size=1024
        )
        
        contract.mark_processing()
        assert contract.status == "processing"

    def test_mark_analyzed(self):
        """Test marking contract as analyzed"""
        contract = Contract.create_from_upload(
            contract_id="test_001",
            filename="test.docx",
            original_filename="test.docx",
            file_path="/test/path.docx",
            file_size=1024
        )
        
        contract.mark_analyzed(
            template_used="template.docx",
            changes_count=5,
            similarity_score=0.85,
            risk_level="MEDIUM"
        )
        
        assert contract.status == "analyzed"
        assert contract.template_used == "template.docx"
        assert contract.changes_count == 5
        assert contract.similarity_score == 0.85
        assert contract.risk_level == "MEDIUM"
        assert isinstance(contract.analysis_timestamp, datetime)

    def test_mark_error(self):
        """Test marking contract with error"""
        contract = Contract.create_from_upload(
            contract_id="test_001",
            filename="test.docx",
            original_filename="test.docx",
            file_path="/test/path.docx",
            file_size=1024
        )
        
        contract.mark_error("Test error message")
        
        assert contract.status == "error"
        assert contract.metadata["error_message"] == "Test error message"
        assert "error_timestamp" in contract.metadata

    def test_is_analyzed(self):
        """Test is_analyzed method"""
        contract = Contract.create_from_upload(
            contract_id="test_001",
            filename="test.docx",
            original_filename="test.docx",
            file_path="/test/path.docx",
            file_size=1024
        )
        
        assert not contract.is_analyzed()
        
        contract.mark_analyzed(
            template_used="template.docx",
            changes_count=5,
            similarity_score=0.85,
            risk_level="LOW"
        )
        
        assert contract.is_analyzed()

    def test_is_high_risk(self):
        """Test is_high_risk method"""
        contract = Contract.create_from_upload(
            contract_id="test_001",
            filename="test.docx",
            original_filename="test.docx",
            file_path="/test/path.docx",
            file_size=1024
        )
        
        contract.mark_analyzed(
            template_used="template.docx",
            changes_count=5,
            similarity_score=0.85,
            risk_level="HIGH"
        )
        
        assert contract.is_high_risk()
        
        contract.risk_level = "LOW"
        assert not contract.is_high_risk()

    def test_get_file_extension(self):
        """Test get_file_extension method"""
        contract = Contract.create_from_upload(
            contract_id="test_001",
            filename="test.docx",
            original_filename="test.docx",
            file_path="/test/path.docx",
            file_size=1024
        )
        
        assert contract.get_file_extension() == ".docx"

    def test_get_display_name(self):
        """Test get_display_name method"""
        contract = Contract.create_from_upload(
            contract_id="test_001",
            filename="hashed_filename.docx",
            original_filename="My Contract.docx",
            file_path="/test/path.docx",
            file_size=1024
        )
        
        assert contract.get_display_name() == "My Contract.docx"

    def test_get_summary(self):
        """Test get_summary method"""
        contract = Contract.create_from_upload(
            contract_id="test_001",
            filename="test.docx",
            original_filename="My Contract.docx",
            file_path="/test/path.docx",
            file_size=1024
        )
        
        contract.mark_analyzed(
            template_used="template.docx",
            changes_count=5,
            similarity_score=0.85,
            risk_level="MEDIUM"
        )
        
        summary = contract.get_summary()
        
        assert summary["id"] == "test_001"
        assert summary["filename"] == "My Contract.docx"
        assert summary["status"] == "analyzed"
        assert summary["changes_count"] == 5
        assert summary["similarity_score"] == 85.0
        assert summary["risk_level"] == "MEDIUM"
        assert "upload_date" in summary
        assert "analysis_date" in summary

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization"""
        contract = Contract.create_from_upload(
            contract_id="test_001",
            filename="test.docx",
            original_filename="My Contract.docx",
            file_path="/test/path.docx",
            file_size=1024
        )
        
        contract.mark_analyzed(
            template_used="template.docx",
            changes_count=5,
            similarity_score=0.85,
            risk_level="HIGH"
        )
        
        # Serialize to dict
        data = contract.to_dict()
        
        # Deserialize from dict
        restored_contract = Contract.from_dict(data)
        
        assert restored_contract.id == contract.id
        assert restored_contract.filename == contract.filename
        assert restored_contract.status == contract.status
        assert restored_contract.changes_count == contract.changes_count
        assert restored_contract.similarity_score == contract.similarity_score
        assert restored_contract.risk_level == contract.risk_level


class TestValidateContractFile:
    """Test suite for validate_contract_file function"""

    def test_validate_existing_docx_file(self, test_docx_file):
        """Test validation of existing DOCX file"""
        # The test_docx_file fixture creates a real DOCX file
        assert validate_contract_file(str(test_docx_file)) == True

    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file"""
        assert validate_contract_file("/nonexistent/file.docx") == False

    def test_validate_wrong_extension(self, tmp_path):
        """Test validation of file with wrong extension"""
        # Create a test file with wrong extension
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        assert validate_contract_file(str(test_file)) == False

    def test_validate_invalid_path(self):
        """Test validation with invalid path"""
        assert validate_contract_file("") == False
        assert validate_contract_file(None) == False