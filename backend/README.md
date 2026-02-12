# AI Architecture Assistant - Backend

FastAPI backend for generating Technical Architecture Documents using Azure OpenAI and Azure AI Search.

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env and add your Azure API keys
```

3. **Run the development server:**
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### POST /api/qualify
Analyze and qualify requirements using GPT-4.

**Request:**
```json
{
  "requirements": "string with FR/NFR"
}
```

**Response:**
```json
{
  "qualification": {
    "completeness": {"score": 0-100, "issues": []},
    "clarity": {"score": 0-100, "issues": []},
    "feasibility": {"score": 0-100, "issues": []},
    "consistency": {"score": 0-100, "issues": []},
    "overall_gap": 0-100,
    "recommendations": []
  },
  "gap": 0-100
}
```

### POST /api/validate
Validate qualification data (checks if GAB = 0).

**Request:**
```json
{
  "qualification": {...}
}
```

**Response:**
```json
{
  "valid": true/false,
  "gap": 0-100
}
```

### POST /api/generate-tad
Generate Technical Architecture Document using RAG.

**Request:**
```json
{
  "requirements": {...}
}
```

**Response:**
```json
{
  "tad_markdown": "# Technical Architecture Document\n..."
}
```

## Docker

Build and run with Docker:

```bash
docker build -t aia-backend .
docker run -p 8000:8000 --env-file .env aia-backend
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── qualify.py          # /api/qualify endpoint
│   │   ├── validate.py         # /api/validate endpoint
│   │   └── generate_tad.py     # /api/generate-tad endpoint
│   └── services/
│       ├── __init__.py
│       ├── openai_service.py   # Azure OpenAI wrapper
│       └── search_service.py   # Azure AI Search wrapper
├── main.py                     # Entry point
├── requirements.txt
├── Dockerfile
└── .env.example
```
