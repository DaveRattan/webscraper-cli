"""
Configuration management for the web scraper
"""

from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, field_validator, Field
import json

class Config(BaseModel):
    """
    Configuration settings for the web scraper
    """
    
    # Output settings
    output_dir: Path
    
    # Crawling settings
    max_depth: int = 3
    max_links_per_page: int = 50
    max_concurrent_requests: int = 5
    max_concurrent_downloads: int = 3
    crawl_delay: float = 1.0  # seconds between requests
    
    # Domain settings
    allow_subdomains: bool = True
    respect_robots_txt: bool = True
    
    # File settings
    supported_extensions: List[str] = Field(default_factory=lambda: [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.txt', '.rtf', '.csv', '.odt', '.ods', '.odp'
    ])
    
    # UI settings
    interactive: bool = True
    show_progress: bool = True
    
    # PDF conversion settings
    pdf_format: str = 'A4'
    pdf_margin: str = '1cm'
    
    model_config = {"arbitrary_types_allowed": True}
    
    @field_validator('output_dir', mode='before')
    @classmethod
    def validate_output_dir(cls, v):
        """Ensure output_dir is a Path object"""
        if isinstance(v, str):
            return Path(v)
        return v
    
    @field_validator('max_depth')
    @classmethod
    def validate_max_depth(cls, v):
        """Ensure max_depth is reasonable"""
        if v < 1:
            raise ValueError("max_depth must be at least 1")
        if v > 10:
            raise ValueError("max_depth should not exceed 10 for performance reasons")
        return v
    
    @field_validator('crawl_delay')
    @classmethod
    def validate_crawl_delay(cls, v):
        """Ensure crawl_delay is reasonable"""
        if v < 0:
            raise ValueError("crawl_delay cannot be negative")
        if v > 60:
            raise ValueError("crawl_delay should not exceed 60 seconds")
        return v
    
    def save_to_file(self, config_path: Path):
        """Save configuration to a JSON file"""
        try:
            config_data = self.model_dump()
            # Convert Path to string for JSON serialization
            config_data['output_dir'] = str(config_data['output_dir'])
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            raise ValueError(f"Could not save config to {config_path}: {e}")
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> 'Config':
        """Load configuration from a JSON file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            return cls(**config_data)
            
        except Exception as e:
            raise ValueError(f"Could not load config from {config_path}: {e}")
    
    def get_user_agent(self) -> str:
        """Get user agent string"""
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    def get_request_headers(self) -> dict:
        """Get default request headers"""
        return {
            'User-Agent': self.get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def create_output_structure(self):
        """Create the output directory structure"""
        try:
            # Main output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Subdirectories
            (self.output_dir / 'pages').mkdir(exist_ok=True)  # PDF pages
            (self.output_dir / 'files').mkdir(exist_ok=True)  # Downloaded files
            (self.output_dir / 'html').mkdir(exist_ok=True)   # Raw HTML (optional)
            (self.output_dir / 'logs').mkdir(exist_ok=True)   # Log files
            
            # Create subdirectories for different file types
            file_types = ['pdf', 'doc', 'xls', 'ppt', 'txt', 'other']
            for file_type in file_types:
                (self.output_dir / 'files' / file_type).mkdir(exist_ok=True)
                
        except Exception as e:
            raise ValueError(f"Could not create output structure: {e}")
    
    def get_summary(self) -> dict:
        """Get a summary of current configuration"""
        return {
            'output_directory': str(self.output_dir),
            'max_crawl_depth': self.max_depth,
            'concurrent_requests': self.max_concurrent_requests,
            'crawl_delay': f"{self.crawl_delay}s",
            'supported_file_types': len(self.supported_extensions),
            'interactive_mode': self.interactive,
            'respect_robots_txt': self.respect_robots_txt
        }

class ConfigManager:
    """
    Manages configuration loading, saving, and defaults
    """
    
    DEFAULT_CONFIG_NAME = 'webscraper_config.json'
    
    @staticmethod
    def get_default_config_path() -> Path:
        """Get the default configuration file path"""
        # Try to use user's home directory
        home_dir = Path.home()
        config_dir = home_dir / '.webscraper'
        config_dir.mkdir(exist_ok=True)
        return config_dir / ConfigManager.DEFAULT_CONFIG_NAME
    
    @staticmethod
    def create_default_config(output_dir: Path) -> Config:
        """Create a default configuration"""
        return Config(output_dir=output_dir)
    
    @staticmethod
    def load_or_create_config(output_dir: Path, config_path: Optional[Path] = None) -> Config:
        """Load existing config or create default"""
        if config_path is None:
            config_path = ConfigManager.get_default_config_path()
        
        if config_path.exists():
            try:
                config = Config.load_from_file(config_path)
                # Update output directory if provided
                config.output_dir = output_dir
                return config
            except Exception:
                # If loading fails, create default
                pass
        
        # Create default config
        config = ConfigManager.create_default_config(output_dir)
        
        # Try to save it for next time
        try:
            config.save_to_file(config_path)
        except Exception:
            pass  # Not critical if we can't save
        
        return config
    
    @staticmethod
    def update_config(config: Config, **kwargs) -> Config:
        """Update configuration with new values"""
        config_dict = config.dict()
        config_dict.update(kwargs)
        return Config(**config_dict)
