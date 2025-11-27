#!/bin/bash

# Start Frontend Only
echo "🎨 Starting Tensor Frontend..."
echo ""

cd "$(dirname "$0")/../frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📥 Installing dependencies..."
    npm install
fi

echo "🚀 Starting Vite dev server on port 3001..."
echo "🌐 Frontend will be available at: http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop"

npm run dev


