# Development Workflow

## Git Workflow

### Branch Strategy

**Always use feature branches** - Never commit directly to `main`

1. **Create a feature branch** for each new feature or bug fix
   ```bash
   git checkout -b feature/feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make changes and commit** with detailed commit messages
   ```bash
   git add -A
   git commit -m "Detailed commit message"
   ```

3. **Push feature branch**
   ```bash
   git push origin feature/feature-name
   ```

4. **Create Pull Request** for review
   ```bash
   gh pr create --title "Feature: Description" --body "Detailed description"
   ```

5. **Merge to main** after approval
   ```bash
   git checkout main
   git merge feature/feature-name
   git push origin main
   ```

6. **Delete feature branch** after merge
   ```bash
   git branch -d feature/feature-name
   git push origin --delete feature/feature-name
   ```

### Commit Message Format

```
<Type>: <Short description>

<Detailed description of changes>

**Changes:**
- Bullet point 1
- Bullet point 2

**Test Results:**
- Test summary

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Commit Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### Pull Request Guidelines

1. **Every change requires a PR** - No direct commits to main
2. **Include tests** - All new features must have tests
3. **Update documentation** - Keep docs in sync with code
4. **Run pre-commit hooks** - Ensure code quality before pushing
5. **Descriptive PR titles** - Clearly state what the PR does

### Pre-commit Hooks

Pre-commit hooks run automatically on every commit:
- **black** - Python code formatting
- **ruff** - Python linting
- **isort** - Import sorting
- **eslint** - JavaScript/TypeScript linting
- **prettier** - JavaScript/TypeScript formatting
- **detect-secrets** - Security scanning

To manually run hooks:
```bash
pre-commit run --all-files
```

## Testing

### Backend Tests

```bash
cd agent-service
source .venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/test_logging.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run unit tests only (skip integration)
pytest tests/test_logging.py tests/test_agents.py tests/test_api.py tests/test_ui_tools.py
```

### Frontend Tests

```bash
cd frontend-ui

# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage
```

### Test Requirements

- **New features** - Must include unit tests
- **Bug fixes** - Must include regression tests
- **Generative UI** - Must test component rendering and interactions
- **Minimum coverage** - Aim for 80%+ on new code

## Running the Application

### Backend

```bash
cd agent-service
source .venv/bin/activate

# Default (INFO logging)
python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8080

# Debug logging
LOG_LEVEL=DEBUG python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8080

# With file logging
LOG_LEVEL=INFO LOG_FILE=agent.log python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8080
```

### Frontend

```bash
cd frontend-ui
npm run dev
```

Access at http://localhost:3000

## Debugging

### Logging Levels

Set via `LOG_LEVEL` environment variable:
- **DEBUG** - Detailed diagnostic information
- **INFO** - General informational messages (default)
- **WARNING** - Warning messages
- **ERROR** - Error messages
- **CRITICAL** - Critical errors

See [LOGGING.md](LOGGING.md) for detailed logging documentation.

### Common Debug Commands

```bash
# View backend logs
tail -f /tmp/claude/-Users-scottkurihara-Projects-agent/tasks/[task-id].output

# Filter logs by component
grep "src.nodes.supervisor" agent.log

# Find errors
grep -E "ERROR|WARNING" agent.log

# Check server health
curl http://localhost:8080/health
```

## Code Quality

### Before Committing

1. **Run tests** - Ensure all tests pass
   ```bash
   pytest
   ```

2. **Check formatting** - Pre-commit hooks run automatically
   ```bash
   pre-commit run --all-files
   ```

3. **Review changes**
   ```bash
   git diff
   ```

### Code Style Guidelines

**Python:**
- Line length: 100 characters
- Follow PEP 8
- Type hints encouraged
- Docstrings for public functions

**TypeScript:**
- Follow Next.js conventions
- Use TypeScript strict mode
- Functional components preferred
- Props interfaces for components

## Dependencies

### Adding Backend Dependencies

```bash
cd agent-service
source .venv/bin/activate
uv pip install package-name
uv pip freeze > requirements.txt  # If using pip
```

### Adding Frontend Dependencies

```bash
cd frontend-ui
npm install package-name
```

## Troubleshooting

### Backend Issues

**Import errors:**
```bash
cd agent-service
source .venv/bin/activate
```

**Port already in use:**
```bash
pkill -f "uvicorn src.api.server"
```

### Frontend Issues

**Module not found:**
```bash
cd frontend-ui
rm -rf node_modules
npm install
```

**Port already in use:**
```bash
pkill -f "next dev"
```

### Test Issues

**Async warnings:**
```bash
uv pip install pytest-asyncio
```

**Jest configuration:**
- Check jest.config.js
- Verify jest.setup.js exists

## CI/CD

### GitHub Actions (Planned)

Future CI/CD pipeline will:
- Run tests on every PR
- Enforce code quality checks
- Run integration tests
- Deploy on merge to main

## Resources

- [LOGGING.md](LOGGING.md) - Logging documentation
- [tests/README.md](tests/README.md) - Testing guide
- [PRE_COMMIT_SETUP.md](PRE_COMMIT_SETUP.md) - Pre-commit hooks guide
- [frontend-ui/__tests__/README.md](../frontend-ui/__tests__/README.md) - Frontend testing

## Questions?

For questions or issues:
1. Check existing documentation
2. Review recent PRs for examples
3. Ask in PR comments
