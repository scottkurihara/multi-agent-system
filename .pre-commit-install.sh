#!/bin/bash
# Pre-commit installation script

set -e

echo "🔧 Installing pre-commit hooks..."

# Install Python dev dependencies
echo "📦 Installing Python dev dependencies..."
cd agent-service
source .venv/bin/activate
uv pip install -e ".[dev]"
cd ..

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install

# Install frontend dependencies if needed
if [ ! -d "frontend-ui/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend-ui
    npm install
    cd ..
fi

echo "✅ Pre-commit hooks installed successfully!"
echo ""
echo "To test the hooks, run: pre-commit run --all-files"
