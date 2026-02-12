# AI Architecture Assistant - Frontend

React + TypeScript frontend for the AI Architecture Assistant application.

## Features

- **Modern UI**: Built with React, TypeScript, and Tailwind CSS
- **Responsive Design**: Mobile-friendly interface
- **Multi-step Workflow**:
  1. Enter requirements (FR/NFR)
  2. View qualification analysis with GAB score
  3. Generate and download Technical Architecture Document

## Setup

1. **Install dependencies:**
```bash
npm install
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env if your backend runs on a different URL
```

3. **Run development server:**
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── InputForm.tsx          # Step 1: Requirements input
│   │   ├── QualificationView.tsx  # Step 2: Qualification results
│   │   └── TADViewer.tsx          # Step 3: TAD display & download
│   ├── services/
│   │   └── api.ts                 # API service layer
│   ├── types/
│   │   └── index.ts               # TypeScript type definitions
│   ├── App.tsx                    # Main application with workflow
│   ├── main.tsx                   # Entry point
│   ├── index.css                  # Tailwind CSS
│   └── vite-env.d.ts              # Vite environment types
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Workflow

### Step 1: Enter Requirements
- User enters functional and non-functional requirements
- Click "Qualify Requirements" button

### Step 2: View Qualification
- Display detailed analysis:
  - Completeness score
  - Clarity score
  - Feasibility score
  - Consistency score
- Show GAB (Gap Analysis Score)
- If GAB = 0: Show "Generate TAD" button
- If GAB > 0: Show warnings and recommendations

### Step 3: View & Download TAD
- Display generated TAD in markdown format
- Download options:
  - `.md` - Markdown file
  - `.pdf` - PDF document

## Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **react-markdown** - Markdown rendering
- **lucide-react** - Icons
- **html2pdf.js** - PDF generation

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`:

- `POST /api/qualify` - Qualify requirements
- `POST /api/validate` - Validate qualification
- `POST /api/generate-tad` - Generate TAD

## Environment Variables

- `VITE_API_URL` - Backend API URL (default: `http://localhost:8000`)
