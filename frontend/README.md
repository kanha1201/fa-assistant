# Tensor Chatbot UI

Mobile-first React UI for the Tensor AI Financial Assistant chatbot.

## Features

- 🎨 Dark mode financial terminal design
- 📱 Mobile-optimized (375px-400px width)
- ⚡ Fast and responsive
- 🎯 Quick action chips (Summarise, Red Flags, Bull/Bear)
- 💬 Real-time chat interface

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

## Environment Variables

Create a `.env` file in the frontend directory:

```
VITE_API_URL=http://localhost:8000
```

## Backend Integration

Make sure the backend API is running on port 8000 (or update the API URL in `.env`).

The frontend expects the following endpoints:
- `GET /summary?company_symbol=ETERNAL`
- `GET /red-flags?company_symbol=ETERNAL`
- `GET /bull-bear?company_symbol=ETERNAL`
- `GET /chat/query?company_symbol=ETERNAL&query=...`

## Tech Stack

- React 18
- Vite
- Tailwind CSS
- Lucide React (icons)
- Axios (HTTP client)


