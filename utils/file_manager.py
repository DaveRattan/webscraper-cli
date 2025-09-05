"""
File management utilities for organizing scraped content
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from loguru import logger

@dataclass
class ScrapingSession:
    """Information about a scraping session"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    root_url: str
    output_dir: str
    pages_processed: int = 0
    files_downloaded: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class FileManager:
    """
    Manages file organization and metadata for scraped content
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.session_file = self.output_dir / 'session_info.json'
        self.index_file = self.output_dir / 'content_index.json'
        
    def initialize_session(self, root_url: str) -> ScrapingSession:
        """
        Initialize a new scraping session
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        session = ScrapingSession(
            session_id=session_id,
            start_time=datetime.now(),
            end_time=None,
            root_url=root_url,
            output_dir=str(self.output_dir)
        )
        
        # Create directory structure
        self._create_directory_structure()
        
        # Save initial session info
        self._save_session_info(session)
        
        logger.info(f"Initialized scraping session: {session_id}")
        return session
    
    def finalize_session(self, session: ScrapingSession, pages_processed: int, files_downloaded: int, errors: List[str]):
        """
        Finalize a scraping session with results
        """
        session.end_time = datetime.now()
        session.pages_processed = pages_processed
        session.files_downloaded = files_downloaded
        session.errors = errors
        
        self._save_session_info(session)
        self._create_summary_report(session)
        
        logger.info(f"Finalized scraping session: {session.session_id}")
    
    def _create_directory_structure(self):
        """
        Create the organized directory structure
        """
        directories = [
            'pages',           # PDF pages
            'files/pdf',       # PDF files
            'files/doc',       # Word documents
            'files/xls',       # Excel files
            'files/ppt',       # PowerPoint files
            'files/txt',       # Text files
            'files/other',     # Other file types
            'html',            # Raw HTML (optional)
            'logs',            # Log files
            'metadata'         # Metadata files
        ]
        
        for directory in directories:
            (self.output_dir / directory).mkdir(parents=True, exist_ok=True)
    
    def _save_session_info(self, session: ScrapingSession):
        """
        Save session information to JSON file
        """
        try:
            session_data = asdict(session)
            
            # Convert datetime objects to strings
            if session_data['start_time']:
                session_data['start_time'] = session.start_time.isoformat()
            if session_data['end_time']:
                session_data['end_time'] = session.end_time.isoformat()
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Could not save session info: {e}")
    
    def _create_summary_report(self, session: ScrapingSession):
        """
        Create a human-readable summary report
        """
        try:
            report_path = self.output_dir / 'SUMMARY.md'
            
            duration = "Unknown"
            if session.start_time and session.end_time:
                delta = session.end_time - session.start_time
                duration = str(delta).split('.')[0]  # Remove microseconds
            
            report_content = f"""# Web Scraping Summary

## Session Information
- **Session ID**: {session.session_id}
- **Root URL**: {session.root_url}
- **Start Time**: {session.start_time.strftime('%Y-%m-%d %H:%M:%S') if session.start_time else 'Unknown'}
- **End Time**: {session.end_time.strftime('%Y-%m-%d %H:%M:%S') if session.end_time else 'Unknown'}
- **Duration**: {duration}

## Results
- **Pages Processed**: {session.pages_processed}
- **Files Downloaded**: {session.files_downloaded}
- **Errors Encountered**: {len(session.errors)}

## Directory Structure
```
{self.output_dir.name}/
├── pages/          # PDF versions of web pages
├── files/          # Downloaded files organized by type
│   ├── pdf/
│   ├── doc/
│   ├── xls/
│   ├── ppt/
│   ├── txt/
│   └── other/
├── html/           # Raw HTML files (if saved)
├── logs/           # Log files
└── metadata/       # Metadata and index files
```

## File Counts
"""
            
            # Add file counts by type
            file_counts = self._get_file_counts()
            for file_type, count in file_counts.items():
                report_content += f"- **{file_type.upper()}**: {count} files\n"
            
            if session.errors:
                report_content += f"\n## Errors\n"
                for i, error in enumerate(session.errors[:10], 1):  # Show first 10 errors
                    report_content += f"{i}. {error}\n"
                
                if len(session.errors) > 10:
                    report_content += f"... and {len(session.errors) - 10} more errors\n"
            
            report_content += f"\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
                
            logger.info(f"Summary report created: {report_path}")
            
        except Exception as e:
            logger.error(f"Could not create summary report: {e}")
    
    def _get_file_counts(self) -> Dict[str, int]:
        """
        Get counts of files by type
        """
        counts = {}
        
        # Count PDF pages
        pages_dir = self.output_dir / 'pages'
        if pages_dir.exists():
            counts['pages'] = len(list(pages_dir.glob('*.pdf')))
        
        # Count downloaded files by type
        files_dir = self.output_dir / 'files'
        if files_dir.exists():
            for subdir in files_dir.iterdir():
                if subdir.is_dir():
                    file_count = len(list(subdir.glob('*')))
                    # Exclude .meta files from count
                    meta_count = len(list(subdir.glob('*.meta')))
                    counts[subdir.name] = file_count - meta_count
        
        return counts
    
    def create_content_index(self, pages_info: List[Dict], files_info: List[Dict]):
        """
        Create an index of all scraped content
        """
        try:
            index_data = {
                'created': datetime.now().isoformat(),
                'pages': pages_info,
                'files': files_info,
                'statistics': {
                    'total_pages': len(pages_info),
                    'total_files': len(files_info),
                    'file_types': self._get_file_counts()
                }
            }
            
            with open(self.index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
                
            logger.info(f"Content index created: {self.index_file}")
            
        except Exception as e:
            logger.error(f"Could not create content index: {e}")
    
    def organize_file(self, file_path: Path, file_type: str, metadata: Optional[Dict] = None) -> Path:
        """
        Move a file to the appropriate organized location
        """
        try:
            # Determine target directory
            if file_type.lower() in ['pdf']:
                target_dir = self.output_dir / 'files' / 'pdf'
            elif file_type.lower() in ['doc', 'docx']:
                target_dir = self.output_dir / 'files' / 'doc'
            elif file_type.lower() in ['xls', 'xlsx']:
                target_dir = self.output_dir / 'files' / 'xls'
            elif file_type.lower() in ['ppt', 'pptx']:
                target_dir = self.output_dir / 'files' / 'ppt'
            elif file_type.lower() in ['txt', 'rtf']:
                target_dir = self.output_dir / 'files' / 'txt'
            else:
                target_dir = self.output_dir / 'files' / 'other'
            
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename if needed
            target_path = target_dir / file_path.name
            counter = 1
            while target_path.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                target_path = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Move file
            shutil.move(str(file_path), str(target_path))
            
            # Save metadata if provided
            if metadata:
                self._save_file_metadata(target_path, metadata)
            
            logger.debug(f"Organized file: {target_path}")
            return target_path
            
        except Exception as e:
            logger.error(f"Could not organize file {file_path}: {e}")
            return file_path
    
    def _save_file_metadata(self, file_path: Path, metadata: Dict):
        """
        Save metadata for a file
        """
        try:
            metadata_path = file_path.with_suffix(file_path.suffix + '.meta')
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.debug(f"Could not save metadata for {file_path}: {e}")
    
    def cleanup_empty_directories(self):
        """
        Remove empty directories from the output structure
        """
        try:
            for root, dirs, files in self.output_dir.rglob('*'):
                for directory in dirs:
                    dir_path = Path(root) / directory
                    if dir_path.is_dir() and not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        logger.debug(f"Removed empty directory: {dir_path}")
                        
        except Exception as e:
            logger.debug(f"Error during cleanup: {e}")
    
    def get_session_info(self) -> Optional[Dict]:
        """
        Get information about the current session
        """
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Could not load session info: {e}")
            return None
    
    def archive_session(self, archive_name: Optional[str] = None) -> Path:
        """
        Create a compressed archive of the entire session
        """
        try:
            if not archive_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_name = f"webscraper_session_{timestamp}"
            
            archive_path = self.output_dir.parent / f"{archive_name}.zip"
            
            shutil.make_archive(
                str(archive_path.with_suffix('')),
                'zip',
                str(self.output_dir)
            )
            
            logger.info(f"Session archived: {archive_path}")
            return archive_path
            
        except Exception as e:
            logger.error(f"Could not archive session: {e}")
            raise
