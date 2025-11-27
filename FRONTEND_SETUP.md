# Frontend Setup Guide

## Prerequisites

- Node.js 16+ and npm installed
- Backend API running on port 8000

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (optional, defaults to localhost:8000):
```bash
echo "VITE_API_URL=http://localhost:8000" > .env
```

## Running the Frontend

### Development Mode
```bash
npm run dev
```

The app will be available at `http://localhost:3001`

### Production Build
```bash
npm run build
npm run preview
```

## Features Implemented

✅ **Header Component**
- Back arrow navigation
- Tensor logo with AI icon
- Menu button

✅ **Chat Area**
- Welcome state with logo and message
- Message bubbles (user/assistant)
- Auto-scroll to latest message
- Loading indicator

✅ **Quick Action Chips**
- Summarise button
- Red Flags button (with red icon)
- Bull/Bear button
- Horizontal scroll support

✅ **Input Field**
- Text input with placeholder
- Send button (mint green)
- Enter key support
- Disabled state during loading

✅ **API Integration**
- Summary endpoint
- Red Flags endpoint
- Bull/Bear endpoint
- Chat query endpoint

✅ **Styling**
- Dark mode theme (#121212 background)
- Groww-inspired colors
- Mobile-first design (375px-400px)
- Smooth animations
- Custom scrollbar

## Color Palette

- Background: `#121212` (groww-black)
- Surface: `#1E1E1E` (groww-surface)
- Border: `#2C2C2E` (groww-border)
- Primary: `#00D09C` (groww-mint)
- Warning: `#EB5B3C` (groww-coral)
- Text: `#FFFFFF` (groww-white)
- Secondary Text: `#9CA3AF` (groww-gray)

## Component Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx          # Top navigation bar
│   │   ├── ChatArea.jsx        # Main chat display area
│   │   ├── MessageBubble.jsx   # Individual message component
│   │   ├── QuickActionChips.jsx # Quick action buttons
│   │   └── InputField.jsx      # Text input and send button
│   ├── services/
│   │   └── api.js              # API service layer
│   ├── App.jsx                 # Main app component
│   ├── main.jsx                # Entry point
│   └── index.css               # Global styles
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## API Endpoints Used

- `GET /summary?company_symbol=ETERNAL` - Get fundamentals summary
- `GET /red-flags?company_symbol=ETERNAL` - Get red flags
- `GET /bull-bear?company_symbol=ETERNAL` - Get bull/bear case
- `GET /chat/query?company_symbol=ETERNAL&query=...` - Answer user query

## Troubleshooting

### CORS Issues
If you see CORS errors, make sure:
1. Backend has CORS middleware enabled
2. Backend is running on port 8000
3. Frontend API URL matches backend URL

### API Connection Issues
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify API URL in `.env` file
3. Check browser console for errors

### Build Issues
1. Clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

2. Clear Vite cache:
```bash
rm -rf node_modules/.vite
```

## Next Steps

1. Start backend API: `python scripts/run_api.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser: `http://localhost:3001`
4. Test quick actions and chat functionality

