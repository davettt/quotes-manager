# Privacy & Security Policy

**Quotes Manager** is designed with privacy and security as core principles. This document explains how your data is handled and what happens when you use AI features.

---

## 🏠 Local-First Architecture

**Your quotes stay on your machine.** All quote data is stored locally in:

```
local_data/personal_data/quotes.json
local_data/personal_data/config.json
```

These directories are:
- ✅ Never synced to cloud automatically
- ✅ Never shared unless you explicitly copy files
- ✅ Excluded from version control (`.gitignore`)
- ✅ Only readable by you (recommended: `chmod 700 local_data/`)

---

## 🔒 API Key Security

Your Anthropic API key is stored in a `.env` file that is:
- ✅ **Never committed to git** (listed in `.gitignore`)
- ✅ **Loaded only at runtime** (not printed or logged)
- ✅ **Used only for authorized API calls** (not shared or stored elsewhere)
- ✅ **Your responsibility to protect** (treat like a password)

### Best Practices for API Keys

1. **Keep it secret** - Never share your `.env` file or API key
2. **Use file permissions** - Restrict access:
   ```bash
   chmod 600 .env
   ```
3. **Rotate regularly** - If compromised, generate a new key in Anthropic Console
4. **Monitor usage** - Check your Anthropic account for unexpected API calls

---

## 🤖 AI Features & Data Transmission

When you enable AI features, **quote data is sent to Anthropic's Claude API** for processing. Here's what gets sent and when:

### Feature: Author Identification

**When triggered:** Adding a new quote without specifying an author (optional)

**Data sent to Claude:**
- The quote text (required to identify the author)

