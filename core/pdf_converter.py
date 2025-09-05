"""
PDF conversion functionality using multiple backends
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Union
import tempfile
import os
from loguru import logger

try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from utils.config import Config

class PDFConverter:
    """
    PDF converter with multiple backend support
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.preferred_backend = self._detect_best_backend()
        logger.info(f"PDF Converter initialized with backend: {self.preferred_backend}")
    
    def _detect_best_backend(self) -> str:
        """
        Detect the best available PDF conversion backend
        """
        if PLAYWRIGHT_AVAILABLE:
            return 'playwright'
        elif WEASYPRINT_AVAILABLE:
            return 'weasyprint'
        elif PDFKIT_AVAILABLE:
            return 'pdfkit'
        else:
            return 'chrome'  # Fallback to Chrome headless
    
    async def convert_url_to_pdf(self, url: str, output_path: Path) -> bool:
        """
        Convert a URL to PDF using the best available method
        """
        try:
            if self.preferred_backend == 'playwright':
                return await self._convert_with_playwright(url, output_path)
            elif self.preferred_backend == 'weasyprint':
                return await self._convert_with_weasyprint(url, output_path)
            elif self.preferred_backend == 'pdfkit':
                return await self._convert_with_pdfkit(url, output_path)
            else:
                return await self._convert_with_chrome(url, output_path)
        except Exception as e:
            logger.error(f"PDF conversion failed for {url}: {e}")
            return False
    
    async def convert_html_to_pdf(self, html_content: str, output_path: Path, base_url: Optional[str] = None) -> bool:
        """
        Convert HTML content to PDF
        """
        try:
            if self.preferred_backend == 'playwright':
                return await self._convert_html_with_playwright(html_content, output_path)
            elif self.preferred_backend == 'weasyprint':
                return await self._convert_html_with_weasyprint(html_content, output_path, base_url)
            elif self.preferred_backend == 'pdfkit':
                return await self._convert_html_with_pdfkit(html_content, output_path)
            else:
                # For Chrome, we need to save HTML to temp file first
                return await self._convert_html_with_chrome(html_content, output_path)
        except Exception as e:
            logger.error(f"HTML to PDF conversion failed: {e}")
            return False
    
    async def _convert_with_playwright(self, url: str, output_path: Path) -> bool:
        """
        Convert URL to PDF using Playwright
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set viewport and user agent
                await page.set_viewport_size({"width": 1920, "height": 1080})
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                # Navigate to page
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Generate PDF
                await page.pdf(
                    path=str(output_path),
                    format='A4',
                    print_background=True,
                    margin={
                        'top': '1cm',
                        'right': '1cm',
                        'bottom': '1cm',
                        'left': '1cm'
                    }
                )
                
                await browser.close()
                return True
                
        except Exception as e:
            logger.error(f"Playwright conversion failed for {url}: {e}")
            return False
    
    async def _convert_html_with_playwright(self, html_content: str, output_path: Path) -> bool:
        """
        Convert HTML content to PDF using Playwright
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set content
                await page.set_content(html_content, wait_until='networkidle')
                
                # Generate PDF
                await page.pdf(
                    path=str(output_path),
                    format='A4',
                    print_background=True,
                    margin={
                        'top': '1cm',
                        'right': '1cm',
                        'bottom': '1cm',
                        'left': '1cm'
                    }
                )
                
                await browser.close()
                return True
                
        except Exception as e:
            logger.error(f"Playwright HTML conversion failed: {e}")
            return False
    
    async def _convert_with_weasyprint(self, url: str, output_path: Path) -> bool:
        """
        Convert URL to PDF using WeasyPrint
        """
        try:
            # WeasyPrint is synchronous, so run in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: weasyprint.HTML(url=url).write_pdf(str(output_path))
            )
            return True
        except Exception as e:
            logger.error(f"WeasyPrint conversion failed for {url}: {e}")
            return False
    
    async def _convert_html_with_weasyprint(self, html_content: str, output_path: Path, base_url: Optional[str] = None) -> bool:
        """
        Convert HTML content to PDF using WeasyPrint
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: weasyprint.HTML(string=html_content, base_url=base_url).write_pdf(str(output_path))
            )
            return True
        except Exception as e:
            logger.error(f"WeasyPrint HTML conversion failed: {e}")
            return False
    
    async def _convert_with_pdfkit(self, url: str, output_path: Path) -> bool:
        """
        Convert URL to PDF using pdfkit (wkhtmltopdf)
        """
        try:
            options = {
                'page-size': 'A4',
                'margin-top': '1cm',
                'margin-right': '1cm',
                'margin-bottom': '1cm',
                'margin-left': '1cm',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None
            }
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: pdfkit.from_url(url, str(output_path), options=options)
            )
            return True
        except Exception as e:
            logger.error(f"pdfkit conversion failed for {url}: {e}")
            return False
    
    async def _convert_html_with_pdfkit(self, html_content: str, output_path: Path) -> bool:
        """
        Convert HTML content to PDF using pdfkit
        """
        try:
            options = {
                'page-size': 'A4',
                'margin-top': '1cm',
                'margin-right': '1cm',
                'margin-bottom': '1cm',
                'margin-left': '1cm',
                'encoding': "UTF-8",
                'no-outline': None
            }
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: pdfkit.from_string(html_content, str(output_path), options=options)
            )
            return True
        except Exception as e:
            logger.error(f"pdfkit HTML conversion failed: {e}")
            return False
    
    async def _convert_with_chrome(self, url: str, output_path: Path) -> bool:
        """
        Convert URL to PDF using Chrome headless (fallback method)
        """
        try:
            cmd = [
                'google-chrome',
                '--headless',
                '--disable-gpu',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--print-to-pdf=' + str(output_path),
                '--virtual-time-budget=10000',
                url
            ]
            
            # Try different Chrome executable names
            chrome_executables = ['google-chrome', 'chromium-browser', 'chromium', 'chrome']
            
            for executable in chrome_executables:
                try:
                    cmd[0] = executable
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await process.communicate()
                    
                    if process.returncode == 0 and output_path.exists():
                        return True
                    else:
                        logger.debug(f"Chrome ({executable}) failed: {stderr.decode()}")
                        
                except FileNotFoundError:
                    continue
            
            logger.error("No Chrome executable found for PDF conversion")
            return False
            
        except Exception as e:
            logger.error(f"Chrome conversion failed for {url}: {e}")
            return False
    
    async def _convert_html_with_chrome(self, html_content: str, output_path: Path) -> bool:
        """
        Convert HTML content to PDF using Chrome headless
        """
        try:
            # Save HTML to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_html_path = f.name
            
            try:
                # Convert the temporary file
                file_url = f"file://{temp_html_path}"
                success = await self._convert_with_chrome(file_url, output_path)
                return success
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_html_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Chrome HTML conversion failed: {e}")
            return False
    
    def get_backend_info(self) -> dict:
        """
        Get information about available backends
        """
        return {
            'current_backend': self.preferred_backend,
            'available_backends': {
                'playwright': PLAYWRIGHT_AVAILABLE,
                'weasyprint': WEASYPRINT_AVAILABLE,
                'pdfkit': PDFKIT_AVAILABLE,
                'chrome': True  # Assume Chrome might be available
            }
        }
