#!/bin/bash
# WebScraper CLI Installation Checker

echo "🔍 WebScraper CLI Installation Checker"
echo "======================================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEBSCRAPER_DIR="$SCRIPT_DIR"
VENV_DIR="$WEBSCRAPER_DIR/webscraper_env"

echo "📁 Project directory: $WEBSCRAPER_DIR"

# Check if we're in the right directory
if [ ! -f "$WEBSCRAPER_DIR/main.py" ]; then
    echo "❌ Not in WebScraper directory (main.py not found)"
    exit 1
fi

echo "✅ Found main.py"

# Check virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at $VENV_DIR"
    echo "   Run: ./install.sh"
    exit 1
fi

echo "✅ Virtual environment exists"

# Check Python in venv
if [ ! -f "$VENV_DIR/bin/python3" ] && [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "❌ Python not found in virtual environment"
    echo "   Run: rm -rf webscraper_env && ./install.sh"
    exit 1
fi

echo "✅ Python found in virtual environment"

# Activate and check dependencies
source "$VENV_DIR/bin/activate"

PYTHON_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python"
fi

echo "🐍 Using Python: $PYTHON_CMD"

# Check key dependencies (using import names)
DEPS=("typer" "rich" "requests" "bs4" "pydantic" "aiohttp" "loguru")
MISSING_DEPS=()

for dep in "${DEPS[@]}"; do
    if $PYTHON_CMD -c "import $dep" 2>/dev/null; then
        echo "✅ $dep installed"
    else
        echo "❌ $dep missing"
        MISSING_DEPS+=("$dep")
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo ""
    echo "❌ Missing dependencies: ${MISSING_DEPS[*]}"
    echo "   Run: pip install -r requirements-simple.txt"
    exit 1
fi

# Check executables
if [ ! -x "$WEBSCRAPER_DIR/webscraper" ]; then
    echo "❌ webscraper not executable"
    echo "   Run: chmod +x webscraper"
else
    echo "✅ webscraper executable"
fi

if [ ! -x "$WEBSCRAPER_DIR/webscraper-standalone" ]; then
    echo "❌ webscraper-standalone not executable"
    echo "   Run: chmod +x webscraper-standalone"
else
    echo "✅ webscraper-standalone executable"
fi

# Check global symlink
if [ -L "$HOME/.local/bin/webscraper" ]; then
    LINK_TARGET="$(readlink "$HOME/.local/bin/webscraper")"
    echo "✅ Global symlink exists: $HOME/.local/bin/webscraper -> $LINK_TARGET"
else
    echo "⚠️  Global symlink not found"
    echo "   Run: ln -sf $WEBSCRAPER_DIR/webscraper-standalone ~/.local/bin/webscraper"
fi

# Check PATH
if echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo "✅ ~/.local/bin in PATH"
else
    echo "⚠️  ~/.local/bin not in PATH"
    echo "   Add to ~/.zshrc: export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo ""
echo "🧪 Testing CLI..."

# Test CLI
if $PYTHON_CMD main.py --help >/dev/null 2>&1; then
    echo "✅ CLI works locally"
else
    echo "❌ CLI fails locally"
    exit 1
fi

# Test global command if symlink exists
if [ -L "$HOME/.local/bin/webscraper" ]; then
    if "$HOME/.local/bin/webscraper" --help >/dev/null 2>&1; then
        echo "✅ Global webscraper command works"
    else
        echo "❌ Global webscraper command fails"
    fi
fi

echo ""
echo "🎉 Installation check complete!"
echo ""
echo "Usage:"
echo "  webscraper --help"
echo "  webscraper scrape https://example.com"
