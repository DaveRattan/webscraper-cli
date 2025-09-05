#!/usr/bin/env python3
"""
Basic test script to verify the webscraper functionality
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import asyncio
from rich.console import Console
from utils.config import Config
from core.crawler import WebCrawler
from utils.logging_config import setup_logging

console = Console()

async def test_basic_functionality():
    """Test basic functionality"""
    console.print("🧪 [bold blue]Testing WebScraper Basic Functionality[/bold blue]")
    
    # Create test output directory
    output_dir = Path("./test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Set up logging
    setup_logging(output_dir, verbose=True)
    
    # Create config
    config = Config(
        output_dir=output_dir,
        max_depth=1,  # Keep it shallow for testing
        max_concurrent_requests=2
    )
    
    console.print(f"📁 Test output directory: {output_dir.absolute()}")
    
    # Test crawler
    console.print("🕷️ Testing web crawler...")
    crawler = WebCrawler(config)
    
    try:
        # Test with a simple, reliable website
        test_url = "https://httpbin.org/"
        console.print(f"🌐 Testing with URL: {test_url}")
        
        site_map = await crawler.discover_site_structure(test_url)
        
        console.print(f"✅ Crawler test successful!")
        console.print(f"   - Discovered {len(site_map.pages)} pages")
        console.print(f"   - Found {sum(len(files) for files in site_map.files.values())} files")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Crawler test failed: {e}")
        return False

def test_imports():
    """Test that all imports work correctly"""
    console.print("📦 [bold blue]Testing Imports[/bold blue]")
    
    try:
        # Test core imports
        from core.crawler import WebCrawler
        from core.scraper import WebScraper
        from core.pdf_converter import PDFConverter
        from core.downloader import FileDownloader
        console.print("✅ Core modules imported successfully")
        
        # Test CLI imports
        from cli.commands import app
        from cli.prompts import get_save_directory
        from cli.display import SiteMap
        console.print("✅ CLI modules imported successfully")
        
        # Test utils imports
        from utils.config import Config
        from utils.file_manager import FileManager
        from utils.logging_config import setup_logging
        console.print("✅ Utils modules imported successfully")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Import test failed: {e}")
        return False

def main():
    """Run all tests"""
    console.print("🚀 [bold green]WebScraper Test Suite[/bold green]\n")
    
    # Test imports
    if not test_imports():
        console.print("❌ [red]Import tests failed. Exiting.[/red]")
        sys.exit(1)
    
    console.print()
    
    # Test basic functionality
    try:
        result = asyncio.run(test_basic_functionality())
        if result:
            console.print("\n🎉 [bold green]All tests passed![/bold green]")
            console.print("✨ WebScraper is ready to use!")
        else:
            console.print("\n❌ [red]Some tests failed.[/red]")
            sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ [red]Test suite failed: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
