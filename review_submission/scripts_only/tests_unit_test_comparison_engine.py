"""
Unit tests for ComparisonEngine service
"""

import pytest
from unittest.mock import Mock, patch
from difflib import SequenceMatcher

from app.core.services.comparison_engine import ComparisonEngine
from app.core.models.analysis_result import Change, ChangeType, ChangeClassification


class TestComparisonEngine:
    """Test suite for ComparisonEngine service"""

    def test_init(self):
        """Test engine initialization"""
        engine = ComparisonEngine()
        assert engine is not None

    def test_compare_texts_identical(self):
        """Test comparison of identical texts"""
        engine = ComparisonEngine()
        
        text = "This is identical text"
        changes = engine.compare_texts(text, text)
        
        assert isinstance(changes, list)
        assert len(changes) == 0

    def test_compare_texts_different(self, sample_template_text, sample_contract_text):
        """Test comparison of different texts"""
        engine = ComparisonEngine()
        
        changes = engine.compare_texts(sample_template_text, sample_contract_text)
        
        assert isinstance(changes, list)
        assert len(changes) > 0
        
        # Check that changes contain proper operations
        for change in changes:
            assert isinstance(change, tuple)
            assert len(change) == 2
            assert change[0] in ['delete', 'insert', 'equal', 'replace']
            assert isinstance(change[1], str)

    def test_compare_texts_empty(self):
        """Test comparison with empty texts"""
        engine = ComparisonEngine()
        
        # Both empty
        changes = engine.compare_texts("", "")
        assert isinstance(changes, list)
        assert len(changes) == 0
        
        # One empty
        changes = engine.compare_texts("", "new text")
        assert len(changes) > 0
        assert any(op == 'insert' for op, _ in changes)
        
        changes = engine.compare_texts("old text", "")
        assert len(changes) > 0
        assert any(op == 'delete' for op, _ in changes)

    def test_calculate_similarity_identical(self):
        """Test similarity calculation with identical texts"""
        engine = ComparisonEngine()
        
        text = "This is identical text"
        similarity = engine.calculate_similarity(text, text)
        
        assert similarity == 1.0

    def test_calculate_similarity_different(self):
        """Test similarity calculation with different texts"""
        engine = ComparisonEngine()
        
        text1 = "This is the original text"
        text2 = "This is completely different content"
        similarity = engine.calculate_similarity(text1, text2)
        
        assert 0.0 <= similarity <= 1.0
        assert similarity < 1.0

    def test_calculate_similarity_similar(self):
        """Test similarity calculation with similar texts"""
        engine = ComparisonEngine()
        
        text1 = "This is the original text"
        text2 = "This is the original content"  # Only one word different
        similarity = engine.calculate_similarity(text1, text2)
        
        assert 0.5 <= similarity <= 1.0

    def test_calculate_similarity_empty(self):
        """Test similarity calculation with empty texts"""
        engine = ComparisonEngine()
        
        # Both empty should be 100% similar
        assert engine.calculate_similarity("", "") == 1.0
        
        # One empty should be 0% similar
        assert engine.calculate_similarity("", "text") == 0.0
        assert engine.calculate_similarity("text", "") == 0.0

    def test_find_word_level_changes(self):
        """Test word-level change detection"""
        engine = ComparisonEngine()
        
        text1 = "The quick brown fox jumps"
        text2 = "The slow brown dog jumps"
        
        changes = engine.find_word_level_changes(text1, text2)
        
        assert isinstance(changes, list)
        assert len(changes) > 0
        
        # Should detect 'quick' -> 'slow' and 'fox' -> 'dog'
        change_texts = [change[1] for change in changes]
        assert 'quick' in change_texts or 'slow' in change_texts
        assert 'fox' in change_texts or 'dog' in change_texts

    def test_find_sentence_level_changes(self):
        """Test sentence-level change detection"""
        engine = ComparisonEngine()
        
        text1 = "First sentence. Second sentence. Third sentence."
        text2 = "First sentence. Modified second sentence. Third sentence."
        
        changes = engine.find_sentence_level_changes(text1, text2)
        
        assert isinstance(changes, list)
        assert len(changes) > 0
        
        # Should detect the modified sentence
        modified_found = any('Modified' in change[1] for change in changes)
        assert modified_found

    def test_detect_insertions(self):
        """Test insertion detection"""
        engine = ComparisonEngine()
        
        text1 = "Original text"
        text2 = "Original text with additional content"
        
        insertions = engine.detect_insertions(text1, text2)
        
        assert isinstance(insertions, list)
        assert len(insertions) > 0
        assert any('additional' in insertion.lower() for insertion in insertions)

    def test_detect_deletions(self):
        """Test deletion detection"""
        engine = ComparisonEngine()
        
        text1 = "Original text with extra content"
        text2 = "Original text"
        
        deletions = engine.detect_deletions(text1, text2)
        
        assert isinstance(deletions, list)
        assert len(deletions) > 0
        assert any('extra' in deletion.lower() for deletion in deletions)

    def test_detect_modifications(self):
        """Test modification detection"""
        engine = ComparisonEngine()
        
        text1 = "The quick brown fox"
        text2 = "The slow brown dog"
        
        modifications = engine.detect_modifications(text1, text2)
        
        assert isinstance(modifications, list)
        assert len(modifications) > 0
        
        # Should detect word-level replacements
        for old_text, new_text in modifications:
            assert isinstance(old_text, str)
            assert isinstance(new_text, str)
            assert old_text != new_text

    def test_create_change_objects(self):
        """Test creating Change objects from comparison results"""
        engine = ComparisonEngine()
        
        text1 = "Original text"
        text2 = "Modified text"
        
        changes = engine.create_change_objects(text1, text2)
        
        assert isinstance(changes, list)
        assert all(isinstance(change, Change) for change in changes)
        
        if changes:
            change = changes[0]
            assert hasattr(change, 'change_type')
            assert hasattr(change, 'deleted_text')
            assert hasattr(change, 'inserted_text')

    def test_get_change_statistics(self):
        """Test getting change statistics"""
        engine = ComparisonEngine()
        
        text1 = "The quick brown fox jumps over the lazy dog"
        text2 = "The slow brown cat jumps over the active dog"
        
        stats = engine.get_change_statistics(text1, text2)
        
        assert isinstance(stats, dict)
        assert 'total_changes' in stats
        assert 'insertions' in stats
        assert 'deletions' in stats
        assert 'modifications' in stats
        assert 'similarity_score' in stats
        
        assert stats['total_changes'] >= 0
        assert 0.0 <= stats['similarity_score'] <= 1.0

    def test_analyze_change_patterns(self):
        """Test change pattern analysis"""
        engine = ComparisonEngine()
        
        text1 = "[DATE] contract with [COMPANY] for [AMOUNT]"
        text2 = "2025-01-01 contract with Acme Corp for $1000"
        
        patterns = engine.analyze_change_patterns(text1, text2)
        
        assert isinstance(patterns, dict)
        assert 'placeholder_fills' in patterns
        assert 'formatting_changes' in patterns
        assert 'content_additions' in patterns
        
        # Should detect placeholder filling
        assert patterns['placeholder_fills'] > 0

    def test_get_contextual_changes(self):
        """Test getting changes with context"""
        engine = ComparisonEngine()
        
        text1 = "This is a long document with multiple sentences. This sentence will be changed. This is another sentence."
        text2 = "This is a long document with multiple sentences. This sentence was modified. This is another sentence."
        
        contextual_changes = engine.get_contextual_changes(text1, text2, context_size=10)
        
        assert isinstance(contextual_changes, list)
        
        for change in contextual_changes:
            assert isinstance(change, dict)
            assert 'change' in change
            assert 'context_before' in change
            assert 'context_after' in change


