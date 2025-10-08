# Quotes Manager

A beautiful CLI tool for saving, organizing, and reflecting on meaningful quotes with AI-powered insights.

## Features

- 💾 **Save quotes** with rich context (source, personal notes, categories)
- 🤖 **AI-powered** categorization, duplicate detection, and author identification
- 📅 **Daily inspiration** - see a different quote each day (no repeats for 21 days)
- 🔍 **Smart search** - find quotes by keyword, category, or author
- 💡 **AI explanations** - get insights into what quotes mean on demand
- ✨ **Beautiful terminal** - formatted with Rich for an enjoyable experience

## Installation

### Step 1: Clone and Install

```bash
# Clone the repository
git clone <repo-url>
cd quotes-manager

# Install the package
pip install .
```

### Step 2: Set Up PATH (Required)

After installation, you need to add Python's user bin directory to your PATH so the `quotes` command works from anywhere:

```bash
# For macOS, add to ~/.zshrc or ~/.bash_profile:
# Note: Replace 3.9 with your Python version if different
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

# For Linux, add to ~/.bashrc or ~/.zshrc:
export PATH="$HOME/.local/bin:$PATH"

# Then reload your shell:
source ~/.zshrc  # or source ~/.bashrc / source ~/.bash_profile
```

**To verify it works:**
```bash
quotes --version
```

You should see: `Quotes Manager v1.0.0-dev`

### Step 3: Configure API Key

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Anthropic API key:
# ANTHROPIC_API_KEY=sk-ant-...
```

You can get an API key from [Anthropic's Console](https://console.anthropic.com/).

### Step 4: Set Up Shell Integration (Optional)

For daily quotes to appear automatically when you open your terminal:

```bash
quotes setup
```

---

### For Developers

If you want to modify the code and see changes immediately, use editable mode:

```bash
pip install -e .
```

This creates a live link to your code, so any changes you make are reflected without reinstalling.

## Quick Start

### Launch the interactive menu (recommended)

Simply run:

```bash
quotes
```

This opens a beautiful interactive menu where you can:

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
  9 - Exit

Choice [9]:
```

The menu is the easiest way to use Quotes Manager for daily tasks!

### Using direct commands

You can also run commands directly (useful for scripting or quick actions):

```bash
# Add a new quote
quotes add

# See your daily quote
quotes daily

# Search by keyword
quotes search "passion work"

# List all quotes
quotes list

# Filter by category or author
quotes list --category inspiration
quotes list --author "Steve Jobs"

# View quote details (with AI explanation option)
quotes view <quote-id>

# Set up shell integration for daily quotes
quotes setup
```

## Available Commands

All commands can be run directly or accessed through the interactive menu:

- `add` - Add a new quote with AI-powered categorization
- `daily` - Show today's quote (no repeats for 21 days)
- `list` - List all quotes (with optional filters)
- `search` - Search quotes by keyword
- `view` - View detailed information with AI explanation option
- `edit` - Edit an existing quote
- `delete` - Delete a quote
- `setup` - Set up automatic daily quotes in your terminal

## Requirements

- Python 3.9+
- Anthropic API key (for AI features)

## Data Storage

All your quotes are stored locally in `local_data/personal_data/quotes.json`. Your data never leaves your machine except for AI analysis via the Claude API.

## Development

Built with:
- [Typer](https://typer.tiangolo.com/) - Modern CLI framework
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal formatting
- [Claude API](https://docs.anthropic.com/) - AI-powered insights

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## License

MIT License - See [LICENSE](LICENSE) for details

## Support

Found a bug or have a feature request? Please open an issue on GitHub.

---

**Enjoy your daily dose of wisdom! 📖✨**
