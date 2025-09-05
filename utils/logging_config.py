"""
Logging configuration for the web scraper
"""

import sys
from pathlib import Path
from loguru import logger

def setup_logging(output_dir: Path, verbose: bool = False):
    """
    Set up logging configuration
    """
    # Remove default handler
    logger.remove()
    
    # Console handler
    log_level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # File handler for all logs
    log_dir = output_dir / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_dir / "webscraper.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    # Error-only file handler
    logger.add(
        log_dir / "errors.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="5 MB",
        retention="30 days"
    )
    
    logger.info("Logging configured successfully")

def get_logger(name: str):
    """
    Get a logger instance for a specific module
    """
    return logger.bind(name=name)