class TestComparisonEngineAdvanced:
    """Test advanced comparison features"""

    def test_fuzzy_matching(self):
        """Test fuzzy string matching"""
        engine = ComparisonEngine()
        
        # Similar but not identical strings
        text1 = "Contract Agreement"
        text2 = "Contract Agrement"  # Typo
        
        similarity = engine.fuzzy_match(text1, text2)
        
        assert 0.8 <= similarity <= 1.0  # Should be high similarity despite typo

    def test_semantic_similarity(self):
        """Test semantic similarity detection"""
        engine = ComparisonEngine()
        
        # Semantically similar phrases
        text1 = "payment due within thirty days"
        text2 = "payment required within 30 days"
        
        similarity = engine.semantic_similarity(text1, text2)
        
        # Even if exact matching is low, semantic should be higher
        assert similarity > 0.5

    def test_detect_structural_changes(self):
        """Test detection of structural changes"""
        engine = ComparisonEngine()
        
        # Different paragraph structures
        text1 = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        text2 = "First paragraph. Second paragraph.\n\nThird paragraph."
        
        structural_changes = engine.detect_structural_changes(text1, text2)
        
        assert isinstance(structural_changes, dict)
        assert 'paragraph_changes' in structural_changes
        assert 'line_break_changes' in structural_changes

    def test_detect_formatting_changes(self):
        """Test detection of formatting-related changes"""
        engine = ComparisonEngine()
        
        # Changes that are primarily formatting
        text1 = "Section 1.1 Payment Terms"
        text2 = "Section 1.1: Payment Terms"
        
        formatting_changes = engine.detect_formatting_changes(text1, text2)
        
        assert isinstance(formatting_changes, list)
        # Should detect the colon addition
        assert len(formatting_changes) > 0

    def test_ignore_whitespace_comparison(self):
        """Test comparison ignoring whitespace differences"""
        engine = ComparisonEngine()
        
        text1 = "This  has   extra    spaces"
        text2 = "This has extra spaces"
        
        similarity = engine.calculate_similarity(text1, text2, ignore_whitespace=True)
        
        # Should be identical when ignoring whitespace
        assert similarity == 1.0

    def test_case_insensitive_comparison(self):
        """Test case-insensitive comparison"""
        engine = ComparisonEngine()
        
        text1 = "This Is Mixed Case Text"
        text2 = "this is mixed case text"
        
        similarity = engine.calculate_similarity(text1, text2, ignore_case=True)
        
        # Should be identical when ignoring case
        assert similarity == 1.0


