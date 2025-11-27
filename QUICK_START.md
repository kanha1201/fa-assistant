# Quick Start Guide

## Start Frontend (Port 3001)

### Option 1: Using the script (Recommended)
```bash
./scripts/start_frontend_dev.sh
```

### Option 2: Manual start
```bash
cd frontend
npm install
npm run dev
```

Then open: **http://localhost:3001**

## Start Backend (Port 8000)

```bash
python scripts/run_api.py
```

## Troubleshooting

### Connection Refused Error
1. Make sure the dev server is running:
   ```bash
   cd frontend
   npm run dev
   ```

2. Check if port 3001 is in use:
   ```bash
   lsof -ti:3001
   ```

3. Install dependencies if needed:
   ```bash
   cd frontend
   npm install
   ```

### Module Not Found Errors
Clear cache and reinstall:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Backend Not Responding
Make sure backend is running:
```bash
python scripts/run_api.py
```

Test backend:
```bash
curl http://localhost:8000/health
```
