# Quotes Manager

*A beautiful CLI tool for saving, organizing, and reflecting on meaningful quotes with AI-powered insights.*

**Current Version:** v1.3.1 | [Changelog](CHANGELOG.md)

---

## What It Does

- 💾 **Save & organize quotes** with rich context (source, notes, categories)
- 🤖 **AI-powered intelligence** - automatic categorization, duplicate detection, and author identification
- 📅 **Daily inspiration** - see a different quote each day (no repeats for 21 days)
- 🔍 **Smart search** - find quotes by keyword, category, or author
- 💡 **AI explanations** - get deep insights into what quotes mean
- ✨ **Beautiful terminal** - formatted with Rich for an enjoyable experience

---

## Quick Start

**Want to try it right now?**

```bash
# 1. Clone and install
git clone <repo-url>
cd quotes-manager
pip install .

# 2. Set up API key
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your-key-here

# 3. Run
quotes
```

**That's it!** See [Installation](#installation) for detailed setup.

---

## Installation

### Prerequisites

Before installing, make sure you have:
- **Python 3.9 or newer** ([Check version](https://www.python.org/downloads/): `python3 --version`)
- **pip** (usually comes with Python)
- **Anthropic API key** ([Get one here](https://console.anthropic.com/) - paid service)

### Step 1: Clone the Repository

```bash
git clone <repo-url>
cd quotes-manager
```

### Step 2: Install Dependencies

```bash
# Install the package (includes all dependencies)
pip install .
```

**What this does:** Installs Quotes Manager and all required packages (typer, rich, anthropic, etc.)

### Step 3: Set Up PATH

Add Python's bin directory to your PATH so `quotes` works from anywhere:

```bash
# For macOS - add to ~/.zshrc or ~/.bash_profile:
# Replace X.X with your Python version (check with: python3 --version)
export PATH="$HOME/Library/Python/X.X/bin:$PATH"

# Example for Python 3.11:
export PATH="$HOME/Library/Python/3.11/bin:$PATH"

# For Linux - add to ~/.bashrc or ~/.zshrc:
export PATH="$HOME/.local/bin:$PATH"

# Then reload:
source ~/.zshrc  # or source ~/.bashrc
```

**Tip:** Find your Python version with `python3 --version`

**Verify it works:**
```bash
quotes --version
# Should show: Quotes Manager v1.3.1
```

### Step 4: Configure API Key

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Anthropic API key:
# ANTHROPIC_API_KEY=sk-ant-...
```

Get an API key from [Anthropic's Console](https://console.anthropic.com/).

### Step 5: Run Quotes Manager

```bash
# Launch interactive menu
quotes

# Or if you used requirements.txt only:
python3 main.py
```

**Expected result:** You should see a colorful interactive menu.

### Troubleshooting Installation

**"quotes: command not found"?**
- Check PATH is set correctly (Step 3)
- Or just run: `python3 main.py` from the quotes-manager directory

**Python version too old?**
- Install Python 3.9+ from [python.org](https://www.python.org/downloads/)
- Check version: `python3 --version`

**"No module named 'typer'" or similar?**
- Install dependencies: `pip install .`
- Make sure you're in the quotes-manager directory

**API key not working?**
- Check `.env` file has correct format: `ANTHROPIC_API_KEY=sk-ant-...`
- No quotes around the key
- No spaces around the `=`

---

## How to Use

### Interactive Menu (Recommended)

Simply run:
```bash
quotes
```

You'll see an interactive menu:

```
╔════════════════════════════════════════════╗
║          Quotes Manager - Main Menu        ║
╚════════════════════════════════════════════╝

  1 - Add new quote
  2 - View daily quote
  3 - List all quotes
  4 - Search quotes
  5 - View quote details
  6 - Edit quote
  7 - Delete quote
  8 - Setup shell integration
  9 - Change theme
  0 - Exit

Choice [0]:
```

The menu is the easiest way to use Quotes Manager for daily tasks!

### Direct Commands

You can also run commands directly:

```bash
quotes add           # Add a new quote
quotes daily         # See your daily quote
quotes list          # List all quotes
quotes search "work" # Search by keyword
quotes view <id>     # View quote details
quotes theme         # Change color theme
```

See all commands: `quotes --help`

---

## Common Tasks

### Adding Your First Quote

```bash
quotes add
```

The tool will guide you through:
1. Enter the quote text
2. Enter the author (or let AI identify them)
3. Add source, personal notes (optional)
4. AI suggests categories - select which ones fit
5. AI checks for duplicates

### Viewing Today's Quote

```bash
quotes daily
```

Shows a different quote each day. No repeats for 21 days!

### Searching Your Quotes

```bash
# Search by keyword
quotes search "motivation"

# Filter by category
quotes list --category inspiration

# Filter by author
quotes list --author "Maya Angelou"
```

### Getting Daily Quotes Automatically

```bash
quotes setup
```

This adds a quote to your terminal startup (optional).

### Changing Colors

```bash
quotes theme
```

Choose from 5 themes: auto, dark, light, high-contrast, or none.

---

## Requirements

- Python 3.9+
- Anthropic API key (paid service for AI features)

**Optional:**
- Shell profile for daily quote integration

---

## Data Storage & Privacy

- 🏠 **Your quotes stay local** in `local_data/personal_data/quotes.json`
- 🔒 **API keys** stored in `.env` file (never committed to git)
- ☁️ **AI analysis** sent to Claude API only when you add/explain quotes
- 🚫 **No tracking** or telemetry
- ✅ **Open source** - review all code yourself

**Your private files:**
- `local_data/` - Your quotes and data
- `.env` - Your API key
- Both are automatically excluded from git

---

## Usage & Forking

This project is open source under MIT license. You're welcome to:
- **Fork the repository** and customize for your own needs
- **Report bugs** via GitHub issues
- **Suggest improvements** in discussions

*Note: This is a personal productivity system. While the code is open source, I keep contributions minimal to maintain system stability for personal use.*

### For Developers (Forking/Customization)

If you've forked this project and want to modify it, see:
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Complete setup, tools, and workflow guide

**Quick fork setup:**
```bash
git clone <your-fork-url>
cd quotes-manager
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # Includes dev tools
pre-commit install
# See DEVELOPMENT.md for complete guide
```

### Built With

- [Typer](https://typer.tiangolo.com/) - Modern CLI framework
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal formatting
- [Claude API](https://docs.anthropic.com/) - AI-powered insights

---

## Support

- 📖 **Questions?** Check the [Common Tasks](#common-tasks) section above
- 🐛 **Found a bug?** Open an issue on GitHub
- 💡 **Have an idea?** Start a discussion
- 📚 **Forking/customizing?** See [DEVELOPMENT.md](DEVELOPMENT.md)

---

## Advanced

### Color Themes & Accessibility

Quotes Manager supports 5 color themes:
- **`auto`** (default) - Adapts to your terminal
- **`dark`** - Bright colors for dark backgrounds
- **`light`** - Darker colors for light backgrounds
- **`high-contrast`** - Maximum contrast for accessibility
- **`none`** - Plain text (screen readers)

**Change theme:**
```bash
# Interactive selection
quotes theme

# Direct selection
quotes theme dark

# For one command
quotes list --theme light

# Permanently via config
mkdir -p ~/.config/quotes-manager
echo '[display]
theme = "dark"' > ~/.config/quotes-manager/config.toml
```

**Priority order:** CLI flag > Environment variable > Config file > Default

### All Available Commands

```bash
quotes add           # Add a new quote
quotes daily         # Show today's quote
quotes list          # List all quotes
quotes search        # Search quotes
quotes view          # View quote details
quotes edit          # Edit a quote
quotes delete        # Delete a quote
quotes theme         # Change color theme
quotes setup         # Setup shell integration
quotes --help        # Show all options
```

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

**Version:** v1.3.1 | **Last updated:** 2025-10-12

**Enjoy your daily dose of wisdom! 📖✨**