class TestComparisonEngineEdgeCases:
    """Test edge cases and error conditions"""

    def test_very_long_texts(self):
        """Test comparison with very long texts"""
        engine = ComparisonEngine()
        
        # Create long texts
        long_text1 = "A" * 10000
        long_text2 = "A" * 9999 + "B"
        
        changes = engine.compare_texts(long_text1, long_text2)
        
        assert isinstance(changes, list)
        # Should handle long texts without crashing
        
        similarity = engine.calculate_similarity(long_text1, long_text2)
        assert 0.0 <= similarity <= 1.0

    def test_unicode_text_comparison(self):
        """Test comparison with unicode characters"""
        engine = ComparisonEngine()
        
        text1 = "Contract with üñïçödé characters"
        text2 = "Contract with üñïçödé characters"
        
        similarity = engine.calculate_similarity(text1, text2)
        assert similarity == 1.0
        
        # Test with different unicode
        text3 = "Contract with différent characters"
        similarity = engine.calculate_similarity(text1, text3)
        assert 0.0 <= similarity < 1.0

    def test_special_characters(self):
        """Test comparison with special characters"""
        engine = ComparisonEngine()
        
        text1 = "Contract with $pecial ch@r&cters!"
        text2 = "Contract with $pecial ch@r&cters!"
        
        similarity = engine.calculate_similarity(text1, text2)
        assert similarity == 1.0

    def test_mixed_line_endings(self):
        """Test comparison with mixed line endings"""
        engine = ComparisonEngine()
        
        text1 = "Line 1\nLine 2\nLine 3"  # Unix
        text2 = "Line 1\r\nLine 2\r\nLine 3"  # Windows
        
        # Should handle different line endings gracefully
        changes = engine.compare_texts(text1, text2)
        assert isinstance(changes, list)

    def test_null_and_empty_inputs(self):
        """Test handling of null and empty inputs"""
        engine = ComparisonEngine()
        
        # Test with None inputs
        changes = engine.compare_texts(None, "text")
        assert isinstance(changes, list)
        
        changes = engine.compare_texts("text", None)
        assert isinstance(changes, list)
        
        # Test similarity with None
        similarity = engine.calculate_similarity(None, "text")
        assert similarity == 0.0
        
        similarity = engine.calculate_similarity("text", None)
        assert similarity == 0.0

    def test_performance_with_repetitive_text(self):
        """Test performance with highly repetitive text"""
        engine = ComparisonEngine()
        
        # Create repetitive text
        pattern = "This is a repeated pattern. "
        text1 = pattern * 100
        text2 = pattern * 99 + "This is a modified pattern. "
        
        changes = engine.compare_texts(text1, text2)
        
        assert isinstance(changes, list)
        # Should complete without timeout
        
        similarity = engine.calculate_similarity(text1, text2)
        assert 0.0 <= similarity <= 1.0