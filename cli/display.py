"""
Rich-based display components for visual output
"""

from typing import List, Dict, Any
from rich.console import Console
from rich.tree import Tree
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
import questionary

from cli.prompts import select_paths_to_process

console = Console()

class SiteMap:
    """Represents the discovered site structure"""
    
    def __init__(self, root_url: str):
        self.root_url = root_url
        self.pages = {}  # url -> page info
        self.links = {}  # url -> list of linked urls
        self.files = {}  # url -> list of downloadable files
    
    def add_page(self, url: str, title: str = "", depth: int = 0):
        """Add a page to the site map"""
        self.pages[url] = {
            'title': title,
            'depth': depth,
            'processed': False
        }
        if url not in self.links:
            self.links[url] = []
        if url not in self.files:
            self.files[url] = []
    
    def add_link(self, from_url: str, to_url: str):
        """Add a link between pages"""
        if from_url not in self.links:
            self.links[from_url] = []
        if to_url not in self.links[from_url]:
            self.links[from_url].append(to_url)
    
    def add_file(self, page_url: str, file_url: str, file_type: str):
        """Add a downloadable file found on a page"""
        if page_url not in self.files:
            self.files[page_url] = []
        self.files[page_url].append({
            'url': file_url,
            'type': file_type
        })
    
    def get_all_paths(self) -> List[str]:
        """Get all discovered URLs"""
        return list(self.pages.keys())
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the site map"""
        total_files = sum(len(files) for files in self.files.values())
        return {
            'pages': len(self.pages),
            'links': sum(len(links) for links in self.links.values()),
            'files': total_files
        }

def display_site_map(site_map: SiteMap) -> List[str]:
    """
    Display the site map as an interactive tree and get user selections
    """
    console.print(Panel("🗺️ [bold]Discovered Site Structure[/bold]", style="green"))
    
    # Create tree visualization
    tree = Tree(f"🌐 [bold blue]{site_map.root_url}[/bold blue]")
    
    # Build tree structure
    _build_tree_recursive(tree, site_map, site_map.root_url, visited=set(), max_depth=3)
    
    # Display the tree
    console.print(tree)
    
    # Show statistics
    stats = site_map.get_stats()
    stats_table = Table(show_header=False, box=None)
    stats_table.add_row("📄 Pages discovered:", str(stats['pages']))
    stats_table.add_row("🔗 Links found:", str(stats['links']))
    stats_table.add_row("📁 Files found:", str(stats['files']))
    
    console.print(Panel(stats_table, title="Statistics", style="blue"))
    
    # Let user select paths to process
    all_paths = site_map.get_all_paths()
    selected_paths = select_paths_to_process(all_paths)
    
    return selected_paths

def _build_tree_recursive(parent_node, site_map: SiteMap, url: str, visited: set, max_depth: int, current_depth: int = 0):
    """Recursively build the tree structure"""
    if current_depth >= max_depth or url in visited:
        return
    
    visited.add(url)
    
    page_info = site_map.pages.get(url, {})
    title = page_info.get('title', url.split('/')[-1] or url)
    
    # Add files found on this page
    files = site_map.files.get(url, [])
    if files:
        file_node = parent_node.add(f"📁 Files ({len(files)})")
        for file_info in files[:5]:  # Show first 5 files
            file_type = file_info['type'].upper()
            file_name = file_info['url'].split('/')[-1]
            file_node.add(f"📄 [{file_type}] {file_name}")
        if len(files) > 5:
            file_node.add(f"... and {len(files) - 5} more files")
    
    # Add linked pages
    links = site_map.links.get(url, [])
    for link_url in links[:10]:  # Limit to first 10 links to avoid clutter
        if link_url not in visited:
            link_info = site_map.pages.get(link_url, {})
            link_title = link_info.get('title', link_url.split('/')[-1] or link_url)
            link_node = parent_node.add(f"🔗 {link_title}")
            _build_tree_recursive(link_node, site_map, link_url, visited.copy(), max_depth, current_depth + 1)

def show_download_progress(total_items: int) -> Progress:
    """
    Create and return a progress bar for downloads
    """
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TextColumn("{task.completed}/{task.total}"),
        TimeRemainingColumn(),
        console=console
    )
    
    return progress

def show_processing_status(current_url: str, completed: int, total: int, files_downloaded: int):
    """
    Show current processing status
    """
    layout = Layout()
    
    # Current status
    status_panel = Panel(
        f"🔄 Processing: [bold blue]{current_url}[/bold blue]\n"
        f"📊 Progress: {completed}/{total} pages\n"
        f"📥 Files downloaded: {files_downloaded}",
        title="Current Status",
        style="green"
    )
    
    console.print(status_panel)

def show_final_summary(results: Dict[str, Any]):
    """
    Display final summary of the scraping session
    """
    summary_table = Table(title="🎉 Scraping Summary", show_header=False, box=None)
    
    summary_table.add_row("📄 Pages converted to PDF:", str(results.get('pages_converted', 0)))
    summary_table.add_row("📥 Files downloaded:", str(results.get('files_downloaded', 0)))
    summary_table.add_row("⏱️  Total time:", results.get('total_time', 'Unknown'))
    summary_table.add_row("📁 Output directory:", str(results.get('output_dir', 'Unknown')))
    
    if results.get('errors'):
        summary_table.add_row("❌ Errors encountered:", str(len(results['errors'])))
    
    console.print(Panel(summary_table, style="green"))
    
    # Show errors if any
    if results.get('errors'):
        console.print("\n⚠️ [yellow]Errors encountered:[/yellow]")
        for error in results['errors'][:5]:  # Show first 5 errors
            console.print(f"  • {error}")
        if len(results['errors']) > 5:
            console.print(f"  ... and {len(results['errors']) - 5} more errors")

def create_live_dashboard():
    """
    Create a live updating dashboard for real-time progress
    """
    layout = Layout()
    
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    
    layout["main"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )
    
    return layout
