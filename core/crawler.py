"""
Web crawler for discovering site structure and links
"""

import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
from typing import Set, List, Dict, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
import time
from loguru import logger

# SiteMap will be imported from display module when needed
from utils.config import Config

@dataclass
class CrawlResult:
    """Result of a crawl operation"""
    url: str
    title: str
    links: List[str]
    files: List[Dict[str, str]]
    depth: int
    success: bool
    error: Optional[str] = None

class WebCrawler:
    """
    Web crawler that discovers site structure and downloadable files
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.visited_urls: Set[str] = set()
        self.discovered_files: Set[str] = set()
        
        # File extensions we want to download
        self.downloadable_extensions = {
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.txt', '.rtf', '.odt', '.ods', '.odp', '.csv'
        }
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def discover_site_structure(self, root_url: str):
        """
        Discover the structure of a website starting from the root URL
        """
        logger.info(f"Starting site discovery for: {root_url}")
        
        # Import SiteMap here to avoid circular imports
        from cli.display import SiteMap
        site_map = SiteMap(root_url)
        
        async with self:
            # Start crawling from the root
            await self._crawl_recursive(root_url, site_map, depth=0)
        
        logger.info(f"Site discovery completed. Found {len(site_map.pages)} pages")
        return site_map
    
    async def _crawl_recursive(self, url: str, site_map, depth: int):
        """
        Recursively crawl a website
        """
        # Check depth limit
        if depth > self.config.max_depth:
            return
        
        # Check if already visited
        if url in self.visited_urls:
            return
        
        # Mark as visited
        self.visited_urls.add(url)
        
        # Add delay to be respectful
        if depth > 0:  # No delay for the first request
            await asyncio.sleep(self.config.crawl_delay)
        
        try:
            # Crawl the current page
            result = await self._crawl_single_page(url, depth)
            
            if result.success:
                # Add page to site map
                site_map.add_page(result.url, result.title, depth)
                
                # Add discovered files
                for file_info in result.files:
                    site_map.add_file(result.url, file_info['url'], file_info['type'])
                
                # Process links for next level crawling
                if depth < self.config.max_depth:
                    tasks = []
                    for link_url in result.links[:self.config.max_links_per_page]:
                        site_map.add_link(result.url, link_url)
                        
                        # Only crawl if it's within the same domain (optional)
                        if self._is_same_domain(url, link_url):
                            task = self._crawl_recursive(link_url, site_map, depth + 1)
                            tasks.append(task)
                    
                    # Execute crawling tasks concurrently (but limited)
                    if tasks:
                        # Limit concurrent requests to avoid overwhelming the server
                        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
                        limited_tasks = [self._limited_crawl(semaphore, task) for task in tasks]
                        await asyncio.gather(*limited_tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
    
    async def _limited_crawl(self, semaphore: asyncio.Semaphore, task):
        """Execute crawl task with semaphore limiting"""
        async with semaphore:
            return await task
    
    async def _crawl_single_page(self, url: str, depth: int) -> CrawlResult:
        """
        Crawl a single page and extract information
        """
        try:
            logger.debug(f"Crawling: {url} (depth: {depth})")
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    return CrawlResult(
                        url=url, title="", links=[], files=[], depth=depth,
                        success=False, error=f"HTTP {response.status}"
                    )
                
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract page title
                title_tag = soup.find('title')
                title = title_tag.get_text().strip() if title_tag else url.split('/')[-1]
                
                # Extract all links
                links = self._extract_links(soup, url)
                
                # Extract downloadable files
                files = self._extract_files(soup, url)
                
                return CrawlResult(
                    url=url, title=title, links=links, files=files,
                    depth=depth, success=True
                )
        
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return CrawlResult(
                url=url, title="", links=[], files=[], depth=depth,
                success=False, error=str(e)
            )
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract all valid links from a page
        """
        links = []
        
        # Find all anchor tags with href
        for link_tag in soup.find_all('a', href=True):
            href = link_tag['href'].strip()
            
            # Skip empty hrefs, anchors, and javascript
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            # Basic URL validation
            if self._is_valid_url(absolute_url):
                links.append(absolute_url)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(links))
    
    def _extract_files(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """
        Extract downloadable files from a page
        """
        files = []
        
        # Check all links for downloadable files
        for link_tag in soup.find_all('a', href=True):
            href = link_tag['href'].strip()
            if not href:
                continue
            
            absolute_url = urljoin(base_url, href)
            
            # Check if it's a downloadable file
            file_ext = self._get_file_extension(absolute_url)
            if file_ext in self.downloadable_extensions:
                files.append({
                    'url': absolute_url,
                    'type': file_ext[1:],  # Remove the dot
                    'text': link_tag.get_text().strip()
                })
        
        # Also check for embedded files (like PDFs in iframes)
        for iframe in soup.find_all('iframe', src=True):
            src = iframe['src'].strip()
            if src:
                absolute_url = urljoin(base_url, src)
                file_ext = self._get_file_extension(absolute_url)
                if file_ext in self.downloadable_extensions:
                    files.append({
                        'url': absolute_url,
                        'type': file_ext[1:],
                        'text': 'Embedded file'
                    })
        
        return files
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Check if a URL is valid for crawling
        """
        try:
            parsed = urlparse(url)
            return parsed.scheme in ('http', 'https') and parsed.netloc
        except:
            return False
    
    def _is_same_domain(self, url1: str, url2: str) -> bool:
        """
        Check if two URLs are from the same domain
        """
        try:
            domain1 = urlparse(url1).netloc.lower()
            domain2 = urlparse(url2).netloc.lower()
            
            # Allow subdomains if configured
            if self.config.allow_subdomains:
                # Extract main domain (e.g., example.com from www.example.com)
                def get_main_domain(domain):
                    parts = domain.split('.')
                    if len(parts) >= 2:
                        return '.'.join(parts[-2:])
                    return domain
                
                return get_main_domain(domain1) == get_main_domain(domain2)
            else:
                return domain1 == domain2
        except:
            return False
    
    def _get_file_extension(self, url: str) -> str:
        """
        Get file extension from URL
        """
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            # Remove query parameters and fragments
            if '?' in path:
                path = path.split('?')[0]
            if '#' in path:
                path = path.split('#')[0]
            
            # Get extension
            if '.' in path:
                return '.' + path.split('.')[-1]
            return ''
        except:
            return ''
