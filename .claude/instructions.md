# Project Instructions for Claude

## Git Workflow - CRITICAL
- **ALWAYS commit changes immediately** - Do NOT ask for permission
- Commit after completing each feature, fix, or logical unit of work
- Use descriptive commit messages following conventional commits format
- Always include these lines at the end of commit messages:
  ```
  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
  ```
- Use `--no-verify` flag if pre-commit hooks fail on style issues
- Create commits even for small changes - commit early, commit often

## Project Context
This is an AI-powered to-do app built with:
- **Backend**: FastAPI + LangGraph + PostgreSQL
- **Frontend**: Next.js + React + TypeScript (to be built)
- **Architecture**: Tool-calling pattern - supervisor agent calls specialized tools

## Implementation Phases
- ✅ **Phase 1**: Database, CRUD API, and tests (COMPLETE)
- 🔄 **Phase 2**: AI agent tools (breakdown, prioritize, schedule, guidance)
- 📋 **Phase 3**: Frontend hybrid UI (chat + list view)
- 📋 **Phase 4**: Advanced features (API integrations, recurring tasks)
- 📋 **Phase 5**: Polish and production deployment

## Key Architectural Decisions
1. **Tool-calling over separate nodes**: Agents are tools called by supervisor, not separate graph nodes
2. **Dual-state system**: Internal ToDos (agent planning) vs UserTodos (database)
3. **Simplified graph**: Only supervisor → finalizer nodes
4. **Supervisor has full control**: Can call multiple tools per request

## Code Style
- Use async/await throughout
- Type hints on all functions
- Comprehensive docstrings
- Follow existing patterns in codebase
- Pre-commit hooks: black, ruff, isort (can bypass if needed)

## Testing
- Write tests for all new features
- Use pytest with async support
- Mock external dependencies
- In-memory SQLite for service tests
- Mock service layer for API tests

## Plan File Location
Implementation plans are tracked in: `/Users/scottkurihara/.claude/plans/playful-booping-melody.md`

## Common Commands
```bash
# Run tests
cd agent-service && uv run pytest

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f agent-service

# Stop services
docker-compose down
```

## Notes
- No emojis in code/commits unless explicitly requested
- Keep responses concise and technical
- Reference file paths with line numbers when relevant (e.g., `file.py:123`)
