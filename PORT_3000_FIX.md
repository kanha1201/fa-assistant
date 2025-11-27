# Fix Port 3000 Issue

Port 3000 is currently in use by another process. To use it for Tensor frontend:

## Option 1: Kill the existing process (Recommended)

Run this script to free up port 3000:
```bash
./scripts/kill_port_3000.sh
```

Or manually:
```bash
# Find the process
lsof -ti:3000

# Kill it
kill -9 $(lsof -ti:3000)
```

Then start the frontend:
```bash
cd frontend
npm install
npm run dev
```

## Option 2: Use a different port

If you want to keep the other project running, the frontend is configured to use port 3000, but you can change it in `frontend/vite.config.js`:

```js
server: {
  port: 3001,  // Change to any available port
}
```

## Verify

After freeing port 3000, start the frontend:
```bash
cd frontend
npm run dev
```

The Tensor frontend should now be available at: http://localhost:3000
