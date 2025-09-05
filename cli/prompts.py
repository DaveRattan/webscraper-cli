"""
Interactive prompts using Rich and Questionary
"""

from pathlib import Path
from typing import List, Optional
import questionary
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

def get_save_directory() -> str:
    """
    Prompt user for save directory with validation
    """
    console.print(Panel("📁 [bold]Output Directory Setup[/bold]", style="blue"))
    
    while True:
        directory = Prompt.ask(
            "Enter the directory path to save scraped content",
            default="./scraped_content"
        )
        
        path = Path(directory).expanduser().resolve()
        
        # Check if directory exists or can be created
        try:
            if path.exists():
                if not path.is_dir():
                    console.print(f"❌ [red]{path} exists but is not a directory[/red]")
                    continue
                
                if any(path.iterdir()):
                    overwrite = questionary.confirm(
                        f"Directory {path} is not empty. Continue anyway?"
                    ).ask()
                    if not overwrite:
                        continue
            else:
                # Try to create the directory
                path.mkdir(parents=True, exist_ok=True)
                console.print(f"✅ Created directory: {path}")
            
            return str(path)
            
        except PermissionError:
            console.print(f"❌ [red]Permission denied: Cannot create/access {path}[/red]")
        except Exception as e:
            console.print(f"❌ [red]Error with directory {path}: {e}[/red]")

def show_crawl_options() -> dict:
    """
    Show crawling configuration options
    """
    console.print(Panel("🕷️ [bold]Crawling Options[/bold]", style="green"))
    
    options = {}
    
    # Max depth
    options['max_depth'] = questionary.text(
        "Maximum crawl depth (how many levels deep to go):",
        default="3",
        validate=lambda x: x.isdigit() and int(x) > 0
    ).ask()
    options['max_depth'] = int(options['max_depth'])
    
    # Rate limiting
    options['delay'] = questionary.text(
        "Delay between requests (seconds):",
        default="1.0",
        validate=lambda x: x.replace('.', '').isdigit()
    ).ask()
    options['delay'] = float(options['delay'])
    
    # File types to download
    file_types = questionary.checkbox(
        "Select file types to download:",
        choices=[
            "PDF (.pdf)",
            "Word Documents (.doc, .docx)",
            "Excel Files (.xls, .xlsx)",
            "PowerPoint (.ppt, .pptx)",
            "Text Files (.txt)",
            "Images (.jpg, .png, .gif)",
            "Archives (.zip, .rar, .tar)"
        ],
        default=["PDF (.pdf)", "Word Documents (.doc, .docx)", "Excel Files (.xls, .xlsx)"]
    ).ask()
    
    options['file_types'] = file_types
    
    # Respect robots.txt
    options['respect_robots'] = questionary.confirm(
        "Respect robots.txt?",
        default=True
    ).ask()
    
    return options

def confirm_crawl_start(url: str, output_dir: str, options: dict) -> bool:
    """
    Show summary and confirm before starting crawl
    """
    console.print(Panel(
        f"[bold]Ready to start crawling![/bold]\n\n"
        f"🌐 URL: {url}\n"
        f"📁 Output: {output_dir}\n"
        f"🔍 Max Depth: {options.get('max_depth', 3)}\n"
        f"⏱️  Delay: {options.get('delay', 1.0)}s\n"
        f"📄 File Types: {len(options.get('file_types', []))} selected",
        title="Crawl Summary",
        style="yellow"
    ))
    
    return questionary.confirm("Start crawling?").ask()

def select_paths_to_process(discovered_paths: List[str]) -> List[str]:
    """
    Allow user to select which discovered paths to process
    """
    if not discovered_paths:
        return []
    
    console.print(Panel(f"🔍 [bold]Discovered {len(discovered_paths)} paths[/bold]", style="blue"))
    
    # Show preview of paths
    for i, path in enumerate(discovered_paths[:10]):  # Show first 10
        console.print(f"  {i+1}. {path}")
    
    if len(discovered_paths) > 10:
        console.print(f"  ... and {len(discovered_paths) - 10} more")
    
    # Selection options
    choice = questionary.select(
        "How would you like to proceed?",
        choices=[
            "Process all paths",
            "Select specific paths",
            "Process first 10 paths only",
            "Cancel"
        ]
    ).ask()
    
    if choice == "Process all paths":
        return discovered_paths
    elif choice == "Process first 10 paths only":
        return discovered_paths[:10]
    elif choice == "Select specific paths":
        return questionary.checkbox(
            "Select paths to process:",
            choices=discovered_paths
        ).ask()
    else:
        return []
