"""
CLI Commands using Typer
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
import asyncio

from cli.prompts import get_save_directory, show_crawl_options
from cli.display import display_site_map, show_download_progress
from core.crawler import WebCrawler
from core.scraper import WebScraper
from utils.config import Config
from utils.logging_config import setup_logging

app = typer.Typer(
    help="WebScraper CLI - Scrape, crawl and convert websites to PDF",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]}
)
console = Console()

@app.command()
def scrape(
    url: str = typer.Argument(..., help="URL to scrape"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    max_depth: int = typer.Option(3, "--depth", "-d", help="Maximum crawl depth"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive mode for path selection")
):
    """
    Scrape a website, crawl its links, and save content as PDFs
    """
    console.print(f"🚀 Starting web scraping for: [bold blue]{url}[/bold blue]")
    
    # Get or prompt for output directory
    if not output_dir:
        output_dir = get_save_directory()
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    console.print(f"📁 Saving content to: [green]{output_path.absolute()}[/green]")
    
    # Set up logging
    setup_logging(output_path, verbose=False)
    
    # Initialize components
    config = Config(
        output_dir=output_path,
        max_depth=max_depth,
        interactive=interactive
    )
    
    crawler = WebCrawler(config)
    scraper = WebScraper(config)
    
    try:
        # Start the crawling process
        asyncio.run(run_scraping_session(url, crawler, scraper, config))
        
    except KeyboardInterrupt:
        console.print("\n❌ Scraping interrupted by user")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Error during scraping: {e}")
        raise typer.Exit(1)

async def run_scraping_session(url: str, crawler: WebCrawler, scraper: WebScraper, config: Config):
    """Run the complete scraping session"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Initial crawl to build site map
        task = progress.add_task("🕷️ Discovering site structure...", total=None)
        site_map = await crawler.discover_site_structure(url)
        progress.update(task, description="✅ Site structure discovered")
        
        if config.interactive:
            # Show interactive site map and get user selections
            selected_paths = display_site_map(site_map)
            
            if not selected_paths:
                console.print("❌ No paths selected. Exiting.")
                return
                
            console.print(f"📋 Selected {len(selected_paths)} paths for processing")
        else:
            # Non-interactive mode: process all discovered paths
            selected_paths = site_map.get_all_paths()
            console.print(f"📋 Processing all {len(selected_paths)} discovered paths")
        
        # Process selected paths
        task = progress.add_task("🔄 Processing selected paths...", total=len(selected_paths))
        
        results = await scraper.process_paths(selected_paths, progress_callback=lambda: progress.advance(task))
        
        progress.update(task, description="✅ All paths processed")
    
    # Show final results
    console.print("\n🎉 [bold green]Scraping completed successfully![/bold green]")
    console.print(f"📊 Processed: {results.pages_converted} pages → PDF")
    console.print(f"📥 Downloaded: {results.files_downloaded} files")
    console.print(f"📁 Saved to: {config.output_dir}")

@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    reset: bool = typer.Option(False, "--reset", help="Reset configuration to defaults")
):
    """
    Manage configuration settings
    """
    if show:
        # Show current config
        console.print("⚙️ Current Configuration:")
        # TODO: Implement config display
        pass
    
    if reset:
        if Confirm.ask("Reset all configuration to defaults?"):
            # TODO: Implement config reset
            console.print("✅ Configuration reset to defaults")

@app.command()
def version():
    """Show version information"""
    console.print("🕷️ WebScraper CLI v1.0.0")

if __name__ == "__main__":
    app()
