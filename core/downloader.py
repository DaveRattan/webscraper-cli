"""
File downloader for various document formats
"""

import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set, Optional
import mimetypes
from bs4 import BeautifulSoup
from loguru import logger

from utils.config import Config

class FileDownloader:
    """
    Downloads files of supported formats from web pages
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.downloaded_files: Set[str] = set()
        
        # Supported file extensions and their MIME types
        self.supported_extensions = {
            # Documents
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.txt': 'text/plain',
            '.rtf': 'application/rtf',
            '.csv': 'text/csv',
            
            # OpenDocument formats
            '.odt': 'application/vnd.oasis.opendocument.text',
            '.ods': 'application/vnd.oasis.opendocument.spreadsheet',
            '.odp': 'application/vnd.oasis.opendocument.presentation',
            
            # Archives (optional)
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
            '.tar': 'application/x-tar',
            '.gz': 'application/gzip',
            
            # Images (optional)
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml'
        }
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=300)  # 5 minutes for large files
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def download_files_from_html(self, html_content: str, base_url: str) -> int:
        """
        Extract and download all supported files from HTML content
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        file_urls = self._extract_file_urls(soup, base_url)
        
        if not file_urls:
            return 0
        
        logger.info(f"Found {len(file_urls)} downloadable files on {base_url}")
        
        # Download files concurrently (but limited)
        semaphore = asyncio.Semaphore(self.config.max_concurrent_downloads)
        tasks = []
        
        for file_info in file_urls:
            if file_info['url'] not in self.downloaded_files:
                task = self._download_single_file(semaphore, file_info, base_url)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successful downloads
        successful_downloads = sum(1 for result in results if result is True)
        
        return successful_downloads
    
    def _extract_file_urls(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """
        Extract all downloadable file URLs from HTML
        """
        file_urls = []
        
        # Check all anchor tags
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            if not href:
                continue
            
            absolute_url = urljoin(base_url, href)
            file_info = self._analyze_url(absolute_url, link.get_text().strip())
            
            if file_info:
                file_urls.append(file_info)
        
        # Check embedded content (iframes, objects, embeds)
        for tag in soup.find_all(['iframe', 'object', 'embed'], src=True):
            src = tag['src'].strip()
            if not src:
                continue
            
            absolute_url = urljoin(base_url, src)
            file_info = self._analyze_url(absolute_url, 'Embedded content')
            
            if file_info:
                file_urls.append(file_info)
        
        # Check for data attributes that might contain file URLs
        for element in soup.find_all(attrs={'data-url': True}):
            data_url = element['data-url'].strip()
            if data_url:
                absolute_url = urljoin(base_url, data_url)
                file_info = self._analyze_url(absolute_url, element.get_text().strip())
                
                if file_info:
                    file_urls.append(file_info)
        
        # Remove duplicates
        seen_urls = set()
        unique_files = []
        for file_info in file_urls:
            if file_info['url'] not in seen_urls:
                seen_urls.add(file_info['url'])
                unique_files.append(file_info)
        
        return unique_files
    
    def _analyze_url(self, url: str, link_text: str) -> Optional[Dict[str, str]]:
        """
        Analyze a URL to determine if it's a downloadable file
        """
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            # Remove query parameters for extension detection
            clean_path = path.split('?')[0].split('#')[0]
            
            # Check file extension
            for ext in self.supported_extensions:
                if clean_path.endswith(ext):
                    return {
                        'url': url,
                        'extension': ext,
                        'mime_type': self.supported_extensions[ext],
                        'link_text': link_text,
                        'filename': self._extract_filename(url, ext)
                    }
            
            # Check for common document indicators in URL or link text
            doc_indicators = ['download', 'file', 'document', 'attachment', 'export']
            if any(indicator in path.lower() or indicator in link_text.lower() for indicator in doc_indicators):
                # Might be a document, try to determine type from other clues
                if any(word in link_text.lower() for word in ['pdf', 'document']):
                    return {
                        'url': url,
                        'extension': '.pdf',
                        'mime_type': 'application/pdf',
                        'link_text': link_text,
                        'filename': self._extract_filename(url, '.pdf')
                    }
            
            return None
            
        except Exception as e:
            logger.debug(f"Error analyzing URL {url}: {e}")
            return None
    
    def _extract_filename(self, url: str, extension: str) -> str:
        """
        Extract or generate a filename from URL
        """
        try:
            parsed = urlparse(url)
            path = parsed.path
            
            # Try to get filename from path
            if path and '/' in path:
                filename = path.split('/')[-1]
                if filename and '.' in filename:
                    return filename
            
            # Generate filename from domain and path
            domain = parsed.netloc.replace('www.', '')
            safe_path = path.replace('/', '_').replace('\\', '_').strip('_')
            
            if safe_path:
                filename = f"{domain}_{safe_path}"
            else:
                filename = domain
            
            # Clean filename
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                filename = filename.replace(char, '_')
            
            # Limit length
            if len(filename) > 100:
                filename = filename[:100]
            
            # Ensure extension
            if not filename.endswith(extension):
                filename += extension
            
            return filename
            
        except Exception:
            # Fallback filename
            import time
            timestamp = int(time.time())
            return f"file_{timestamp}{extension}"
    
    async def _download_single_file(self, semaphore: asyncio.Semaphore, file_info: Dict[str, str], source_url: str) -> bool:
        """
        Download a single file
        """
        async with semaphore:
            try:
                url = file_info['url']
                filename = file_info['filename']
                
                # Skip if already downloaded
                if url in self.downloaded_files:
                    return True
                
                logger.debug(f"Downloading: {filename} from {url}")
                
                # Create output directory
                file_type = file_info['extension'][1:]  # Remove dot
                output_dir = self.config.output_dir / 'files' / file_type
                output_dir.mkdir(parents=True, exist_ok=True)
                
                output_path = output_dir / filename
                
                # Skip if file already exists
                if output_path.exists():
                    logger.debug(f"File already exists: {filename}")
                    self.downloaded_files.add(url)
                    return True
                
                # Download the file
                async with self.session.get(url) as response:
                    if response.status != 200:
                        logger.warning(f"HTTP {response.status} for {url}")
                        return False
                    
                    # Check content type
                    content_type = response.headers.get('content-type', '').lower()
                    expected_mime = file_info['mime_type'].lower()
                    
                    # Some flexibility in MIME type checking
                    if not (expected_mime in content_type or content_type in expected_mime or 'application/octet-stream' in content_type):
                        logger.debug(f"MIME type mismatch for {url}: expected {expected_mime}, got {content_type}")
                    
                    # Save file
                    async with aiofiles.open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                
                # Verify file was downloaded
                if output_path.exists() and output_path.stat().st_size > 0:
                    self.downloaded_files.add(url)
                    logger.info(f"✅ Downloaded: {filename} ({output_path.stat().st_size} bytes)")
                    
                    # Save metadata
                    await self._save_file_metadata(output_path, file_info, source_url)
                    
                    return True
                else:
                    logger.warning(f"❌ Download failed or empty file: {filename}")
                    return False
                
            except Exception as e:
                logger.error(f"Error downloading {file_info.get('url', 'unknown')}: {e}")
                return False
    
    async def _save_file_metadata(self, file_path: Path, file_info: Dict[str, str], source_url: str):
        """
        Save metadata about the downloaded file
        """
        try:
            metadata = {
                'original_url': file_info['url'],
                'source_page': source_url,
                'link_text': file_info['link_text'],
                'file_type': file_info['extension'],
                'mime_type': file_info['mime_type'],
                'download_time': str(asyncio.get_event_loop().time()),
                'file_size': file_path.stat().st_size
            }
            
            metadata_path = file_path.with_suffix(file_path.suffix + '.meta')
            
            async with aiofiles.open(metadata_path, 'w', encoding='utf-8') as f:
                import json
                await f.write(json.dumps(metadata, indent=2))
                
        except Exception as e:
            logger.debug(f"Could not save metadata for {file_path}: {e}")
    
    async def download_direct_url(self, url: str, output_path: Path) -> bool:
        """
        Download a file directly from a URL
        """
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return False
                
                # Ensure output directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Download file
                async with aiofiles.open(output_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
                
                return output_path.exists() and output_path.stat().st_size > 0
                
        except Exception as e:
            logger.error(f"Direct download failed for {url}: {e}")
            return False
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions
        """
        return list(self.supported_extensions.keys())
    
    def get_download_stats(self) -> Dict[str, int]:
        """
        Get download statistics
        """
        return {
            'total_downloaded': len(self.downloaded_files),
            'supported_types': len(self.supported_extensions)
        }
