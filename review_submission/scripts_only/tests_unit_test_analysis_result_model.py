"""
Unit tests for AnalysisResult and Change domain models
"""

import pytest
from datetime import datetime

from app.core.models.analysis_result import (
    AnalysisResult, 
    Change, 
    ChangeClassification, 
    ChangeType,
    create_change_from_diff
)


class TestChange:
    """Test suite for Change model"""

    def test_change_creation(self):
        """Test creating a change object"""
        change = Change(
            change_id="change_001",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.SIGNIFICANT,
            deleted_text="old text",
            inserted_text="new text",
            explanation="Text was updated"
        )
        
        assert change.change_id == "change_001"
        assert change.change_type == ChangeType.MODIFICATION
        assert change.classification == ChangeClassification.SIGNIFICANT
        assert change.deleted_text == "old text"
        assert change.inserted_text == "new text"
        assert change.explanation == "Text was updated"

    def test_change_validation(self):
        """Test change validation"""
        # Missing change_id should raise error
        with pytest.raises(ValueError, match="Change ID is required"):
            Change(
                change_id="",
                change_type=ChangeType.MODIFICATION,
                classification=ChangeClassification.SIGNIFICANT
            )

    def test_change_type_conversion(self):
        """Test automatic conversion of string change types"""
        change = Change(
            change_id="change_001",
            change_type="modification",  # String instead of enum
            classification=ChangeClassification.SIGNIFICANT
        )
        
        assert change.change_type == ChangeType.MODIFICATION

    def test_classification_conversion(self):
        """Test automatic conversion of string classifications"""
        change = Change(
            change_id="change_001",
            change_type=ChangeType.MODIFICATION,
            classification="CRITICAL"  # String instead of enum
        )
        
        assert change.classification == ChangeClassification.CRITICAL

    def test_is_critical(self):
        """Test is_critical method"""
        critical_change = Change(
            change_id="change_001",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.CRITICAL
        )
        
        significant_change = Change(
            change_id="change_002",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.SIGNIFICANT
        )
        
        assert critical_change.is_critical()
        assert not significant_change.is_critical()

    def test_is_significant(self):
        """Test is_significant method"""
        significant_change = Change(
            change_id="change_001",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.SIGNIFICANT
        )
        
        critical_change = Change(
            change_id="change_002",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.CRITICAL
        )
        
        assert significant_change.is_significant()
        assert not critical_change.is_significant()

    def test_is_content_change(self):
        """Test is_content_change method"""
        content_change = Change(
            change_id="change_001",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.SIGNIFICANT,
            deleted_text="old text",
            inserted_text="new text"
        )
        
        empty_change = Change(
            change_id="change_002",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.INCONSEQUENTIAL,
            deleted_text="",
            inserted_text=""
        )
        
        assert content_change.is_content_change()
        assert not empty_change.is_content_change()

    def test_get_change_summary(self):
        """Test get_change_summary method"""
        insertion = Change(
            change_id="change_001",
            change_type=ChangeType.INSERTION,
            classification=ChangeClassification.SIGNIFICANT,
            inserted_text="This is new text that was added to the document"
        )
        
        deletion = Change(
            change_id="change_002",
            change_type=ChangeType.DELETION,
            classification=ChangeClassification.SIGNIFICANT,
            deleted_text="This text was removed from the document"
        )
        
        modification = Change(
            change_id="change_003",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.SIGNIFICANT,
            deleted_text="old text here",
            inserted_text="new text here"
        )
        
        assert insertion.get_change_summary().startswith("Added:")
        assert deletion.get_change_summary().startswith("Removed:")
        assert modification.get_change_summary().startswith("Changed:")

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization"""
        change = Change(
            change_id="change_001",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.CRITICAL,
            deleted_text="old text",
            inserted_text="new text",
            explanation="Important change",
            confidence_score=0.95,
            risk_impact="High impact change",
            recommendation="Review immediately"
        )
        
        # Serialize to dict
        data = change.to_dict()
        
        # Deserialize from dict
        restored_change = Change.from_dict(data)
        
        assert restored_change.change_id == change.change_id
        assert restored_change.change_type == change.change_type
        assert restored_change.classification == change.classification
        assert restored_change.deleted_text == change.deleted_text
        assert restored_change.inserted_text == change.inserted_text
        assert restored_change.explanation == change.explanation
        assert restored_change.confidence_score == change.confidence_score


class TestAnalysisResult:
    """Test suite for AnalysisResult model"""

    def test_analysis_result_creation(self):
        """Test creating an analysis result"""
        analysis = AnalysisResult(
            analysis_id="analysis_001",
            contract_id="contract_001", 
            template_id="template_001",
            analysis_timestamp=datetime.now(),
            similarity_score=0.85
        )
        
        assert analysis.analysis_id == "analysis_001"
        assert analysis.contract_id == "contract_001"
        assert analysis.template_id == "template_001"
        assert analysis.similarity_score == 0.85
        assert analysis.total_changes == 0  # No changes added yet
        assert analysis.overall_risk_level == "LOW"  # Default for no changes

    def test_analysis_result_validation(self):
        """Test analysis result validation"""
        # Missing analysis_id should raise error
        with pytest.raises(ValueError, match="Analysis ID is required"):
            AnalysisResult(
                analysis_id="",
                contract_id="contract_001",
                template_id="template_001",
                analysis_timestamp=datetime.now()
            )

    def test_add_change(self):
        """Test adding changes to analysis result"""
        analysis = AnalysisResult(
            analysis_id="analysis_001",
            contract_id="contract_001",
            template_id="template_001",
            analysis_timestamp=datetime.now()
        )
        
        change = Change(
            change_id="change_001",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.CRITICAL,
            deleted_text="old",
            inserted_text="new"
        )
        
        analysis.add_change(change)
        
        assert analysis.total_changes == 1
        assert len(analysis.changes) == 1
        assert analysis.overall_risk_level == "HIGH"  # Should be high due to critical change

    def test_get_critical_changes(self):
        """Test getting critical changes"""
        analysis = AnalysisResult(
            analysis_id="analysis_001",
            contract_id="contract_001",
            template_id="template_001", 
            analysis_timestamp=datetime.now()
        )
        
        critical_change = Change(
            change_id="change_001",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.CRITICAL
        )
        
        significant_change = Change(
            change_id="change_002",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.SIGNIFICANT
        )
        
        analysis.add_change(critical_change)
        analysis.add_change(significant_change)
        
        critical_changes = analysis.get_critical_changes()
        assert len(critical_changes) == 1
        assert critical_changes[0].change_id == "change_001"

    def test_get_significant_changes(self):
        """Test getting significant changes"""
        analysis = AnalysisResult(
            analysis_id="analysis_001",
            contract_id="contract_001",
            template_id="template_001",
            analysis_timestamp=datetime.now()
        )
        
        critical_change = Change(
            change_id="change_001",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.CRITICAL
        )
        
        significant_change = Change(
            change_id="change_002",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.SIGNIFICANT
        )
        
        analysis.add_change(critical_change)
        analysis.add_change(significant_change)
        
        significant_changes = analysis.get_significant_changes()
        assert len(significant_changes) == 1
        assert significant_changes[0].change_id == "change_002"

    def test_risk_level_calculation(self):
        """Test automatic risk level calculation"""
        analysis = AnalysisResult(
            analysis_id="analysis_001",
            contract_id="contract_001",
            template_id="template_001",
            analysis_timestamp=datetime.now()
        )
        
        # No changes = LOW risk
        assert analysis.overall_risk_level == "LOW"
        
        # Add significant changes = MEDIUM risk
        for i in range(3):
            change = Change(
                change_id=f"change_{i}",
                change_type=ChangeType.MODIFICATION,
                classification=ChangeClassification.SIGNIFICANT
            )
            analysis.add_change(change)
        
        assert analysis.overall_risk_level == "MEDIUM"
        
        # Add many significant changes = HIGH risk
        for i in range(3, 10):
            change = Change(
                change_id=f"change_{i}",
                change_type=ChangeType.MODIFICATION,
                classification=ChangeClassification.SIGNIFICANT
            )
            analysis.add_change(change)
        
        assert analysis.overall_risk_level == "HIGH"
        
        # Add critical change = HIGH risk (regardless of count)
        analysis_critical = AnalysisResult(
            analysis_id="analysis_002",
            contract_id="contract_001",
            template_id="template_001",
            analysis_timestamp=datetime.now()
        )
        
        critical_change = Change(
            change_id="critical_001",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.CRITICAL
        )
        analysis_critical.add_change(critical_change)
        
        assert analysis_critical.overall_risk_level == "HIGH"

    def test_get_similarity_percentage(self):
        """Test get_similarity_percentage method"""
        analysis = AnalysisResult(
            analysis_id="analysis_001",
            contract_id="contract_001",
            template_id="template_001",
            analysis_timestamp=datetime.now(),
            similarity_score=0.8567
        )
        
        assert analysis.get_similarity_percentage() == 85.7

    def test_is_high_risk(self):
        """Test is_high_risk method"""
        analysis = AnalysisResult(
            analysis_id="analysis_001",
            contract_id="contract_001",
            template_id="template_001",
            analysis_timestamp=datetime.now()
        )
        
        # Add critical change to make it high risk
        critical_change = Change(
            change_id="change_001",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.CRITICAL
        )
        analysis.add_change(critical_change)
        
        assert analysis.is_high_risk()

    def test_get_summary(self):
        """Test get_summary method"""
        timestamp = datetime.now()
        analysis = AnalysisResult(
            analysis_id="analysis_001",
            contract_id="contract_001",
            template_id="template_001",
            analysis_timestamp=timestamp,
            similarity_score=0.85,
            processing_time_seconds=2.5,
            llm_model_used="gpt-4o"
        )
        
        # Add some changes
        critical_change = Change(
            change_id="change_001",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.CRITICAL
        )
        significant_change = Change(
            change_id="change_002",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.SIGNIFICANT
        )
        analysis.add_change(critical_change)
        analysis.add_change(significant_change)
        
        summary = analysis.get_summary()
        
        assert summary["analysis_id"] == "analysis_001"
        assert summary["contract_id"] == "contract_001"
        assert summary["template_id"] == "template_001"
        assert summary["total_changes"] == 2
        assert summary["critical_changes"] == 1
        assert summary["significant_changes"] == 1
        assert summary["inconsequential_changes"] == 0
        assert summary["similarity_percentage"] == 85.0
        assert summary["overall_risk_level"] == "HIGH"
        assert summary["processing_time"] == 2.5
        assert summary["model_used"] == "gpt-4o"

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization"""
        timestamp = datetime.now()
        analysis = AnalysisResult(
            analysis_id="analysis_001",
            contract_id="contract_001",
            template_id="template_001",
            analysis_timestamp=timestamp,
            similarity_score=0.85,
            processing_time_seconds=2.5
        )
        
        # Add a change
        change = Change(
            change_id="change_001",
            change_type=ChangeType.MODIFICATION,
            classification=ChangeClassification.CRITICAL,
            explanation="Test change"
        )
        analysis.add_change(change)
        
        # Serialize to dict
        data = analysis.to_dict()
        
        # Deserialize from dict
        restored_analysis = AnalysisResult.from_dict(data)
        
        assert restored_analysis.analysis_id == analysis.analysis_id
        assert restored_analysis.contract_id == analysis.contract_id
        assert restored_analysis.template_id == analysis.template_id
        assert restored_analysis.similarity_score == analysis.similarity_score
        assert restored_analysis.total_changes == analysis.total_changes
        assert len(restored_analysis.changes) == len(analysis.changes)
        assert restored_analysis.changes[0].change_id == analysis.changes[0].change_id


