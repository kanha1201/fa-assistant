# Starting the Frontend

## Quick Start

Run the setup script from the project root:

```bash
./setup_and_start.sh
```

This script will:
1. ✅ Check/install Node.js via nvm
2. ✅ Install frontend dependencies
3. ✅ Start the dev server on port 3001

## Manual Start (if Node.js is already installed)

```bash
# Load nvm (if using nvm)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

## Troubleshooting

If you see "command not found: node":
1. Make sure nvm is loaded: `source ~/.nvm/nvm.sh`
2. Or restart your terminal
3. Or install Node.js from https://nodejs.org/

The frontend will be available at: **http://localhost:3001**
