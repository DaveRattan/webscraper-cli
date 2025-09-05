#!/usr/bin/env python3
"""
WebScraper CLI - A comprehensive web scraping and crawling tool
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from cli.commands import app as cli_app

console = Console()

def main():
    """Main entry point for the WebScraper CLI"""
    console.print(Panel.fit(
        Text("🕷️  WebScraper CLI", style="bold blue"),
        subtitle="Web Scraping, Crawling & PDF Conversion Tool"
    ))
    
    cli_app()

if __name__ == "__main__":
    main()
