# 🕷️ WebScraper CLI

A comprehensive command-line tool for web scraping, crawling, and PDF conversion. This tool allows you to explore websites visually, select specific paths to scrape, and automatically convert web pages to PDF while downloading all supported document files.

## ✨ Features

- **🌐 Web Crawling**: Discover and map entire website structures
- **🎯 Interactive Path Selection**: Visual tree interface to select which paths to process
- **📄 Automatic PDF Conversion**: Convert every visited webpage to PDF
- **📥 Smart File Downloads**: Automatically detect and download documents (PDF, Word, Excel, PowerPoint, etc.)
- **📁 Organized Storage**: Automatically organize all content in structured folders
- **🚀 Concurrent Processing**: Fast parallel processing with rate limiting
- **🛡️ Respectful Crawling**: Built-in delays and robots.txt respect
- **📊 Progress Tracking**: Real-time progress bars and status updates
- **📈 Detailed Reporting**: Comprehensive summary reports and metadata

## 🚀 Quick Start

### Installation

#### Option 1: Automated Installation (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd webscraper
   ```

2. **Run the installation script**:
   ```bash
   ./install.sh
   ```
   
   This will:
   - Install all Python dependencies
   - Make scripts executable
   - Optionally install Playwright for better PDF conversion
   - Create a global symlink (if you have permissions)

#### Option 2: Manual Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd webscraper
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Make scripts executable**:
   ```bash
   chmod +x webscraper main.py test_basic.py demo.py
   ```

4. **Install additional tools** (optional but recommended):
   ```bash
   # For better PDF conversion
   playwright install chromium
   
   # Or install wkhtmltopdf
   # Ubuntu/Debian: sudo apt-get install wkhtmltopdf
   # macOS: brew install wkhtmltopdf
   # Windows: Download from https://wkhtmltopdf.org/downloads.html
   ```

### Basic Usage

```bash
# Option 1: Use the executable (recommended)
./webscraper scrape https://example.com

# Option 2: Use Python directly
python3 main.py scrape https://example.com

# Specify output directory
./webscraper scrape https://example.com --output ./my_scraped_content

# Set maximum crawl depth
./webscraper scrape https://example.com --depth 5

# Non-interactive mode (process all discovered paths)
./webscraper scrape https://example.com --no-interactive
```

## 📖 Detailed Usage

### Command Options

```bash
./webscraper scrape [URL] [OPTIONS]
# OR
python3 main.py scrape [URL] [OPTIONS]
```

**Options:**
- `--output, -o`: Output directory (default: prompts user)
- `--depth, -d`: Maximum crawl depth (default: 3)
- `--interactive/--no-interactive`: Enable/disable interactive path selection (default: interactive)

### Interactive Mode

When running in interactive mode (default), the tool will:

1. **Discover the website structure** by crawling from the root URL
2. **Display a visual tree** showing all discovered pages and files
3. **Let you select** which paths you want to process
4. **Process selected paths** by converting to PDF and downloading files

### Non-Interactive Mode

In non-interactive mode (`--no-interactive`), the tool will automatically process all discovered paths without user intervention.

## 📁 Output Structure

The tool creates an organized directory structure:

```
output_directory/
├── pages/              # PDF versions of web pages
│   ├── example.com_page1.pdf
│   └── example.com_page2.pdf
├── files/              # Downloaded files organized by type
│   ├── pdf/           # PDF documents
│   ├── doc/           # Word documents (.doc, .docx)
│   ├── xls/           # Excel files (.xls, .xlsx)
│   ├── ppt/           # PowerPoint files (.ppt, .pptx)
│   ├── txt/           # Text files
│   └── other/         # Other supported formats
├── html/              # Raw HTML files (optional)
├── logs/              # Log files
├── metadata/          # Metadata and index files
├── session_info.json # Session information
├── content_index.json# Content index
└── SUMMARY.md         # Human-readable summary
```

## 🔧 Configuration

### Supported File Types

The tool automatically detects and downloads these file types:

- **Documents**: PDF, DOC, DOCX, RTF, TXT, CSV
- **Spreadsheets**: XLS, XLSX, ODS
- **Presentations**: PPT, PPTX, ODP
- **OpenDocument**: ODT, ODS, ODP
- **Archives**: ZIP, RAR, TAR, GZ (optional)
- **Images**: JPG, PNG, GIF, SVG (optional)

### Advanced Configuration

You can customize the behavior by modifying the configuration:

```python
# Example configuration options
max_depth = 3                    # Maximum crawl depth
max_concurrent_requests = 5      # Concurrent requests limit
crawl_delay = 1.0               # Delay between requests (seconds)
respect_robots_txt = True       # Respect robots.txt
allow_subdomains = True         # Allow crawling subdomains
```

## 🛠️ Technical Details

### PDF Conversion Backends

The tool supports multiple PDF conversion backends (automatically detected):

1. **Playwright** (recommended) - Best for modern websites with JavaScript
2. **WeasyPrint** - Good for static HTML/CSS
3. **pdfkit/wkhtmltopdf** - Reliable fallback option
4. **Chrome Headless** - System fallback

### Performance Features

- **Concurrent Processing**: Multiple pages processed simultaneously
- **Rate Limiting**: Respectful crawling with configurable delays
- **Memory Efficient**: Streaming downloads for large files
- **Resume Capability**: Can resume interrupted sessions
- **Smart Deduplication**: Avoids downloading the same file multiple times

### Error Handling

- **Graceful Failures**: Continues processing even if individual pages fail
- **Comprehensive Logging**: Detailed logs for troubleshooting
- **Error Reporting**: Summary of all errors encountered
- **Retry Logic**: Automatic retries for transient failures

## 📊 Examples

### Example 1: Basic Website Scraping

```bash
./webscraper scrape https://docs.python.org
```

This will:
1. Crawl the Python documentation site
2. Show you a visual tree of all discovered pages
3. Let you select which sections to download
4. Convert selected pages to PDF and download any document files

### Example 2: Deep Crawling with Custom Output

```bash
./webscraper scrape https://example.com --depth 5 --output ./example_backup
```

This will crawl up to 5 levels deep and save everything to `./example_backup/`.

### Example 3: Automated Processing

```bash
./webscraper scrape https://research-site.edu --no-interactive --depth 2
```

This will automatically process all discovered pages without user interaction.

## 🔍 Troubleshooting

### Common Issues

1. **PDF conversion fails**:
   - Install Playwright: `playwright install chromium`
   - Or install wkhtmltopdf system package

2. **Permission errors**:
   - Ensure you have write permissions to the output directory
   - Try running with elevated permissions if needed

3. **Network timeouts**:
   - Some sites may be slow; the tool will retry automatically
   - Check your internet connection

4. **Memory usage**:
   - For very large sites, consider reducing `max_concurrent_requests`
   - Use smaller `max_depth` values

### Logging

Detailed logs are saved to `output_directory/logs/` for troubleshooting.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and legitimate research purposes. Always respect website terms of service, robots.txt files, and applicable laws. Be respectful with your crawling frequency and don't overload servers.
