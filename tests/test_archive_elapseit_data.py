"""
Unit tests for Archive ElapseIT Data utility
"""

import pytest
import os
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from archive_elapseit_data import ElapseITArchiveManager


class TestElapseITArchiveManager:
    """Test cases for ElapseIT Archive Manager"""
    
    def test_init(self, temp_dir):
        """Test archive manager initialization"""
        data_dir = os.path.join(temp_dir, 'elapseIT_data')
        archive_dir = os.path.join(temp_dir, 'elapseIT_data', 'archive')
        
        manager = ElapseITArchiveManager()
        manager.data_dir = data_dir
        manager.archive_dir = archive_dir
        
        assert manager.data_dir == data_dir
        assert manager.archive_dir == archive_dir
    
    def test_create_archive_filename(self):
        """Test archive filename creation"""
        manager = ElapseITArchiveManager()
        
        # Test with timestamp
        filename = manager.create_archive_filename(
            'timesheets_20240101_to_20240331_143046.xlsx',
            date(2024, 3, 31),
            '143046'
        )
        
        assert filename == 'legacy_143046_timesheets_20240101_to_20240331_143046.xlsx'
        
        # Test without timestamp
        filename = manager.create_archive_filename(
            'timesheets_20240101_to_20240331.xlsx',
            date(2024, 3, 31)
        )
        
        assert filename.startswith('legacy_')
        assert filename.endswith('_timesheets_20240101_to_20240331.xlsx')
    
    def test_get_file_date_from_filename(self):
        """Test file date extraction from filename"""
        manager = ElapseITArchiveManager()
        
        # Test with valid filename
        file_date = manager.get_file_date_from_filename('timesheets_20240101_to_20240331_143046.xlsx')
        assert file_date == date(2024, 3, 31)
        
        # Test with different format
        file_date = manager.get_file_date_from_filename('timesheets_20241201_to_20241231_120000.xlsx')
        assert file_date == date(2024, 12, 31)
        
        # Test with invalid filename
        file_date = manager.get_file_date_from_filename('invalid_filename.xlsx')
        assert file_date is None
    
    def test_list_archive_contents(self, temp_dir):
        """Test archive contents listing"""
        # Create test archive directory
        archive_dir = os.path.join(temp_dir, 'archive')
        os.makedirs(archive_dir, exist_ok=True)
        
        # Create test files
        test_files = [
            'legacy_143046_timesheets_20240101_to_20240331_143046.xlsx',
            'legacy_091500_timesheets_20240401_to_20240630_091500.xlsx',
            'legacy_094936_timesheets_20240701_to_20240930_094936.xlsx'
        ]
        
        for filename in test_files:
            file_path = os.path.join(archive_dir, filename)
            with open(file_path, 'w') as f:
                f.write('test content')
        
        manager = ElapseITArchiveManager()
        manager.archive_dir = archive_dir
        
        result = manager.list_archive_contents()
        
        assert result is not None
        assert len(result) == 3
        
        # Check that files are sorted by date
        assert result[0]['filename'] == 'legacy_143046_timesheets_20240101_to_20240331_143046.xlsx'
        assert result[1]['filename'] == 'legacy_091500_timesheets_20240401_to_20240630_091500.xlsx'
        assert result[2]['filename'] == 'legacy_094936_timesheets_20240701_to_20240930_094936.xlsx'
    
    def test_list_archive_contents_empty(self, temp_dir):
        """Test archive contents listing with empty directory"""
        archive_dir = os.path.join(temp_dir, 'archive')
        os.makedirs(archive_dir, exist_ok=True)
        
        manager = ElapseITArchiveManager()
        manager.archive_dir = archive_dir
        
        result = manager.list_archive_contents()
        
        assert result == []
    
    def test_archive_file_success(self, temp_dir):
        """Test successful file archiving"""
        # Create test directories
        data_dir = os.path.join(temp_dir, 'elapseIT_data')
        archive_dir = os.path.join(temp_dir, 'elapseIT_data', 'archive')
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(archive_dir, exist_ok=True)
        
        # Create test file
        test_file = os.path.join(data_dir, 'timesheets_20240101_to_20240331_143046.xlsx')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        manager = ElapseITArchiveManager()
        manager.data_dir = data_dir
        manager.archive_dir = archive_dir
        
        result = manager.archive_file(test_file)
        
        assert result is True
        assert not os.path.exists(test_file)  # Original file should be moved
        assert os.path.exists(os.path.join(archive_dir, 'legacy_143046_timesheets_20240101_to_20240331_143046.xlsx'))
    
    def test_archive_file_not_found(self, temp_dir):
        """Test file archiving when file doesn't exist"""
        manager = ElapseITArchiveManager()
        manager.data_dir = temp_dir
        manager.archive_dir = os.path.join(temp_dir, 'archive')
        
        result = manager.archive_file('nonexistent_file.xlsx')
        
        assert result is False
    
    def test_archive_file_permission_error(self, temp_dir):
        """Test file archiving with permission error"""
        # Create test directories
        data_dir = os.path.join(temp_dir, 'elapseIT_data')
        archive_dir = os.path.join(temp_dir, 'elapseIT_data', 'archive')
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(archive_dir, exist_ok=True)
        
        # Create test file
        test_file = os.path.join(data_dir, 'timesheets_20240101_to_20240331_143046.xlsx')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        manager = ElapseITArchiveManager()
        manager.data_dir = data_dir
        manager.archive_dir = archive_dir
        
        # Mock shutil.move to raise PermissionError
        with patch('shutil.move', side_effect=PermissionError("Permission denied")):
            result = manager.archive_file(test_file)
        
        assert result is False
    
    def test_archive_all_files_success(self, temp_dir):
        """Test archiving all files successfully"""
        # Create test directories
        data_dir = os.path.join(temp_dir, 'elapseIT_data')
        archive_dir = os.path.join(temp_dir, 'elapseIT_data', 'archive')
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(archive_dir, exist_ok=True)
        
        # Create test files
        test_files = [
            'timesheets_20240101_to_20240331_143046.xlsx',
            'timesheets_20240401_to_20240630_091500.xlsx'
        ]
        
        for filename in test_files:
            file_path = os.path.join(data_dir, filename)
            with open(file_path, 'w') as f:
                f.write('test content')
        
        manager = ElapseITArchiveManager()
        manager.data_dir = data_dir
        manager.archive_dir = archive_dir
        
        result = manager.archive_all_files()
        
        assert result is True
        
        # Check that all files were archived
        for filename in test_files:
            assert not os.path.exists(os.path.join(data_dir, filename))
            assert os.path.exists(os.path.join(archive_dir, f'legacy_{filename.split("_")[-1].split(".")[0]}_{filename}'))
    
    def test_archive_all_files_no_files(self, temp_dir):
        """Test archiving when no files exist"""
        # Create test directories
        data_dir = os.path.join(temp_dir, 'elapseIT_data')
        archive_dir = os.path.join(temp_dir, 'elapseIT_data', 'archive')
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(archive_dir, exist_ok=True)
        
        manager = ElapseITArchiveManager()
        manager.data_dir = data_dir
        manager.archive_dir = archive_dir
        
        result = manager.archive_all_files()
        
        assert result is True  # Should succeed even with no files
    
    def test_clean_old_archives_success(self, temp_dir):
        """Test cleaning old archives successfully"""
        # Create test archive directory
        archive_dir = os.path.join(temp_dir, 'archive')
        os.makedirs(archive_dir, exist_ok=True)
        
        # Create test files with different dates
        old_date = datetime.now() - timedelta(days=100)
        recent_date = datetime.now() - timedelta(days=10)
        
        old_file = os.path.join(archive_dir, 'legacy_old_file.xlsx')
        recent_file = os.path.join(archive_dir, 'legacy_recent_file.xlsx')
        
        with open(old_file, 'w') as f:
            f.write('old content')
        with open(recent_file, 'w') as f:
            f.write('recent content')
        
        # Mock file modification times
        old_timestamp = old_date.timestamp()
        recent_timestamp = recent_date.timestamp()
        
        with patch('os.path.getmtime', side_effect=lambda x: old_timestamp if 'old' in x else recent_timestamp):
            manager = ElapseITArchiveManager()
            manager.archive_dir = archive_dir
            
            result = manager.clean_old_archives(days=30)
        
        assert result is True
        assert not os.path.exists(old_file)  # Old file should be deleted
        assert os.path.exists(recent_file)   # Recent file should remain
    
    def test_clean_old_archives_no_files(self, temp_dir):
        """Test cleaning old archives when no files exist"""
        archive_dir = os.path.join(temp_dir, 'archive')
        os.makedirs(archive_dir, exist_ok=True)
        
        manager = ElapseITArchiveManager()
        manager.archive_dir = archive_dir
        
        result = manager.clean_old_archives(days=30)
        
        assert result is True  # Should succeed even with no files
    
    def test_get_archive_statistics(self, temp_dir):
        """Test archive statistics generation"""
        # Create test archive directory
        archive_dir = os.path.join(temp_dir, 'archive')
        os.makedirs(archive_dir, exist_ok=True)
        
        # Create test files
        test_files = [
            'legacy_143046_timesheets_20240101_to_20240331_143046.xlsx',
            'legacy_091500_timesheets_20240401_to_20240630_091500.xlsx'
        ]
        
        for filename in test_files:
            file_path = os.path.join(archive_dir, filename)
            with open(file_path, 'w') as f:
                f.write('test content')
        
        manager = ElapseITArchiveManager()
        manager.archive_dir = archive_dir
        
        result = manager.get_archive_statistics()
        
        assert result is not None
        assert 'total_files' in result
        assert 'total_size_mb' in result
        assert 'oldest_file' in result
        assert 'newest_file' in result
        assert 'date_range' in result
        
        assert result['total_files'] == 2
        assert result['total_size_mb'] > 0
        assert result['oldest_file'] is not None
        assert result['newest_file'] is not None
    
    def test_get_archive_statistics_empty(self, temp_dir):
        """Test archive statistics with empty directory"""
        archive_dir = os.path.join(temp_dir, 'archive')
        os.makedirs(archive_dir, exist_ok=True)
        
        manager = ElapseITArchiveManager()
        manager.archive_dir = archive_dir
        
        result = manager.get_archive_statistics()
        
        assert result is not None
        assert result['total_files'] == 0
        assert result['total_size_mb'] == 0
        assert result['oldest_file'] is None
        assert result['newest_file'] is None
    
    def test_validate_file_format(self):
        """Test file format validation"""
        manager = ElapseITArchiveManager()
        
        # Valid formats
        assert manager.validate_file_format('timesheets_20240101_to_20240331_143046.xlsx') is True
        assert manager.validate_file_format('timesheets_20241201_to_20241231_120000.xlsx') is True
        
        # Invalid formats
        assert manager.validate_file_format('invalid_filename.xlsx') is False
        assert manager.validate_file_format('timesheets_20240101_to_20240331.xlsx') is False  # Missing timestamp
        assert manager.validate_file_format('timesheets_20240101_to_20240331_143046.csv') is False  # Wrong extension
    
    def test_get_file_size_mb(self, temp_dir):
        """Test file size calculation in MB"""
        # Create test file
        test_file = os.path.join(temp_dir, 'test_file.xlsx')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        manager = ElapseITArchiveManager()
        
        size_mb = manager.get_file_size_mb(test_file)
        
        assert size_mb > 0
        assert isinstance(size_mb, float)
    
    def test_get_file_size_mb_not_found(self):
        """Test file size calculation for non-existent file"""
        manager = ElapseITArchiveManager()
        
        size_mb = manager.get_file_size_mb('nonexistent_file.xlsx')
        
        assert size_mb == 0
