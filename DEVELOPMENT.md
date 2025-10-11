# Development Setup

**Note:** This guide is for developers who have **forked** this project and want to customize it for their own needs. This is a personal productivity system - contributions to the main repository are kept minimal to maintain stability.

If you're looking to use Quotes Manager as-is, see the main [README.md](README.md) instead.

---

Complete guide for setting up your development environment for your fork of Quotes Manager.

## Initial Setup

1. **Clone and create virtual environment:**
   ```bash
   cd ~/path/to/quotes-manager
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

   This sets up automatic code quality checks that run before every commit.

## Development Tools

### Black - Code Formatter
Automatically formats Python code to be consistent (88 char line length).

```bash
black .              # Format all files
black --check .      # Check without changing files
black main.py        # Format specific file
```

### Ruff - Fast Linter
Catches bugs, style issues, and unused imports. Much faster than pylint/flake8.

```bash
ruff check .         # Check all files
ruff check --fix .   # Auto-fix issues
ruff check main.py   # Check specific file
```

### Bandit - Security Scanner
Scans for common security vulnerabilities in Python code.

```bash
bandit -r . -c pyproject.toml    # Scan all files
bandit commands/add.py            # Scan specific file
```

### Pre-commit - Automatic Checks
Runs all checks automatically before every commit. Configured in `.pre-commit-config.yaml`.

```bash
pre-commit run --all-files        # Run manually on all files
pre-commit run black              # Run specific hook
pre-commit autoupdate             # Update hook versions
git commit --no-verify            # Skip hooks (not recommended!)
```

## Workflow

### Standard Development Flow

1. **Make changes** to Python files

2. **Test manually:**
   ```bash
   quotes list
   quotes add "Test quote" --author "Me" --skip-ai
   ```

3. **Commit changes:**
   ```bash
   git add .
   git commit -m "Add new feature"
   ```

   Pre-commit hooks automatically run:
   - ✓ Black formats code
   - ✓ Ruff checks for issues
   - ✓ Bandit scans for security problems
   - ✓ Various file checks (whitespace, YAML, etc.)

4. **If hooks fail:**
   - Read the error messages
   - Fix the issues (often auto-fixed by hooks)
   - Stage fixes: `git add .`
   - Commit again: `git commit -m "Add new feature"`

### Running Tools Manually

You can run tools before committing:

```bash
# Full workflow (recommended)
black . && ruff check --fix . && ruff check .

# Individual tools
black .                          # Format code
ruff check --fix .              # Fix linting
bandit -r . -c pyproject.toml   # Security scan
pre-commit run --all-files      # Run all hooks
```

## Configuration

All tool configurations centralized in `pyproject.toml`:
- **Black** - Formatting rules (line length, target Python versions)
- **Ruff** - Linting rules (enabled checks, ignored rules)
- **Bandit** - Security scanning rules (excluded dirs, skipped tests)
- **Pytest** - Testing configuration (for future tests)

To modify behavior, edit `pyproject.toml`.

## Project Structure

```
quotes-manager/
├── .claude/                    # Claude Code configuration
│   ├── README.md              # Start here for Claude sessions
│   ├── specs/                 # Feature specifications
│   └── workflow/              # Code standards & workflow
├── commands/                   # CLI command implementations
├── ai/                        # AI integration modules
├── utils/                     # Utility functions
├── models/                    # Data models
├── local_data/                # User data (gitignored)
├── pyproject.toml             # Tool configuration
├── .pre-commit-config.yaml    # Pre-commit hooks
├── requirements.txt           # Dependencies
└── DEVELOPMENT.md             # This file
```

## Troubleshooting

### Pre-commit hooks not running
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Verify installation
pre-commit --version
```

### Ruff reports errors I don't understand
```bash
# Explain specific error code
ruff rule E501
ruff rule F401

# List all available rules
ruff linter
```

### Bandit false positives
If Bandit flags something that's actually safe, add it to `pyproject.toml`:
```toml
[tool.bandit]
skips = ["B101"]  # Skip assert_used check
```

### Black and my editor conflict
Configure your editor to:
- Use Black as the formatter
- Set line-length = 88
- Enable "format on save"

**VS Code:** Install Python extension, add to settings.json:
```json
{
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

### Tool versions mismatch
```bash
# Update all hooks to latest versions
pre-commit autoupdate

# Update pip packages
pip install --upgrade -r requirements.txt
```

## Best Practices

1. **Commit frequently** - Small, focused commits are easier to review
2. **Let tools guide you** - They catch issues early
3. **Don't skip hooks** - Use `--no-verify` only in emergencies
4. **Read error messages** - They tell you exactly what to fix
5. **Keep dependencies updated** - Run updates monthly
6. **Test before committing** - Manual testing catches what tools don't
7. **Write descriptive commits** - Future you will thank you

## Git Workflow

```bash
# Make changes
vim commands/new_feature.py

# Test manually
quotes list

# Check what changed
git status
git diff

# Stage and commit (hooks run automatically)
git add .
git commit -m "Add new feature: brief description"

# If commit fails due to hooks, fix and retry
git add .
git commit -m "Add new feature: brief description"
```

## Adding New Dependencies

1. Add to `requirements.txt`
2. Install: `pip install -r requirements.txt`
3. Test the new dependency works
4. Commit the updated requirements.txt

## Resources

- **Black:** https://black.readthedocs.io/
- **Ruff:** https://docs.astral.sh/ruff/
- **Bandit:** https://bandit.readthedocs.io/
- **Pre-commit:** https://pre-commit.com/
- **Python packaging:** https://packaging.python.org/

## For Claude Code

See `.claude/README.md` for:
- Project architecture
- Code standards
- Feature specifications
- Session starter templates

See `.claude/workflow/code_standards.md` for:
- Standard development workflow
- Pre-commit integration
- Quality checklist
