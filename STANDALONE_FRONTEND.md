# Standalone Frontend - No Node.js Required! ✅

## Overview

Created a **standalone HTML file** that works without Node.js, npm, or any build process. Just open it in your browser!

## File Location

**`frontend/standalone.html`**

## How to Use

### Step 1: Start the Backend API

```bash
python scripts/run_api.py
```

The backend should be running on `http://localhost:8000`

### Step 2: Open the HTML File

Simply open `frontend/standalone.html` in your web browser:

**Option 1: Double-click**
- Navigate to `frontend/standalone.html`
- Double-click to open in your default browser

**Option 2: Drag and Drop**
- Drag `frontend/standalone.html` into your browser window

**Option 3: Open from Browser**
- Open your browser
- Press `Cmd+O` (Mac) or `Ctrl+O` (Windows/Linux)
- Select `frontend/standalone.html`

**Option 4: From Terminal**
```bash
# macOS
open frontend/standalone.html

# Linux
xdg-open frontend/standalone.html

# Windows
start frontend/standalone.html
```

## Features

✅ **All Features Included:**
- Dark mode financial terminal design
- Header with Tensor logo
- Welcome state
- Chat interface
- Quick action chips (Summarise, Red Flags, Bull/Bear)
- Input field with send button
- Full API integration

✅ **No Dependencies Required:**
- Uses CDN links for React, Tailwind CSS, Axios
- No npm install needed
- No build process needed
- Works offline (except API calls)

## Technical Details

### CDN Dependencies Used:
- **React 18** - from unpkg.com
- **ReactDOM 18** - from unpkg.com
- **Babel Standalone** - for JSX transformation
- **Tailwind CSS** - from cdn.tailwindcss.com
- **Axios** - from cdn.jsdelivr.net

### API Configuration:
- Backend URL: `http://localhost:8000`
- All endpoints work the same as the React version

## Troubleshooting

### CORS Errors
If you see CORS errors, make sure:
1. Backend is running on port 8000
2. Backend has CORS enabled (already configured)

### API Connection Issues
1. Check backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Open browser console (F12) to see error messages

### File Not Opening
- Make sure you're opening `standalone.html` (not a folder)
- Try a different browser
- Check file permissions

## Advantages

✅ **No Installation Required**
- No Node.js needed
- No npm needed
- No build process

✅ **Portable**
- Single HTML file
- Can be shared easily
- Works on any device with a browser

✅ **Fast**
- No compilation needed
- Instant loading
- CDN resources cached by browser

## Limitations

⚠️ **Requires Internet Connection**
- CDN resources need internet
- API calls need backend running

⚠️ **Browser Compatibility**
- Modern browsers only (Chrome, Firefox, Safari, Edge)
- IE11 not supported

## Next Steps

1. Start backend: `python scripts/run_api.py`
2. Open `frontend/standalone.html` in browser
3. Start chatting with Tensor!

The frontend will be fully functional and connect to your backend API.


