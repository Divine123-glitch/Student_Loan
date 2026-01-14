# NELFUND Navigator - AI Student Loan Assistant

An intelligent AI assistant that helps Nigerian students navigate NELFUND (Nigerian Education Loan Fund) with confidence. Built with Agentic RAG, FastAPI, and React.

## Features

### Authentication System
- User registration and login with JWT tokens
- Secure password hashing with bcrypt
- Protected routes and session management
- User data stored in ChromaDB vector database

### Intelligent Chat Interface
- **Claude AI-inspired design** with dark/light mode toggle
- Real-time chat with typing indicators
- Conversation history and session management
- Source citations for every answer
- Mobile-responsive design

### Agentic RAG System
- **Conditional retrieval** - Doesn't retrieve documents for greetings
- **Conversation memory** - Handles follow-up questions intelligently
- **Source citation** - Every answer includes document sources
- **LangGraph workflow** - Sophisticated agent decision-making
- Built with LangChain and OpenAI GPT-4

### Interactive Homepage
- Modern, engaging landing page
- Feature showcase with animations
- Direct links to official NELFUND website
- Call-to-action sections
- Statistics and testimonials

### Data Persistence
- ChromaDB for vector storage and user management
- Chat history saved per user
- Session-based conversations
- Document embeddings for semantic search

---

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **LangChain** - LLM orchestration framework
- **LangGraph** - Agent workflow management
- **ChromaDB** - Vector database for documents and users
- **OpenAI GPT-4** - Language model
- **JWT** - Authentication tokens
- **Bcrypt** - Password hashing

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Icon library

---

## Project Structure

```
nelfund-navigator/
│
├── backend/
│   ├── main.py                 # FastAPI app with auth & chat endpoints
│   ├── rag_engine.py           # LangGraph Agentic RAG system
│   ├── document_processor.py   # PDF loading and chunking
│   ├── vector_store.py         # ChromaDB vector database manager
│   ├── setup_vectordb.py       # One-time setup script
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables
│   ├── chroma_db/             # Document vector database (auto-created)
│   ├── chroma_users/          # User data storage (auto-created)
│   └── data/
│       └── documents/         # NELFUND PDF documents (add here)
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx           # React entry point
│   │   ├── App.jsx            # Main router component
│   │   ├── index.css          # Global styles
│   │   └── components/
│   │       ├── HomePage.jsx           # Landing page
│   │       ├── AuthPages.jsx          # Login & Register
│   │       └── ChatInterface.jsx      # Main chat UI
│   │
│   ├── index.html             # HTML template
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite configuration
│   ├── tailwind.config.js     # Tailwind configuration
│   └── postcss.config.js      # PostCSS configuration
│
├── README.md                  # This file
├── DEMO.md                    # Demo video and screenshots
└── .gitignore
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- OpenAI API key

### Step 1: Clone the Repository

```bash
git clone https://github.com/Divine123-glitch/Student_Loan.git
cd nelfund-navigator
```

### Step 2: Backend Setup
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Frontend Setup
# Navigate to frontend (from project root)
cd frontend

# Install dependencies
npm install
```

---

## Configuration

### Backend Configuration

1. Create `.env` file in `backend/` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_super_secret_jwt_key_change_in_production
DATABASE_URL=./chroma_users
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

2. Add NELFUND documents:
   - Create `backend/data/` folder if it doesn't exist
   - Place PDF documents in `backend/data/`
   - Run setup: `python setup_vectordb.py`

3. The setup script will:
   - Load all PDFs from `data/` folder
   - Chunk them into optimal sizes
   - Create embeddings using OpenAI
   - Save to `chroma_db/` directory

### Frontend Configuration

The frontend is pre-configured to connect to `http://localhost:8000` for the backend API.

---

## Running the Application

### First Time Setup (Backend)

**IMPORTANT: Run this once to create your vector database:**
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Make sure you have PDFs in ./data folder
# Then run the setup script:
python setup_vectordb.py


This will:
1. Load all NELFUND PDFs
2. Chunk them into optimal sizes
3. Create embeddings using OpenAI
4. Save the vector database to `./chroma_db`

### Option 1: Run Backend and Frontend Separately

**Terminal 1 - Backend:**
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload --host 0.0.0.0 --port 8000


**Terminal 2 - Frontend:**
cd frontend
npm run dev


The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Production Build

**Backend:**
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend:**
cd frontend
npm run build
npm run preview
```

---

## API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "student@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid",
    "email": "student@example.com",
    "full_name": "John Doe"
  }
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "student@example.com",
  "password": "securepassword"
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer {token}
```

### Chat Endpoints

#### Send Message
```http
POST /api/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "Am I eligible for NELFUND?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "Based on NELFUND documents...",
  "sources": ["NELFUND Act 2023", "Eligibility Guidelines"],
  "session_id": "uuid"
}
```

#### Get Chat History
```http
GET /api/chat/history
Authorization: Bearer {token}
```

#### Get Sessions
```http
GET /api/chat/sessions
Authorization: Bearer {token}
```

#### Delete Session
```http
DELETE /api/chat/session/{session_id}
Authorization: Bearer {token}
```

---

## Testing the System

### Test the RAG Engine

cd backend
python -c "
from rag_engine import get_rag_agent
agent = get_rag_agent()
result = agent.query('Am I eligible for NELFUND?')
print(result)
"
```

### Test API Endpoints

# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'
```

---

## Features Walkthrough

### 1. **Interactive Homepage**
- Animated hero section with gradient text
- Feature cards with hover effects
- Statistics section
- CTA buttons to official NELFUND site
- Fully responsive design

### 2. **Authentication System**
- Beautiful login/register forms
- Form validation
- Error handling with user-friendly messages
- Automatic redirect after login
- Secure JWT token storage

### 3. **Chat Interface**
- Claude AI-inspired design
- Collapsible sidebar with chat history
- Dark/light mode toggle (smooth transitions)
- Message bubbles with proper styling
- Source citations displayed
- Loading indicators
- Auto-scroll to latest message
- Suggested prompts for new users

### 4. **Agentic RAG System**
```
User Query → Classify → Retrieve (if needed) → Generate Response
                ↓
        "Hello" → Don't retrieve
        "Eligibility?" → Retrieve documents
```

---

## Troubleshooting

### Issue: ChromaDB errors
**Solution:** Delete the `chroma_db` folder and restart the backend

### Issue: OpenAI API errors
**Solution:** Check your `.env` file has the correct API key

### Issue: CORS errors
**Solution:** Ensure backend CORS settings include your frontend URL

### Issue: Documents not loading
**Solution:** Check that PDFs are in `backend/data/documents/`

---

## Adding NELFUND Documents

### Step-by-Step Guide

1. **Obtain official NELFUND documents (PDFs)**
   - Student Loan Act 2023
   - NELFUND Application Guidelines
   - Eligibility Criteria
   - FAQs and other official documents

2. **Add them to the data folder:**
   mkdir -p backend/data
   # Copy your PDFs to backend/data/
   ```

3. **Run the setup script:**
   cd backend
   python setup_vectordb.py
   ```

4. **The system will automatically:**
   - Load all PDFs
   - Split into optimized chunks (1000 chars with 200 overlap)
   - Create semantic embeddings
   - Store in ChromaDB vector database
   - Show statistics and test searches

5. **To update documents later:**
   - Add new PDFs to `backend/data/`
   - Run `python setup_vectordb.py` again
   - Choose "yes" when asked to recreate the database

---

## Deployment

### Backend Deployment (Railway/Render/DigitalOcean)

# Install dependencies
pip install -r requirements.txt

# Run with gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Deployment (Vercel/Netlify)

npm run build


---

## Team Members

- Divine Joshua Gbadamosi
- Oludayo Oluwole


---
## Acknowledgments

- NELFUND for making higher education accessible
- Anthropic for Claude AI inspiration
- LangChain team for amazing tools
- Nigerian students everywhere

---
**Built with ❤️ for Nigerian Students**