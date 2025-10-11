# Changelog

All notable changes to the Quotes Manager project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.1] - 2025-10-11

### Changed
- Clarified project philosophy in README: personal productivity system with open-source code
- Updated "Development" section to "Usage & Forking" to better reflect contribution policy
- Explicitly state that contributions are kept minimal to maintain stability
- Guide forkers to development documentation for customization

### Documentation
- No functionality changes, documentation clarity only

## [1.3.0] - 2025-10-11

### Added
- **Development tooling infrastructure**:
  - `pyproject.toml`: Centralized configuration for Black, Ruff, Bandit
  - `.pre-commit-config.yaml`: Automatic git hooks for code quality
  - `bandit` security scanner for vulnerability detection
  - `DEVELOPMENT.md`: Complete development setup and workflow guide
- **Pre-commit hooks** run automatically before commits:
  - Code formatting (Black)
  - Linting (Ruff with auto-fix)
  - Security scanning (Bandit)
  - File validation (whitespace, YAML, JSON, TOML)
  - Private key detection
  - Python AST validation

### Changed
- Centralized all tool configurations in `pyproject.toml`
- Updated `.claude/workflow/code_standards.md` with pre-commit workflow
- Updated `.claude/README.md` with new tooling references
- Updated `requirements.txt` with bandit and pre-commit

### Developer Notes
- **Setup:** Run `pre-commit install` to enable automatic checks
- **Manual run:** Use `pre-commit run --all-files`
- **Documentation:** See `DEVELOPMENT.md` for complete guide
- **Standards:** See `.claude/workflow/code_standards.md` for workflow

## [1.2.0] - 2025-10-11

### Added
- **Theme selection in interactive menu**: Option 9 now allows changing themes without exiting menu
- **`quotes theme` command**: Select theme interactively or directly (e.g., `quotes theme dark`)
- **Theme preview**: Shows color samples when changing theme
- **Current theme indicator**: Menu shows which theme is currently active with ✓ mark

### Changed
- Interactive menu now has 9 options instead of 8
- Theme changes persist for entire menu session

### Fixed
- **Critical: Typer default parameter bug**: Fixed issue where Typer OptionInfo objects were being used as default values when commands were called directly from menu instead of CLI
- Added explicit `theme=None` to all command calls in menu to prevent Typer object corruption
- **Dynamic theme switching**: `get_color()` now imports module and accesses attribute to get current THEME value
- Fixed Python import caching issue by using `import utils.display` then `utils.display.THEME` instead of `from utils.display import THEME`
- Theme changes now properly apply across all display functions in real-time
- Removed `THEME` parameter from all `get_color()` calls throughout codebase
- **Menu now respects themes**: Updated menu display, prompts, and all UI elements to use theme colors instead of hardcoded values
- Menu colors (title, borders, prompts) now change based on selected theme

## [1.1.0] - 2025-10-11

### Added
- **Accessible Color Theme System**: Choose from 5 color themes for different terminal setups
  - `auto` (default): Adapts to your terminal using Rich's smart colors
  - `dark`: Optimized for dark backgrounds with bright colors
  - `light`: Optimized for light backgrounds with darker colors
  - `high-contrast`: Maximum contrast for accessibility needs
  - `none`: Plain text with no colors
- **Theme Configuration**: Set theme via CLI flag (`--theme`), environment variable (`QUOTES_THEME`), or config file (`~/.config/quotes-manager/config.toml`)
- **New Theme Module** (`utils/themes.py`): Centralized theme management system

### Changed
- All color definitions now use theme system instead of hardcoded values
- Default colors now use Rich's adaptive colors for better cross-terminal compatibility
- Display functions updated to support dynamic theme switching

### Fixed
- Dark blue colors on black backgrounds now visible with adaptive colors
- Dim gray text now has better contrast on dark backgrounds
- Colors now work properly on both dark and light terminal backgrounds

## [1.0.0] - 2025-10-06

### Added - V1.0 Complete

**Phase 4: Daily Quote & Shell Integration**
- **Daily Quote Command** (`commands/daily.py`)
  - Shows different quote each day with 21-day rotation
  - Tracks display history to prevent repeats
  - `--quiet` flag for minimal shell startup display
  - `--force` flag to show new quote even if already shown today
  - Beautiful formatted display with quote metadata
- **Shell Integration Setup** (`commands/setup_shell.py`)
  - Auto-detects shell (zsh, bash, fish)
  - Finds appropriate profile file
  - Shows clear instructions for adding daily quote to shell startup
  - Portable approach that works across different installations

**Phase 5: Quote Explanation**
- **AI Explainer Module** (`ai/explainer.py`)
  - Generates deep, meaningful quote explanations
  - 200-400 word insights covering meaning, context, and application
  - Conversational, thought-provoking style
- **Enhanced View Command**
  - Interactive "Explain" option when viewing quotes
  - `--explain` flag for immediate explanation
  - Option to save explanation to quote notes
  - Seamless AI integration

**Phase 6: Polish & Completion**
- All commands properly return to menu (no premature exits)
- Consistent error handling throughout
- Rich formatting polish across all features
- Comprehensive testing of all features
- Updated documentation

### Added - Phase 3: AI Integration (2025-10-06)
- **Claude API Client** (`ai/claude_client.py`)
  - Wrapper for Anthropic Claude API with error handling
  - JSON response parsing for structured AI outputs
  - Global client instance management
  - API availability checking
- **Category Suggestion** (`ai/categorizer.py`)
  - AI-powered category suggestions from predefined list
  - Returns 2-4 categories with confidence scores
  - Safe fallback when AI unavailable
- **Author Identification** (`ai/author_identifier.py`)
  - Identifies quote authors using Claude's knowledge
  - Returns confidence scores
  - Falls back to "Anonymous" when uncertain
- **Duplicate Detection** (`ai/duplicate_detector.py`)
  - Semantic similarity checking between quotes
  - Pre-filtering by length and common words for efficiency
  - Returns similarity scores and explanations
  - Supports high/medium/exact match levels
- **Enhanced Add Command**
  - Integrated all AI features into quote adding workflow
  - Author lookup when not provided
  - Duplicate detection with user options (update/add anyway/cancel)
  - Category suggestions pre-selected in interactive selector
  - `--skip-ai` flag to disable AI features
  - AI metadata tracked in Quote model

### Changed
- Updated `anthropic` package from 0.34.0 to >=0.69.0 for compatibility
- Enhanced `add_quote` command with AI-powered features
- Quote model already had AIMetadata support

### Added - Phase 2: Basic Commands
- Interactive category selector with predefined categories
- Add, list, view, edit, delete, search commands
- Quote display with IDs in parentheses format
- Interactive menu mode as default
- Installable CLI with `quotes` command

### Added - Phase 1: Core Structure
- Initial project structure
- Project specification and documentation
- Claude Code integration files
- Quote and Config data models
- JSON storage system

## [1.0.0] - TBD

Initial release - Coming soon!

### Planned Features
- Add quotes with AI-powered categorization
- AI duplicate detection
- AI author identification
- Daily quote display with shell integration
- Search and filter by keyword, category, author
- View quote details with AI explanations
- Edit and delete quotes
- Beautiful terminal formatting with Rich
