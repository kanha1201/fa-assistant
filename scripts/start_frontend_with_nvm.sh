#!/bin/bash

# Start Frontend with nvm support
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

cd "$(dirname "$0")/../frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📥 Installing dependencies..."
    npm install
fi

echo "🚀 Starting Vite dev server..."
echo "🌐 Frontend will be available at: http://localhost:3001"
echo ""

npm run dev


