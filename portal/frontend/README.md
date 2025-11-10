# DigitalGrub Portal - Frontend

React + TypeScript + Ant Design frontend for the DigitalGrub Content Management Portal.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Run development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

## Features

- **Dashboard**: View indexing statistics and overall progress
- **Content Generator**: 
  - Generate blog titles using AI
  - Create blog content with AI assistance
  - Edit content with Monaco Editor
  - Preview and save blogs

## Tech Stack

- React 18.3+
- TypeScript 5.6+
- Vite 6.0+
- Ant Design 5.21+
- TanStack Query (React Query) v5
- Axios for API calls
- Monaco Editor for code/markdown editing
- React Router for navigation

## Available Scripts

- `npm run dev` - Start development server (http://localhost:5173)
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## API Configuration

The frontend proxies API requests to the backend:
- Development: http://localhost:8000
- Configure in `vite.config.ts`
