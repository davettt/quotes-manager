# Changelog

All notable changes to the Quotes Manager project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - V1.0 Complete (2025-10-06)

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