**Data sent to web search** (if enable_web_search_author is enabled):
- Quote text (to DuckDuckGo for verification if Claude's confidence is low)

**What we do:** Send quote text to Claude, which returns the author's name and confidence score. If confidence < 70%, we optionally search the web for verification.

**Retention:** Anthropic may retain API logs per their [privacy policy](https://www.anthropic.com/privacy).

---

### Feature: Category Suggestion

**When triggered:** Adding a new quote with AI enabled (optional)

**Data sent to Claude:**
- The quote text (to analyze themes)

**What we do:** Analyze the quote and suggest 2-4 categories from a predefined list.

**Retention:** Anthropic may retain API logs per their [privacy policy](https://www.anthropic.com/privacy).

---

### Feature: Duplicate Detection

**When triggered:** Adding a new quote with AI enabled (optional)

**Data sent to Claude:**
- New quote text
- Existing quote texts (for comparison)

**What we do:** Semantically compare your new quote against existing quotes to warn about duplicates.

**Retention:** Anthropic may retain API logs per their [privacy policy](https://www.anthropic.com/privacy).

---

### Feature: Quote Explanation

**When triggered:** Manually requesting an explanation when viewing a quote (optional)

**Data sent to Claude:**
- Quote text
- Author name
- Source (if provided)
- Personal notes (if provided)

**What we do:** Generate a deep, meaningful explanation of the quote's significance and application.

**Retention:** Anthropic may retain API logs per their [privacy policy](https://www.anthropic.com/privacy).

---

## 🚫 How to Avoid Sending Data to APIs

You have full control over API usage:

### Option 1: Disable AI Features by Default
Edit `local_data/personal_data/config.json`:
```json
{
  "ai": {
    "enable_author_lookup": false,
    "enable_duplicate_detection": false,
    "enable_explanations": false
  }
}
```

### Option 2: Skip AI for Single Command
```bash
quotes add --skip-ai
```

### Option 3: Unset API Key
Remove or comment out `ANTHROPIC_API_KEY` in `.env`:
```bash
# ANTHROPIC_API_KEY=sk-ant-...
```

---

## 🔐 Data Security Measures

### Input Validation & Sanitization
- ✅ All user input is sanitized to remove control characters and null bytes
- ✅ Input lengths are validated (max 10,000 chars for quotes, 500 for author, etc.)
- ✅ Special characters are properly escaped when sent to APIs
- ✅ Dangerous escape sequences are stripped from pasted content

### Prompt Injection Prevention
- ✅ User input is enclosed in triple-quote delimiters
- ✅ API responses are validated and type-checked
- ✅ Only predefined categories are accepted from API responses
- ✅ Unexpected response formats are caught and handled safely

### File Security
- ✅ Temporary files are securely created and deleted
- ✅ Quotes are stored in standard JSON format (human-readable, easy to audit)
- ✅ Recommended file permissions protect your data from other local users

---

## 📊 What Data We Collect

**On Your Local Machine:**
- Quote text, author, source, personal notes
- Categories and user selections
- AI metadata (confidence scores, suggestion dates)
- Daily quote rotation history

**From Your Machine to API:**
- Quote text and metadata (only when you enable AI features)
- Never: passwords, secrets, system information

**What We Never Do:**
- ❌ Never track you or your usage
- ❌ Never sell or share your data
- ❌ Never store credentials
- ❌ Never transmit data without your consent
- ❌ Never access files outside `local_data/`

---

## 📜 Third-Party Services

### Anthropic Claude API
- **Purpose:** AI-powered quote analysis and explanations
- **Data:** Quote text (when you enable AI features)
- **Policy:** See [Anthropic Privacy Policy](https://www.anthropic.com/privacy)
- **Required:** Anthropic API key (requires paid account)

### DuckDuckGo (Optional)
- **Purpose:** Web search for author verification (if enabled)
- **Data:** Quote text for search queries
- **Policy:** See [DuckDuckGo Privacy Policy](https://duckduckgo.com/privacy)
- **Control:** Disable with `enable_web_search_author: false` in config

---

## 🛡️ Security Best Practices

1. **Keep your `.env` file secure**
   ```bash
   chmod 600 .env
   ```

2. **Protect your `local_data/` directory**
   ```bash
   chmod 700 local_data/
   ```

3. **Don't share your data directory**
   - The entire `local_data/` folder contains all your quotes
   - Treat it like any other sensitive personal data

4. **Use strong API keys**
   - Anthropic generates keys with built-in security
   - Never hardcode keys in version control

5. **Review quote data before backup**
   - If you back up your quotes, treat backups as sensitive data
   - Encrypt backups if stored outside your machine

6. **Audit your quotes regularly**
   ```bash
   quotes list  # View all stored quotes
   ```

---

## 🔍 Transparency & Auditability

### Open Source
- All code is publicly available on GitHub
- Anyone can audit the codebase for security issues
- Security issues should be reported (not disclosed publicly) to the maintainers

### What You Can Verify
- ✅ View all Python source code in `commands/`, `ai/`, `utils/`
- ✅ Check what data is sent to APIs
- ✅ Verify SSL/TLS certificates for API calls
- ✅ Inspect your `quotes.json` file anytime

### Debug Mode
To see exactly what's being sent to APIs, search for API calls in:
- `ai/claude_client.py` - API request construction
- `ai/author_identifier.py` - Author lookup requests
- `ai/categorizer.py` - Category suggestion requests

---

## 🚨 Incident Response

If you suspect a security issue:

1. **Check your machine first**
   - Has your `.env` file been accessed?
   - Is your `local_data/` directory intact?
   - Are there unexpected files?

2. **Rotate your API key immediately**
   - Go to [Anthropic Console](https://console.anthropic.com/)
   - Generate a new API key
   - Update your `.env` file

3. **Review API usage**
   - Check Anthropic account for unexpected API calls
   - Monitor your usage and costs

4. **Report to Anthropic**
   - If you believe the API was compromised
   - Contact security@anthropic.com

---

## ❓ FAQ

**Q: Does Quotes Manager collect analytics?**
A: No. There is zero analytics, telemetry, or tracking built into Quotes Manager.

**Q: Can someone access my quotes remotely?**
A: No. Your quotes are only stored locally. You control all access.

**Q: What happens to my quotes if I stop using Quotes Manager?**
A: Your `local_data/personal_data/quotes.json` file remains yours. You can:
- Export to backup
- Import into another tool
- Delete if no longer needed

**Q: Is my API key stored securely?**
A: Your API key is stored in plain text in `.env`. It's your responsibility to:
- Keep `.env` secure with file permissions (`chmod 600`)
- Never commit `.env` to version control
- Rotate the key if compromised

**Q: Can Anthropic see my quotes when using AI features?**
A: Yes. When you use AI features, quote text is sent to Anthropic's API. See Anthropic's [privacy policy](https://www.anthropic.com/privacy) for retention details.

**Q: How is web search for authors handled?**
A: Optional. If enabled, quote text is sent to DuckDuckGo. You can disable with:
```
enable_web_search_author: false  # in config.json
```

**Q: What if I don't have an API key?**
A: All core features (save, search, view, edit) work without an API key. AI features gracefully degrade.

---

## 📝 Version History

- **v1.5.3** - Added comprehensive input validation and sanitization, improved prompt injection prevention, added privacy documentation
- **v1.5.0+** - Maintained privacy-first approach with local-only storage

---

## 📧 Questions?

For privacy questions or security concerns:
- Open an issue on GitHub (for non-sensitive issues)
- Follow responsible disclosure practices for security vulnerabilities

---

**Last Updated:** November 2024

This privacy policy is subject to change. Check back periodically for updates.
