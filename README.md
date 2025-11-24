# Quotes Manager

*A beautiful CLI tool for saving, organizing, and reflecting on meaningful quotes with AI-powered insights.*

**Current Version:** v1.5.3 | [Changelog](CHANGELOG.md)

---

## What It Does

- 💾 **Save & organize quotes** with rich context (source, notes, categories)
- 🤖 **AI-powered intelligence** - automatic categorization, duplicate detection, and enhanced author identification with web search fallback
- 📅 **Daily inspiration** - see a different quote each day (no repeats for 21 days)
- 🔍 **Smart search** - find quotes by keyword, category, or author
- 💡 **AI explanations** - get deep insights into what quotes mean
- ✨ **Beautiful terminal** - formatted with Rich for an enjoyable experience

---

## Quick Start

**Want to try it right now?**

```bash
# 1. Clone and set up virtual environment
git clone <repo-url>
cd quotes-manager
python3 -m venv venv
source venv/bin/activate

# 2. Install (use -e for editable mode so it finds local data files)
pip install -e .

# 3. Set up API key
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your-key-here

# 4. Run
quotes
```

**That's it!** See [Installation](#installation) for detailed setup.

**Note:** You only run `pip install -e .` **once**. After that, packages stay in your venv automatically.

**For seamless daily use:** This project includes a `.envrc` file. If you have [direnv](https://direnv.net/) installed, the venv auto-activates when you enter the project directory. See "For Daily Use" section below.

---

## 🔒 Privacy & Security

**Your data stays private.** All quotes are stored locally on your machine. AI features are optional and only send data when you explicitly use them.

**Key privacy features:**
- ✅ **Local-first** - All quotes stored in `local_data/personal_data/` (not cloud synced)
- ✅ **Optional AI** - Use `--skip-ai` flag or disable in config to avoid API calls
- ✅ **Secure input handling** - All user input is validated and sanitized
- ✅ **Open source** - Audit the code yourself

**See [PRIVACY.md](PRIVACY.md) for detailed information about:**
- How data is stored and protected
- What data is sent to APIs (and when)
- Best practices for securing your API key
- Transparency and auditability

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

### Step 2: Create Virtual Environment

```bash
# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or on Windows:
# venv\Scripts\activate
```

**Why?** Virtual environments keep project dependencies isolated and avoid conflicts with system Python.

### Step 3: Install Dependencies

```bash
# Install the package in editable mode (includes all dependencies)
pip install -e .
```

**What this does:** Installs Quotes Manager and all required packages (typer, rich, anthropic, etc.) inside your virtual environment. The `-e` flag keeps the package linked to your project so it can find local data files.

### Step 4: Configure API Key

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Anthropic API key:
# ANTHROPIC_API_KEY=sk-ant-...
```

Get an API key from [Anthropic's Console](https://console.anthropic.com/).

### Step 5: (Optional) For Daily Use - Auto-Activate with direnv

If you use multiple tools daily and want automatic venv switching, use **direnv**:

```bash
# One-time setup
brew install direnv

# Add to ~/.zshrc (after starship init):
eval "$(direnv hook zsh)"

# Reload: source ~/.zshrc

# Then in this project directory:
direnv allow
```

**Result:** When you `cd` into this directory, the venv auto-activates. When you leave, it deactivates. Perfect for switching between multiple projects!

**Note:** The `.envrc` file is already included in this project.

### Step 6: Run Quotes Manager

```bash
# Launch interactive menu
quotes

# Or if using requirements.txt only:
python3 main.py
```

**Expected result:** You should see a colorful interactive menu.

### Troubleshooting Installation

**Fresh clone and "quotes: command not found"?**
- The `.venv` folder might not exist yet. Create it:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e .
  ```

**".venv folder doesn't exist" after cloning?**
- It's gitignored (only created locally). Run:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e .
  ```

**"quotes: command not found" after installation?**
- Make sure your virtual environment is activated: `source .venv/bin/activate`
- Or if using direnv: `direnv allow` in the project directory
- Or use full path: `/path/to/quotes-manager/.venv/bin/quotes`
- Or run: `python3 main.py` from the quotes-manager directory

**"externally-managed-environment" error when installing?**
- You're not in a virtual environment. Activate it: `source .venv/bin/activate`
- Then try: `pip install -e .` again

**Python version too old?**
- Install Python 3.9+ from [python.org](https://www.python.org/downloads/)
- Check version: `python3 --version`

**"No module named 'typer'" or similar?**
- Make sure your virtual environment is activated: `source .venv/bin/activate`
- Then install: `pip install -e .`
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

**Default: Terminal with full arrow key support**
- By default, you get a rich multiline editor right in your terminal
- Use arrow keys (↑↓←→) to navigate anywhere in your text
- Ctrl+D or Esc+Enter to finish
- Auto-cleans pasted content (removes borders, ANSI codes, etc.)
- Requires `prompt_toolkit` (included in requirements.txt)

**Alternative: Use your external editor**
- For longer quotes, use your preferred editor
- Run with the flag:
  ```bash path=null start=null
  quotes add --editor
  ```
- Set your editor:
  ```bash path=null start=null
  export EDITOR="code -w"   # VS Code
  export EDITOR="nano"       # Nano (default)
  export EDITOR="vim"        # Vim
  ```
- Make it default:
  ```bash path=null start=null
  export QUOTES_USE_EDITOR=1
  ```

**Fallback: Simple mode**
- If prompt_toolkit isn't available, falls back to sentinel mode
- Type your text, then type END on its own line to finish

Example:
```text path=null start=null
Quote text (multi-line supported)
Paste or type your text. When finished, type END on its own line and press Enter.

│  Your pasted quote line 1
│  Your pasted quote line 2
END
```
Saved text becomes:
```text path=null start=null
Your pasted quote line 1
Your pasted quote line 2
```

The tool will guide you through:
1. Enter the quote text (multi-line; finish with END)
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

This command shows you how to add a daily quote to your shell startup (optional).

**What it does:**
- Shows your shell type (zsh, bash, fish)
- Displays the command to add to your shell config
- Instructions for editing your profile file (`.zshrc`, `.bashrc`, etc.)

**The command added to your profile:**
```bash
/path/to/quotes-manager/.venv/bin/quotes daily --quiet
```

This uses the full path to the `quotes` command in your venv, so it works even when the venv isn't activated. The `--quiet` flag shows a minimal format suitable for terminal startup.

**After setup:**
- Open a new terminal → Your daily quote appears automatically
- Each day gets a different quote (no repeats for 21 days)

### Changing Colors

```bash
quotes theme
```

Choose from 5 themes: auto, dark, light, high-contrast, or none.

---

## Features in Detail

### Enhanced Author Identification
Quotes Manager uses a smart two-tier approach for identifying quote authors:

1. **Claude First**: Uses Claude's extensive knowledge base (trained through Jan 2025)
   - Fast and free
   - Works well for famous quotes

2. **Web Search Fallback**: If Claude is uncertain, automatically searches the web
   - Improves success rate from ~30% to ~70-80%
   - Great for obscure, recent, or lesser-known quotes
   - Gracefully handles network issues

You can disable web search in the configuration if you prefer:
```json
{
  "preferences": {
    "enable_web_search_author": false
  }
}
```

---

## Requirements

- Python 3.9+
- Anthropic API key (paid service for AI features)
- Internet connection (optional, for web search fallback)

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

**Version:** v1.5.0 | **Last updated:** 2025-10-12

**Enjoy your daily dose of wisdom! 📖✨**
