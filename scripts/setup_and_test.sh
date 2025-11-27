#!/bin/bash
# Setup and test script for backend

set -e

echo "🚀 Setting up backend environment..."
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Verify installation
echo ""
echo "Verifying installation..."
python3 -c "import google.generativeai, fastapi, chromadb, sqlalchemy; print('✓ Core dependencies installed')"

# Setup database
echo ""
echo "Setting up database..."
python3 scripts/setup_database.py || echo "⚠ Database setup skipped (optional)"

# Run data ingestion
echo ""
echo "Running data ingestion..."
python3 scripts/ingest.py

# Test backend
echo ""
echo "Testing backend..."
python3 scripts/test_backend.py

echo ""
echo "✅ Setup complete!"


