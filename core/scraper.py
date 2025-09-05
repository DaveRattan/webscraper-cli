"""
Web scraper for processing pages and downloading content
"""

import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from urllib.parse import urlparse
import time
from loguru import logger

from core.pdf_converter import PDFConverter
from core.downloader import FileDownloader
from utils.config import Config

@dataclass
class ScrapingResult:
    """Result of a scraping session"""
    pages_converted: int = 0
    files_downloaded: int = 0
    errors: List[str] = None
    total_time: float = 0.0
    output_dir: str = ""
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class WebScraper:
    """
    Main scraper that processes selected paths and coordinates PDF conversion and file downloads
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.pdf_converter = PDFConverter(config)
        self.file_downloader = FileDownloader(config)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=60)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def process_paths(self, selected_paths: List[str], progress_callback: Optional[Callable] = None) -> ScrapingResult:
        """
        Process selected paths: convert to PDF and download files
        """
        start_time = time.time()
        result = ScrapingResult(output_dir=str(self.config.output_dir))
        
        logger.info(f"Starting to process {len(selected_paths)} paths")
        
        async with self:
            # Create semaphore to limit concurrent operations
            semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
            
            # Process paths in batches to avoid overwhelming the server
            batch_size = 5
            for i in range(0, len(selected_paths), batch_size):
                batch = selected_paths[i:i + batch_size]
                
                # Create tasks for this batch
                tasks = []
                for url in batch:
                    task = self._process_single_path(semaphore, url, result)
                    tasks.append(task)
                
                # Execute batch
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Update progress
                if progress_callback:
                    progress_callback()
                
                # Small delay between batches
                await asyncio.sleep(0.5)
        
        result.total_time = time.time() - start_time
        logger.info(f"Processing completed in {result.total_time:.2f} seconds")
        
        return result
    
    async def _process_single_path(self, semaphore: asyncio.Semaphore, url: str, result: ScrapingResult):
        """
        Process a single path: convert to PDF and download any files found
        """
        async with semaphore:
            try:
                logger.debug(f"Processing: {url}")
                
                # 1. Convert webpage to PDF
                pdf_success = await self._convert_page_to_pdf(url)
                if pdf_success:
                    result.pages_converted += 1
                else:
                    result.errors.append(f"Failed to convert {url} to PDF")
                
                # 2. Scan page for downloadable files and download them
                downloaded_count = await self._download_files_from_page(url)
                result.files_downloaded += downloaded_count
                
                # Small delay to be respectful
                await asyncio.sleep(self.config.crawl_delay)
                
            except Exception as e:
                error_msg = f"Error processing {url}: {str(e)}"
                logger.error(error_msg)
                result.errors.append(error_msg)
    
    async def _convert_page_to_pdf(self, url: str) -> bool:
        """
        Convert a webpage to PDF
        """
        try:
            # Create a safe filename from URL
            filename = self._create_safe_filename(url, '.pdf')
            output_path = self.config.output_dir / 'pages' / filename
            
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert using PDF converter
            success = await self.pdf_converter.convert_url_to_pdf(url, output_path)
            
            if success:
                logger.info(f"✅ Converted to PDF: {filename}")
                return True
            else:
                logger.warning(f"❌ Failed to convert: {url}")
                return False
                
        except Exception as e:
            logger.error(f"Error converting {url} to PDF: {e}")
            return False
    
    async def _download_files_from_page(self, url: str) -> int:
        """
        Scan a page for downloadable files and download them
        """
        try:
            # Fetch the page content
            async with self.session.get(url) as response:
                if response.status != 200:
                    return 0
                
                content = await response.text()
            
            # Extract downloadable files using the file downloader
            downloaded_count = await self.file_downloader.download_files_from_html(content, url)
            
            return downloaded_count
            
        except Exception as e:
            logger.error(f"Error downloading files from {url}: {e}")
            return 0
    
    def _create_safe_filename(self, url: str, extension: str = '') -> str:
        """
        Create a safe filename from a URL
        """
        try:
            parsed = urlparse(url)
            
            # Use domain + path for filename
            domain = parsed.netloc.replace('www.', '')
            path = parsed.path.strip('/')
            
            if path:
                # Replace path separators and invalid characters
                safe_path = path.replace('/', '_').replace('\\', '_')
                filename = f"{domain}_{safe_path}"
            else:
                filename = domain
            
            # Remove or replace invalid filename characters
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                filename = filename.replace(char, '_')
            
            # Limit filename length
            if len(filename) > 100:
                filename = filename[:100]
            
            # Add extension
            if extension and not filename.endswith(extension):
                filename += extension
            
            return filename
            
        except Exception as e:
            logger.error(f"Error creating filename for {url}: {e}")
            # Fallback to timestamp-based filename
            timestamp = int(time.time())
            return f"page_{timestamp}{extension}"
    
    async def get_page_content(self, url: str) -> Optional[str]:
        """
        Get the HTML content of a page
        """
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    async def save_page_content(self, url: str, content: str) -> bool:
        """
        Save raw HTML content to file
        """
        try:
            filename = self._create_safe_filename(url, '.html')
            output_path = self.config.output_dir / 'html' / filename
            
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save content
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            logger.debug(f"Saved HTML: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving HTML for {url}: {e}")
            return False
