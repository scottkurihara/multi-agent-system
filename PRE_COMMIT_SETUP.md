# Pre-Commit Hooks Setup

This project uses pre-commit hooks to ensure code quality and consistency before commits.

## What's Configured

### General Checks
- Remove trailing whitespace
- Fix end-of-file
- Validate YAML and JSON files
- Check for large files (max 1MB)
- Detect merge conflicts
- Detect private keys

### Python (Backend)
- **Black**: Code formatting (line length: 100)
- **Ruff**: Fast Python linter (replaces flake8, isort checks)
- **isort**: Import sorting

### TypeScript/JavaScript (Frontend)
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting

### Security
- **detect-secrets**: Prevent committing secrets

## Installation

### First Time Setup

1. **Install Python dev dependencies:**
   ```bash
   cd agent-service
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

2. **Install pre-commit hooks:**
   ```bash
   cd ..  # back to project root
   pre-commit install
   ```

3. **Install frontend dependencies (if not already installed):**
   ```bash
   cd frontend-ui
   npm install
   ```

## Usage

### Automatic (Recommended)
Pre-commit hooks run automatically when you commit:
```bash
git add .
git commit -m "Your commit message"
```

If any hook fails, the commit will be blocked. Fix the issues and try again.

### Manual Run
Run all hooks on all files:
```bash
pre-commit run --all-files
```

Run specific hook:
```bash
pre-commit run black --all-files
pre-commit run prettier --all-files
```

### Skip Hooks (Use Sparingly)
If you need to skip hooks temporarily:
```bash
git commit --no-verify -m "Your commit message"
```

⚠️ **Warning**: Only use `--no-verify` in exceptional cases!

## Configuration Files

- `.pre-commit-config.yaml` - Main pre-commit configuration
- `agent-service/pyproject.toml` - Python tool configs (black, ruff, isort)
- `frontend-ui/.eslintrc.json` - ESLint configuration
- `frontend-ui/.prettierrc` - Prettier configuration
- `.secrets.baseline` - Baseline for secret detection

## Common Issues

### Hook Fails with "File Modified"
Some hooks auto-fix issues (black, prettier, ruff). After they modify files:
1. Review the changes: `git diff`
2. Stage the fixes: `git add .`
3. Commit again: `git commit -m "Your message"`

### ESLint/Prettier Not Found
Make sure frontend dependencies are installed:
```bash
cd frontend-ui
npm install
```

### Python Tools Not Found
Make sure you've installed dev dependencies:
```bash
cd agent-service
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Updating Hooks

Update to latest versions:
```bash
pre-commit autoupdate
```

## Benefits

✅ Consistent code style across the team
✅ Catch issues before CI/CD
✅ Automatic formatting saves time
✅ Prevent secrets from being committed
✅ Reduce code review comments on style
