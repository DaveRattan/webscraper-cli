#!/bin/bash
# WebScraper CLI Installation Script

set -e  # Exit on any error

echo "🕷️  WebScraper CLI Installation"
echo "================================"

# Get the current directory (where the script is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEBSCRAPER_DIR="$SCRIPT_DIR"

echo "📁 WebScraper directory: $WEBSCRAPER_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.8 or higher and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if ! pip3 install -r "$WEBSCRAPER_DIR/requirements-simple.txt"; then
    echo "❌ Failed to install Python dependencies"
    echo "   Try running: pip3 install -r requirements-simple.txt"
    exit 1
fi

echo "✅ Python dependencies installed"

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x "$WEBSCRAPER_DIR/main.py"
chmod +x "$WEBSCRAPER_DIR/webscraper"
chmod +x "$WEBSCRAPER_DIR/test_basic.py"
chmod +x "$WEBSCRAPER_DIR/demo.py"

echo "✅ Scripts made executable"

# Create symlink in /usr/local/bin (if possible)
SYMLINK_PATH="/usr/local/bin/webscraper"

if [ -w "/usr/local/bin" ]; then
    echo "🔗 Creating global symlink..."
    ln -sf "$WEBSCRAPER_DIR/webscraper" "$SYMLINK_PATH"
    echo "✅ WebScraper installed globally as 'webscraper'"
    echo "   You can now run: webscraper scrape https://example.com"
else
    echo "⚠️  Cannot create global symlink (no write permission to /usr/local/bin)"
    echo "   You can still run WebScraper from this directory:"
    echo "   ./webscraper scrape https://example.com"
    echo ""
    echo "   To install globally, run with sudo:"
    echo "   sudo ./install.sh"
fi

# Optional: Install Playwright for better PDF conversion
echo ""
echo "🎭 Optional: Install Playwright for better PDF conversion?"
read -p "   Install Playwright? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Installing Playwright..."
    if playwright install chromium; then
        echo "✅ Playwright installed successfully"
    else
        echo "⚠️  Playwright installation failed (optional)"
    fi
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "🧪 Test the installation:"
echo "   ./test_basic.py"
echo ""
echo "🚀 Start using WebScraper:"
if [ -L "$SYMLINK_PATH" ]; then
    echo "   webscraper scrape https://example.com"
else
    echo "   ./webscraper scrape https://example.com"
fi
echo ""
echo "📚 For help:"
if [ -L "$SYMLINK_PATH" ]; then
    echo "   webscraper --help"
else
    echo "   ./webscraper --help"
fi
