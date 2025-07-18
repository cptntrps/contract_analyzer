"""
Unit tests for FileManager service
"""

import pytest
import tempfile
import os
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from app.services.storage.file_manager import FileManager


class TestFileManager:
    """Test suite for FileManager service"""

    def test_init_default(self):
        """Test manager initialization with defaults"""
        manager = FileManager()
        assert manager is not None
        assert hasattr(manager, 'base_path')
        assert hasattr(manager, 'upload_dir')
        assert hasattr(manager, 'reports_dir')
        assert hasattr(manager, 'templates_dir')

    def test_init_custom_paths(self):
        """Test manager initialization with custom paths"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            assert manager.base_path == Path(temp_dir)
            assert manager.upload_dir == Path(temp_dir) / "uploads"
            assert manager.reports_dir == Path(temp_dir) / "reports"
            assert manager.templates_dir == Path(temp_dir) / "templates"

    def test_ensure_directories(self):
        """Test directory creation functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            assert manager.upload_dir.exists()
            assert manager.reports_dir.exists()
            assert manager.templates_dir.exists()

    def test_save_file_success(self):
        """Test successful file saving"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            # Create test file content
            test_content = b"Test file content"
            filename = "test_file.txt"
            
            # Mock file object
            mock_file = Mock()
            mock_file.read.return_value = test_content
            mock_file.filename = filename
            
            saved_path = manager.save_file(mock_file, "uploads")
            
            assert saved_path is not None
            assert saved_path.exists()
            assert saved_path.read_bytes() == test_content

    def test_save_file_with_custom_filename(self):
        """Test file saving with custom filename"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            test_content = b"Test content"
            custom_name = "custom_name.txt"
            
            mock_file = Mock()
            mock_file.read.return_value = test_content
            mock_file.filename = "original.txt"
            
            saved_path = manager.save_file(mock_file, "uploads", custom_name)
            
            assert saved_path.name == custom_name
            assert saved_path.exists()

    def test_save_file_invalid_directory(self):
        """Test file saving with invalid directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            
            mock_file = Mock()
            mock_file.filename = "test.txt"
            mock_file.read.return_value = b"content"
            
            saved_path = manager.save_file(mock_file, "invalid_dir")
            assert saved_path is None

    def test_get_file_path_existing(self):
        """Test getting path for existing file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            # Create test file
            test_file = manager.upload_dir / "test.txt"
            test_file.write_text("test content")
            
            file_path = manager.get_file_path("test.txt", "uploads")
            
            assert file_path == test_file
            assert file_path.exists()

    def test_get_file_path_nonexistent(self):
        """Test getting path for non-existent file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            file_path = manager.get_file_path("nonexistent.txt", "uploads")
            assert file_path is None

    def test_delete_file_success(self):
        """Test successful file deletion"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            # Create test file
            test_file = manager.upload_dir / "test_delete.txt"
            test_file.write_text("test content")
            
            assert test_file.exists()
            
            result = manager.delete_file("test_delete.txt", "uploads")
            
            assert result is True
            assert not test_file.exists()

    def test_delete_file_nonexistent(self):
        """Test deletion of non-existent file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            result = manager.delete_file("nonexistent.txt", "uploads")
            assert result is False

    def test_list_files_in_directory(self):
        """Test listing files in directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            # Create test files
            test_files = ["file1.txt", "file2.docx", "file3.pdf"]
            for filename in test_files:
                (manager.upload_dir / filename).write_text("content")
            
            files = manager.list_files("uploads")
            
            assert len(files) == 3
            assert all(f.name in test_files for f in files)

    def test_list_files_empty_directory(self):
        """Test listing files in empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            files = manager.list_files("uploads")
            assert files == []

    def test_list_files_invalid_directory(self):
        """Test listing files in invalid directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            
            files = manager.list_files("invalid_dir")
            assert files == []

    def test_list_files_with_extension_filter(self):
        """Test listing files with extension filter"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            # Create test files with different extensions
            (manager.upload_dir / "file1.txt").write_text("content")
            (manager.upload_dir / "file2.docx").write_text("content")
            (manager.upload_dir / "file3.pdf").write_text("content")
            (manager.upload_dir / "file4.docx").write_text("content")
            
            docx_files = manager.list_files("uploads", extension_filter=".docx")
            
            assert len(docx_files) == 2
            assert all(f.suffix == ".docx" for f in docx_files)

    def test_get_file_info(self):
        """Test getting file information"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            # Create test file
            test_content = "Test file content for info"
            test_file = manager.upload_dir / "info_test.txt"
            test_file.write_text(test_content)
            
            info = manager.get_file_info("info_test.txt", "uploads")
            
            assert isinstance(info, dict)
            assert 'name' in info
            assert 'size' in info
            assert 'extension' in info
            assert 'created' in info
            assert 'modified' in info
            
            assert info['name'] == "info_test.txt"
            assert info['size'] == len(test_content.encode())
            assert info['extension'] == ".txt"

    def test_get_file_info_nonexistent(self):
        """Test getting info for non-existent file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            info = manager.get_file_info("nonexistent.txt", "uploads")
            assert info is None

    def test_copy_file_success(self):
        """Test successful file copying"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            # Create source file
            source_content = "Source file content"
            source_file = manager.upload_dir / "source.txt"
            source_file.write_text(source_content)
            
            # Copy to reports directory
            copied_path = manager.copy_file("source.txt", "uploads", "reports", "copied.txt")
            
            assert copied_path is not None
            assert copied_path.exists()
            assert copied_path.read_text() == source_content
            assert copied_path.parent == manager.reports_dir

    def test_copy_file_nonexistent_source(self):
        """Test copying non-existent file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            copied_path = manager.copy_file("nonexistent.txt", "uploads", "reports")
            assert copied_path is None

    def test_move_file_success(self):
        """Test successful file moving"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            # Create source file
            source_content = "File to move"
            source_file = manager.upload_dir / "tomove.txt"
            source_file.write_text(source_content)
            
            # Move to reports directory
            moved_path = manager.move_file("tomove.txt", "uploads", "reports", "moved.txt")
            
            assert moved_path is not None
            assert moved_path.exists()
            assert moved_path.read_text() == source_content
            assert not source_file.exists()

    def test_move_file_nonexistent_source(self):
        """Test moving non-existent file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            moved_path = manager.move_file("nonexistent.txt", "uploads", "reports")
            assert moved_path is None

    def test_clean_directory(self):
        """Test cleaning directory contents"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            # Create test files
            for i in range(5):
                (manager.upload_dir / f"file{i}.txt").write_text("content")
            
            # Verify files exist
            assert len(list(manager.upload_dir.iterdir())) == 5
            
            # Clean directory
            result = manager.clean_directory("uploads")
            
            assert result is True
            assert len(list(manager.upload_dir.iterdir())) == 0

    def test_clean_nonexistent_directory(self):
        """Test cleaning non-existent directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            
            result = manager.clean_directory("invalid_dir")
            assert result is False

    def test_get_directory_size(self):
        """Test getting directory size"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            # Create test files with known content
            content1 = "File 1 content"
            content2 = "File 2 has different content"
            
            (manager.upload_dir / "file1.txt").write_text(content1)
            (manager.upload_dir / "file2.txt").write_text(content2)
            
            total_size = manager.get_directory_size("uploads")
            expected_size = len(content1.encode()) + len(content2.encode())
            
            assert total_size == expected_size

    def test_get_directory_size_empty(self):
        """Test getting size of empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            size = manager.get_directory_size("uploads")
            assert size == 0

    def test_get_directory_size_invalid(self):
        """Test getting size of invalid directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            
            size = manager.get_directory_size("invalid_dir")
            assert size == 0


