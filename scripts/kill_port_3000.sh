#!/bin/bash

# Kill process on port 3000
echo "🔍 Checking for process on port 3000..."

PID=$(lsof -ti:3000)

if [ -z "$PID" ]; then
    echo "✅ Port 3000 is free"
else
    echo "⚠️  Found process on port 3000 (PID: $PID)"
    echo "🛑 Killing process..."
    kill -9 $PID 2>/dev/null
    sleep 1
    
    # Verify it's killed
    if lsof -ti:3000 >/dev/null 2>&1; then
        echo "❌ Failed to kill process. Try manually: kill -9 $PID"
    else
        echo "✅ Port 3000 is now free"
    fi
fi


