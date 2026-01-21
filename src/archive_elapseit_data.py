#!/usr/bin/env python3
"""
Nexa - ElapseIT Data Archive Management Utility
===============================================

A utility to manage archiving of ElapseIT timesheet data files with proper organization
and historical tracking.

Features:
- List archive contents with file details
- Archive specific files manually
- Clean old archives (optional)
- View archive statistics

Usage:
    python archive_elapseit_data.py [options]

Author: AI Assistant
Date: 2024
"""

import os
import glob
import shutil
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
import argparse


class ElapseITArchiveManager:
    """Manage ElapseIT data archiving operations."""
    
    def __init__(self):
        """Initialize the archive manager."""
        self.data_dir = "../output/elapseIT_data"
        self.archive_dir = "../output/elapseIT_data/archive"
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)
    
    def create_archive_filename(self, original_filename: str, file_date: date, timestamp: str = None) -> str:
        """
        Create archive filename with proper timestamp.
        
        Args:
            original_filename: Original file name
            file_date: Date to use for archive naming
            timestamp: Optional timestamp, defaults to current time
            
        Returns:
            str: Archive filename
        """
        if not timestamp:
            timestamp = datetime.now().strftime("%H%M%S")
        
        # Extract base name without extension
        base_name = os.path.splitext(original_filename)[0]
        extension = os.path.splitext(original_filename)[1]
        
        # If already has timestamp format, use as is
        if "_to_" in base_name and len(base_name.split("_")) >= 4:
            # Already properly formatted
            archive_filename = original_filename
        else:
            # Add timestamp for manual archives
            date_str = file_date.strftime("%Y%m%d")
            archive_filename = f"manual_{date_str}_{timestamp}_{base_name}{extension}"
        
        return archive_filename
    
    def find_files_to_archive(self) -> List[Dict]:
        """
        Find files in the main directory that can be archived.
        
        Returns:
            List[Dict]: List of file information dictionaries
        """
        files_to_archive = []
        
        # Find Excel files in main directory
        excel_files = glob.glob(os.path.join(self.data_dir, "*.xlsx"))
        
        for filepath in excel_files:
            filename = os.path.basename(filepath)
            
            # Skip README files
            if filename.lower().startswith('readme'):
                continue
            
            try:
                # Get file stats
                stat_info = os.stat(filepath)
                file_size = stat_info.st_size
                modified_time = datetime.fromtimestamp(stat_info.st_mtime)
                
                files_to_archive.append({
                    'filepath': filepath,
                    'filename': filename,
                    'size_bytes': file_size,
                    'modified_date': modified_time,
                    'can_archive': True
                })
                
            except Exception as e:
                print(f"⚠️ Error reading file {filename}: {e}")
                continue
        
        return files_to_archive
    
    def archive_file(self, file_info: Dict, dry_run: bool = False) -> bool:
        """
        Archive a specific file.
        
        Args:
            file_info: File information dictionary
            dry_run: If True, only show what would be done
            
        Returns:
            bool: True if archived successfully
        """
        try:
            filename = file_info['filename']
            filepath = file_info['filepath']
            modified_date = file_info['modified_date'].date()
            
            # Create archive filename
            timestamp = datetime.now().strftime("%H%M%S")
            archive_filename = self.create_archive_filename(filename, modified_date, timestamp)
            archive_path = os.path.join(self.archive_dir, archive_filename)
            
            if dry_run:
                print(f"📋 Would archive: {filename} → {archive_filename}")
                return True
            
            # Move file to archive
            shutil.move(filepath, archive_path)
            print(f"📁 Archived: {filename} → {archive_filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error archiving {file_info['filename']}: {e}")
            return False
    
    def list_archive_contents(self):
        """List all files in the archive directory with details."""
        archive_files = glob.glob(os.path.join(self.archive_dir, "*"))
        
        if not archive_files:
            print("📂 Archive directory is empty")
            return
        
        print("📂 ARCHIVE CONTENTS")
        print("=" * 60)
        
        # Group files by type
        timesheet_files = []
        archive_files = []
        other_files = []
        
        for filepath in archive_files:
            filename = os.path.basename(filepath)
            
            try:
                stat_info = os.stat(filepath)
                file_size = stat_info.st_size
                size_kb = round(file_size / 1024, 1)
                modified_time = datetime.fromtimestamp(stat_info.st_mtime)
                modified_str = modified_time.strftime("%Y-%m-%d %H:%M")
                
                file_info = {
                    'filename': filename,
                    'size_kb': size_kb,
                    'modified_str': modified_str,
                    'modified_time': modified_time
                }
                
                if filename.startswith('timesheets_'):
                    timesheet_files.append(file_info)
                elif filename.startswith('archive_'):
                    archive_files.append(file_info)
                else:
                    other_files.append(file_info)
                    
            except Exception as e:
                print(f"⚠️ Error reading {filename}: {e}")
        
        # Sort files by modification time (newest first)
        timesheet_files.sort(key=lambda x: x['modified_time'], reverse=True)
        archive_files.sort(key=lambda x: x['modified_time'], reverse=True)
        other_files.sort(key=lambda x: x['modified_time'], reverse=True)
        
        # Display timesheet files
        if timesheet_files:
            print(f"\n🕒 TIMESHEET EXTRACTS ({len(timesheet_files)} files)")
            print("-" * 40)
            for file_info in timesheet_files:
                print(f"   📄 {file_info['filename']} ({file_info['size_kb']} KB, {file_info['modified_str']})")
        
        # Display archive files
        if archive_files:
            print(f"\n📜 ARCHIVED FILES ({len(archive_files)} files)")
            print("-" * 40)
            for file_info in archive_files:
                print(f"   📄 {file_info['filename']} ({file_info['size_kb']} KB, {file_info['modified_str']})")
        
        # Display other files
        if other_files:
            print(f"\n📋 OTHER FILES ({len(other_files)} files)")
            print("-" * 40)
            for file_info in other_files:
                print(f"   📄 {file_info['filename']} ({file_info['size_kb']} KB, {file_info['modified_str']})")
        
        # Summary
        total_files = len(timesheet_files) + len(archive_files) + len(other_files)
        total_size_kb = sum(f['size_kb'] for f in timesheet_files + archive_files + other_files)
        total_size_mb = round(total_size_kb / 1024, 1)
        
        print(f"\n📊 SUMMARY")
        print("-" * 20)
        print(f"   📁 Total files: {total_files}")
        print(f"   💾 Total size: {total_size_mb} MB")
    
    def clean_old_archives(self, days_old: int = 90, dry_run: bool = False) -> int:
        """
        Clean archive files older than specified days.
        
        Args:
            days_old: Age threshold in days
            dry_run: If True, only show what would be deleted
            
        Returns:
            int: Number of files cleaned
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        archive_files = glob.glob(os.path.join(self.archive_dir, "*"))
        
        cleaned_count = 0
        
        print(f"🧹 CLEANING ARCHIVES OLDER THAN {days_old} DAYS")
        print(f"   Cutoff date: {cutoff_date.strftime('%Y-%m-%d')}")
        print("-" * 50)
        
        for filepath in archive_files:
            filename = os.path.basename(filepath)
            
            try:
                stat_info = os.stat(filepath)
                modified_time = datetime.fromtimestamp(stat_info.st_mtime)
                
                if modified_time < cutoff_date:
                    if dry_run:
                        print(f"📋 Would delete: {filename} (modified {modified_time.strftime('%Y-%m-%d')})")
                    else:
                        os.remove(filepath)
                        print(f"🗑️ Deleted: {filename} (modified {modified_time.strftime('%Y-%m-%d')})")
                    cleaned_count += 1
                    
            except Exception as e:
                print(f"⚠️ Error processing {filename}: {e}")
        
        if cleaned_count == 0:
            print("✅ No files found to clean")
        else:
            action = "Would clean" if dry_run else "Cleaned"
            print(f"✅ {action} {cleaned_count} old archive files")
        
        return cleaned_count
    
    def archive_all_files(self, dry_run: bool = False) -> int:
        """
        Archive all files in the main directory.
        
        Args:
            dry_run: If True, only show what would be done
            
        Returns:
            int: Number of files archived
        """
        files_to_archive = self.find_files_to_archive()
        
        if not files_to_archive:
            print("✅ No files found to archive")
            return 0
        
        print(f"📁 ARCHIVING {len(files_to_archive)} FILES")
        print("-" * 40)
        
        archived_count = 0
        for file_info in files_to_archive:
            if self.archive_file(file_info, dry_run):
                archived_count += 1
        
        action = "Would archive" if dry_run else "Archived"
        print(f"✅ {action} {archived_count} files")
        
        return archived_count


def main():
    """Main function to run the archive manager."""
    parser = argparse.ArgumentParser(
        description="ElapseIT Data Archive Management Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python archive_elapseit_data.py --list                    # List archive contents
  python archive_elapseit_data.py --archive-all             # Archive all files
  python archive_elapseit_data.py --archive-all --dry-run   # Preview archiving
  python archive_elapseit_data.py --clean 30                # Clean files older than 30 days
  python archive_elapseit_data.py --clean 90 --dry-run      # Preview cleaning
        """
    )
    
    parser.add_argument('--list', action='store_true',
                        help='List archive contents with details')
    parser.add_argument('--archive-all', action='store_true',
                        help='Archive all files in main directory')
    parser.add_argument('--clean', type=int, metavar='DAYS',
                        help='Clean archive files older than DAYS (default: 90)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview actions without making changes')
    
    args = parser.parse_args()
    
    # Create archive manager
    manager = ElapseITArchiveManager()
    
    print("🗂️ ElapseIT Data Archive Manager")
    print("=" * 40)
    
    try:
        if args.list:
            manager.list_archive_contents()
            
        elif args.archive_all:
            if args.dry_run:
                print("🔍 DRY RUN MODE - No files will be moved")
                print("-" * 40)
            manager.archive_all_files(dry_run=args.dry_run)
            
        elif args.clean is not None:
            days = args.clean if args.clean > 0 else 90
            if args.dry_run:
                print("🔍 DRY RUN MODE - No files will be deleted")
                print("-" * 40)
            manager.clean_old_archives(days_old=days, dry_run=args.dry_run)
            
        else:
            # Default: show archive status
            print("📊 ARCHIVE STATUS")
            print("-" * 20)
            manager.list_archive_contents()
            
            print(f"\n💡 TIP: Use --help to see available options")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
