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

```bash
# Clone the repository
git clone <repo-url>
cd quotes-manager

# Install in development mode (creates 'quotes' command)
pip install -e .

# Set up your API key
cp .env.example .env
# Edit .env and add your Anthropic API key:
# ANTHROPIC_API_KEY=sk-ant-...

# Set up shell integration (optional but recommended)
quotes setup
```

After installation, you can use the `quotes` command directly from anywhere in your terminal!

**Note:** If the `quotes` command is not found, you may need to add Python's user bin directory to your PATH:

```bash
# For macOS/Linux, add to ~/.zshrc or ~/.bashrc:
export PATH="$HOME/Library/Python/3.9/bin:$PATH"  # macOS
export PATH="$HOME/.local/bin:$PATH"              # Linux

# Then reload your shell:
source ~/.zshrc  # or source ~/.bashrc
```

## Quick Start

### Add your first quote

```bash
quotes add
```

Follow the interactive prompts to add a quote with context. The AI will:
- Identify the author if you don't know it
- Check for duplicates in your collection
- Suggest relevant categories

### See your daily quote

```bash
quotes daily
```

Or set up shell integration so it appears automatically when you open your terminal!

### Search your collection

```bash
# Search by keyword
quotes search "passion work"

# List all quotes
quotes list

# Filter by category
quotes list --category inspiration

# Filter by author
quotes list --author "Steve Jobs"
```

### View quote details

```bash
quotes view <quote-id>
```

Press `E` to get an AI explanation of the quote!

## Commands

- `add` - Add a new quote to your collection
- `daily` - Show today's quote
- `list` - List all quotes (with optional filters)
- `search` - Search quotes by keyword
- `view` - View detailed information about a quote
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
