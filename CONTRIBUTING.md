# Contributing to WebScraper CLI

Thank you for your interest in contributing to WebScraper CLI! 🕷️

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/webscraper-cli.git
   cd webscraper-cli
   ```
3. **Set up the development environment**:
   ```bash
   ./install.sh
   # Or manually:
   python3 -m venv webscraper_env
   source webscraper_env/bin/activate
   pip install -r requirements-simple.txt
   ```

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and test them:
   ```bash
   python test_basic.py  # Run basic tests
   ./webscraper --help   # Test CLI
   ```

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: your feature description"
   ```

4. **Push and create a Pull Request**:
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

- Follow PEP 8 Python style guidelines
- Use type hints where possible
- Add docstrings to functions and classes
- Keep functions focused and modular

## Testing

- Test your changes with `python test_basic.py`
- Ensure CLI commands work: `./webscraper --help`
- Test with different Python versions if possible

## Areas for Contribution

- 🐛 **Bug fixes** - Fix issues or improve error handling
- ✨ **New features** - Add new scraping capabilities
- 📚 **Documentation** - Improve README, add examples
- 🧪 **Testing** - Add more comprehensive tests
- 🎨 **UI/UX** - Improve CLI interface and user experience
- 🚀 **Performance** - Optimize scraping speed and memory usage

## Reporting Issues

When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages (if any)

## Questions?

Feel free to open an issue for questions or discussions!

---

Thanks for contributing! 🎉