class TestFileManagerSecurity:
    """Test security features of FileManager"""

    def test_path_traversal_protection(self):
        """Test protection against path traversal attacks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            # Attempt path traversal
            malicious_paths = [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                "uploads/../../../secret.txt",
                "/etc/passwd",
                "C:\\Windows\\System32\\config\\sam"
            ]
            
            for malicious_path in malicious_paths:
                file_path = manager.get_file_path(malicious_path, "uploads")
                
                # Should either be None or within the allowed directory
                if file_path:
                    assert manager.upload_dir in file_path.parents

    def test_filename_sanitization(self):
        """Test filename sanitization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            # Test dangerous filenames
            dangerous_names = [
                "file<script>.txt",
                "file|pipe.txt",
                "file?query.txt",
                "file*.txt",
                "file\x00null.txt"
            ]
            
            for dangerous_name in dangerous_names:
                mock_file = Mock()
                mock_file.filename = dangerous_name
                mock_file.read.return_value = b"content"
                
                saved_path = manager.save_file(mock_file, "uploads")
                
                if saved_path:
                    # Filename should be sanitized
                    assert '<' not in saved_path.name
                    assert '|' not in saved_path.name
                    assert '?' not in saved_path.name
                    assert '*' not in saved_path.name
                    assert '\x00' not in saved_path.name

    def test_file_size_limits(self):
        """Test file size limitation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir, max_file_size=1024)  # 1KB limit
            manager.ensure_directories()
            
            # Create oversized file content
            large_content = b"A" * 2048  # 2KB
            
            mock_file = Mock()
            mock_file.filename = "large_file.txt"
            mock_file.read.return_value = large_content
            
            saved_path = manager.save_file(mock_file, "uploads")
            
            # Should reject oversized file
            assert saved_path is None


class TestFileManagerEdgeCases:
    """Test edge cases and error conditions"""

    def test_concurrent_file_operations(self):
        """Test concurrent file operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            # Create multiple files concurrently (simulated)
            filenames = [f"concurrent_{i}.txt" for i in range(10)]
            
            for filename in filenames:
                mock_file = Mock()
                mock_file.filename = filename
                mock_file.read.return_value = b"content"
                
                saved_path = manager.save_file(mock_file, "uploads")
                assert saved_path is not None
            
            # Verify all files were created
            files = manager.list_files("uploads")
            assert len(files) == 10

    def test_unicode_filenames(self):
        """Test handling of unicode filenames"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            unicode_names = [
                "файл.txt",  # Cyrillic
                "文件.txt",  # Chinese
                "ファイル.txt",  # Japanese
                "archivo_niño.txt",  # Spanish with accent
                "émoji😀.txt"  # Emoji
            ]
            
            for unicode_name in unicode_names:
                mock_file = Mock()
                mock_file.filename = unicode_name
                mock_file.read.return_value = b"unicode content"
                
                try:
                    saved_path = manager.save_file(mock_file, "uploads")
                    if saved_path:
                        assert saved_path.exists()
                except UnicodeError:
                    # Some systems may not support certain unicode filenames
                    pass

    def test_disk_space_handling(self):
        """Test handling when disk space is low"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            # This test would require mocking disk space checks
            # For now, just ensure the methods exist
            assert hasattr(manager, 'get_available_space')
            assert hasattr(manager, 'check_disk_space')

    @patch('pathlib.Path.write_bytes')
    def test_file_write_error_handling(self, mock_write):
        """Test handling of file write errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(base_path=temp_dir)
            manager.ensure_directories()
            
            # Mock write to raise an exception
            mock_write.side_effect = OSError("Disk full")
            
            mock_file = Mock()
            mock_file.filename = "test.txt"
            mock_file.read.return_value = b"content"
            
            saved_path = manager.save_file(mock_file, "uploads")
            
            # Should handle the error gracefully
            assert saved_path is None