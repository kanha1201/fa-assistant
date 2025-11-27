# Node.js Installation Required

The frontend requires Node.js and npm to run. They are not currently installed or not in your PATH.

## Install Node.js

### Option 1: Using Homebrew (macOS)
```bash
brew install node
```

### Option 2: Download from Official Website
1. Visit: https://nodejs.org/
2. Download the LTS version for macOS
3. Run the installer
4. Restart your terminal

### Option 3: Using nvm (Node Version Manager)
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Restart terminal or run:
source ~/.zshrc

# Install Node.js
nvm install --lts
nvm use --lts
```

## Verify Installation

After installing, verify:
```bash
node --version
npm --version
```

## Then Install Frontend Dependencies

Once Node.js is installed:
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at: http://localhost:3001
