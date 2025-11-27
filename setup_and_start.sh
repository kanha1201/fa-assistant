#!/bin/bash

# Complete setup and start script for Tensor Frontend

echo "🚀 Tensor Frontend Setup & Start"
echo "=================================="
echo ""

# Load nvm if it exists
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    . "$NVM_DIR/nvm.sh"
    echo "✅ nvm loaded"
fi

# Check if Node.js is available
if ! command -v node >/dev/null 2>&1; then
    echo "❌ Node.js not found"
    
    # Try to install via nvm
    if [ -s "$NVM_DIR/nvm.sh" ]; then
        echo "📦 Installing Node.js via nvm..."
        . "$NVM_DIR/nvm.sh"
        nvm install --lts
        nvm use --lts
        nvm alias default node
    else
        echo "❌ nvm not found. Please install Node.js manually:"
        echo "   1. Visit https://nodejs.org/ and download LTS version"
        echo "   2. Or install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo "   3. Then: brew install node"
        exit 1
    fi
fi

# Verify Node.js
if command -v node >/dev/null 2>&1; then
    echo "✅ Node.js $(node --version) found"
    echo "✅ npm $(npm --version) found"
else
    echo "❌ Node.js still not available after installation"
    exit 1
fi

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo ""
    echo "📥 Installing frontend dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Check if port 3001 is available
if lsof -ti:3001 >/dev/null 2>&1; then
    echo ""
    echo "⚠️  Port 3001 is in use. Killing existing process..."
    kill -9 $(lsof -ti:3001) 2>/dev/null
    sleep 1
fi

# Start the dev server
echo ""
echo "🚀 Starting Vite dev server..."
echo "🌐 Frontend will be available at: http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev


