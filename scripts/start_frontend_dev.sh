#!/bin/bash

# Start Frontend Development Server
echo "🎨 Starting Tensor Frontend Development Server..."
echo ""

cd "$(dirname "$0")/../frontend"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Are you in the correct directory?"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📥 Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
fi

# Check if port 3001 is available
if lsof -ti:3001 >/dev/null 2>&1; then
    echo "⚠️  Port 3001 is already in use"
    echo "   Killing existing process..."
    kill -9 $(lsof -ti:3001) 2>/dev/null
    sleep 1
fi

echo "🚀 Starting Vite dev server..."
echo "🌐 Frontend will be available at: http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev


