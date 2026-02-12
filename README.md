# AI Architecture Assistant (AIA)

Generate comprehensive Technical Architecture Documents (TAD) automatically using AI-powered analysis and Retrieval-Augmented Generation (RAG).

## 🎯 Overview

The AI Architecture Assistant is a full-stack application that helps architects and technical leads create professional Technical Architecture Documents by:

1. **Analyzing Requirements**: Uses Azure OpenAI GPT-4 to qualify functional and non-functional requirements
2. **Gap Analysis**: Calculates a Gap Analysis Score (GAB) to ensure requirements completeness
3. **RAG-Enhanced Generation**: Leverages Azure AI Search with hybrid search (text + vector) to retrieve relevant architectural patterns and best practices
4. **TAD Generation**: Produces comprehensive, production-ready Technical Architecture Documents in Markdown format

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + TS)                    │
│                    Port: 5173 (Vite Dev)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST
┌──────────────────────────▼──────────────────────────────────┐
│                  Backend (FastAPI + Python)                  │
│                        Port: 8000                            │
└──────┬─────────────────────────────────────────────┬────────┘
       │                                             │
       │ Azure OpenAI API                            │ Azure AI Search API
       │                                             │
┌──────▼────────────────────┐           ┌───────────▼─────────┐
│   Azure OpenAI Service    │           │ Azure AI Search     │
│   - GPT-4 (Analysis)      │           │ - Vector Search     │
│   - GPT-4 (TAD Gen)       │           │ - Hybrid Search     │
│   - text-embedding-ada-002│           │ - RAG Knowledge Base│
└───────────────────────────┘           └─────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Azure OpenAI** account with GPT-4 and text-embedding-ada-002 deployments
- **Azure AI Search** instance with a configured index

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/aia-assistant.git
cd aia-assistant
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env and add your Azure API keys
```

**Required Environment Variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | `https://ahaaoai01.openai.azure.com` |
| `AZURE_OPENAI_KEY` | Azure OpenAI API key | `your-api-key-here` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | GPT-4 deployment name | `gpt-4` |
| `AZURE_EMBEDDING_DEPLOYMENT_NAME` | Embedding model deployment | `text-embedding-ada-002` |
| `AZURE_SEARCH_ENDPOINT` | Azure AI Search endpoint | `https://ahaais01.search.windows.net` |
| `AZURE_SEARCH_KEY` | Azure AI Search API key | `your-search-key-here` |
| `AZURE_SEARCH_INDEX_NAME` | Search index name | `tad-knowledge-base` |

### 3. Run with Docker Compose (Recommended)

```bash
docker-compose up --build
```

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Run Locally (Development)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your Azure API keys to .env
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## 📚 API Documentation

### Endpoints

#### 1. POST `/api/qualify`
Analyze and qualify requirements using GPT-4.

**Request:**
```json
{
  "requirements": "User authentication with OAuth2\nReal-time data sync\nSupport 10k concurrent users"
}
```

**Response:**
```json
{
  "qualification": {
    "completeness": {"score": 25, "issues": ["Missing security requirements"]},
    "clarity": {"score": 10, "issues": []},
    "feasibility": {"score": 15, "issues": ["Scalability needs more detail"]},
    "consistency": {"score": 0, "issues": []},
    "overall_gap": 12.5,
    "recommendations": ["Add detailed security requirements", "Specify scalability metrics"]
  },
  "gap": 12.5
}
```

#### 2. POST `/api/validate`
Validate if requirements are complete (GAB = 0).

**Request:**
```json
{
  "qualification": { /* qualification object */ }
}
```

**Response:**
```json
{
  "valid": false,
  "gap": 12.5
}
```

#### 3. POST `/api/generate-tad`
Generate Technical Architecture Document using RAG.

**Request:**
```json
{
  "requirements": {
    "original_requirements": "...",
    "qualification": { /* qualification object */ }
  }
}
```

**Response:**
```json
{
  "tad_markdown": "# Technical Architecture Document\n\n## 1. Executive Summary\n..."
}
```

## 🔄 Workflow

1. **Enter Requirements** → User inputs functional and non-functional requirements
2. **Qualify** → GPT-4 analyzes requirements and calculates GAB score
3. **Review** → User reviews qualification results and recommendations
4. **Generate TAD** (if GAB = 0) → System uses RAG to generate comprehensive TAD
5. **Download** → User downloads TAD as Markdown or PDF

## 🛠️ Technology Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **react-markdown** - Markdown rendering
- **lucide-react** - Icons
- **html2pdf.js** - PDF generation

### Backend
- **FastAPI** - Modern Python web framework
- **Python 3.11** - Programming language
- **Azure OpenAI** - GPT-4 for analysis and generation
- **Azure AI Search** - RAG knowledge base with hybrid search
- **Pydantic** - Data validation
- **python-dotenv** - Environment management

## 📁 Project Structure

```
aia-assistant/
├── frontend/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API service layer
│   │   ├── types/           # TypeScript types
│   │   ├── App.tsx          # Main app component
│   │   └── main.tsx         # Entry point
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Azure service wrappers
│   │   ├── models/          # Pydantic schemas
│   │   ├── prompts/         # Prompt templates
│   │   └── main.py          # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml        # Docker orchestration
├── .env.example             # Environment template
└── README.md                # This file
```

## 🔐 Security Notes

- Never commit `.env` files with real API keys
- Use environment variables for all sensitive data
- Azure API keys should be rotated regularly
- Consider using Azure Key Vault for production deployments

## 🧪 Testing

**Backend:**
```bash
cd backend
pytest
```

**Frontend:**
```bash
cd frontend
npm test
```

## 📝 Logging

The backend uses Python's logging module with both console and file output:
- **Console**: Real-time logs during development
- **File**: `backend/app.log` for persistent logging

Log levels:
- `INFO`: General application flow
- `DEBUG`: Detailed diagnostic information
- `ERROR`: Error events with stack traces

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Azure OpenAI for GPT-4 and embedding models
- Azure AI Search for RAG capabilities
- FastAPI and React communities

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review logs in `backend/app.log`