class TestCreateChangeFromDiff:
    """Test suite for create_change_from_diff function"""

    def test_create_modification_change(self):
        """Test creating a modification change"""
        change = create_change_from_diff(
            change_id="change_001",
            deleted_text="old text",
            inserted_text="new text",
            explanation="Text was modified",
            classification="SIGNIFICANT"
        )
        
        assert change.change_id == "change_001"
        assert change.change_type == ChangeType.MODIFICATION
        assert change.classification == ChangeClassification.SIGNIFICANT
        assert change.deleted_text == "old text"
        assert change.inserted_text == "new text"
        assert change.explanation == "Text was modified"

    def test_create_insertion_change(self):
        """Test creating an insertion change"""
        change = create_change_from_diff(
            change_id="change_001",
            deleted_text="",
            inserted_text="new text",
            explanation="Text was added"
        )
        
        assert change.change_type == ChangeType.INSERTION
        assert change.inserted_text == "new text"
        assert change.deleted_text == ""

    def test_create_deletion_change(self):
        """Test creating a deletion change"""
        change = create_change_from_diff(
            change_id="change_001",
            deleted_text="old text",
            inserted_text="",
            explanation="Text was removed"
        )
        
        assert change.change_type == ChangeType.DELETION
        assert change.deleted_text == "old text"
        assert change.inserted_text == ""