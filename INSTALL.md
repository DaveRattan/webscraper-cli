# 🚀 Installation Guide

## Quick Start (Automated)

1. **Run the installation script**:
   ```bash
   ./install.sh
   ```
   
   This automated script will:
   - Install all Python dependencies
   - Make all scripts executable
   - Optionally install Playwright for better PDF conversion
   - Create a global symlink (if you have sudo permissions)

2. **Test the installation**:
   ```bash
   ./test_basic.py
   ```

3. **Run the CLI**:
   ```bash
   ./webscraper scrape https://example.com
   # OR (if globally installed)
   webscraper scrape https://example.com
   ```

## Manual Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements-simple.txt
   ```

2. **Make scripts executable**:
   ```bash
   chmod +x webscraper main.py test_basic.py demo.py install.sh
   ```

3. **Install optional PDF conversion tools** (recommended):
   ```bash
   # Install Playwright (best option)
   playwright install chromium
   
   # OR install wkhtmltopdf (alternative)
   # macOS: brew install wkhtmltopdf
   # Ubuntu: sudo apt-get install wkhtmltopdf
   # Windows: Download from https://wkhtmltopdf.org/downloads.html
   ```

4. **Test the installation**:
   ```bash
   ./test_basic.py
   ```

5. **Run the CLI**:
   ```bash
   ./webscraper scrape https://example.com
   ```

## Installation Options

### Option 1: Using pip (recommended)
```bash
# Install all dependencies
pip install -r requirements-simple.txt

# Install optional Playwright for better PDF conversion
playwright install chromium
```

### Option 2: Using conda
```bash
# Create conda environment
conda create -n webscraper python=3.9
conda activate webscraper

# Install dependencies
pip install -r requirements-simple.txt
playwright install chromium
```

### Option 3: Using virtual environment
```bash
# Create virtual environment
python3 -m venv webscraper_env
source webscraper_env/bin/activate  # On Windows: webscraper_env\Scripts\activate

# Install dependencies
pip install -r requirements-simple.txt
playwright install chromium
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure you've installed all dependencies with `pip install -r requirements.txt`

2. **PDF conversion fails**: Install Playwright with `playwright install chromium` or wkhtmltopdf

3. **Permission errors**: Make sure you have write permissions to the output directory

4. **Network timeouts**: Some websites may be slow; the tool will retry automatically

### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 1GB RAM (more for large sites)
- **Disk Space**: Varies based on content being scraped

### Optional Dependencies

- **Playwright**: Best PDF conversion quality (recommended)
- **wkhtmltopdf**: Alternative PDF conversion tool
- **Chrome/Chromium**: Fallback PDF conversion option

## Verification

After installation, run the test script:

```bash
python3 test_basic.py
```

You should see:
```
🧪 Testing WebScraper Basic Functionality
📦 Testing Imports
✅ Core modules imported successfully
✅ CLI modules imported successfully  
✅ Utils modules imported successfully
🎉 All tests passed!
✨ WebScraper is ready to use!
```

## Usage

Once installed, you can start using the webscraper:

```bash
# Basic usage
python3 main.py scrape https://example.com

# With custom output directory
python3 main.py scrape https://example.com --output ./my_scraped_content

# Non-interactive mode
python3 main.py scrape https://example.com --no-interactive --depth 2
```

## Getting Help

```bash
# Show help
python3 main.py --help

# Show command-specific help
python3 main.py scrape --help
```
