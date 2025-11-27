#!/bin/bash
# Node.js Installation Guide Script

echo "🔍 Checking for Node.js installation methods..."

# Check for Homebrew
if command -v brew >/dev/null 2>&1; then
    echo "✅ Homebrew found"
    echo "📦 Installing Node.js via Homebrew..."
    brew install node
    if [ $? -eq 0 ]; then
        echo "✅ Node.js installed successfully!"
        node --version
        npm --version
        exit 0
    fi
fi

# Check for nvm
if [ -s "$HOME/.nvm/nvm.sh" ]; then
    echo "✅ nvm found"
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    echo "📦 Installing Node.js via nvm..."
    nvm install --lts
    nvm use --lts
    if command -v node >/dev/null 2>&1; then
        echo "✅ Node.js installed successfully!"
        node --version
        npm --version
        exit 0
    fi
fi

echo "❌ Could not install Node.js automatically"
echo ""
echo "Please install Node.js manually:"
echo "1. Visit https://nodejs.org/ and download the LTS version"
echo "2. Or install Homebrew first: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
echo "   Then run: brew install node"
