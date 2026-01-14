from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import chromadb
from chromadb.config import Settings
import bcrypt
import jwt
from datetime import datetime, timedelta
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="NELFUND Navigator API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
security = HTTPBearer()

# Initialize ChromaDB Client for users and chats
# Note: Documents are handled separately by the RAG engine
chroma_client = chromadb.PersistentClient(path="./chroma_users")

# Collections (users and chats only - documents handled by RAG engine)
users_collection = chroma_client.get_or_create_collection(name="users")
chats_collection = chroma_client.get_or_create_collection(name="chats")

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    session_id: str

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token from Authorization header"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def optional_verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """Optional token verification - returns None if no token provided"""
    if not credentials:
        return None
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# User Management Endpoints
@app.post("/api/auth/register")
async def register(user: UserRegister):
    try:
        # Check if user exists
        existing = users_collection.get(where={"email": user.email})
        if existing['ids']:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        user_id = str(uuid.uuid4())
        hashed_pw = hash_password(user.password)
        
        users_collection.add(
            ids=[user_id],
            documents=[user.email],
            metadatas=[{
                "email": user.email,
                "password": hashed_pw,
                "full_name": user.full_name,
                "created_at": datetime.utcnow().isoformat()
            }]
        )
        
        token = create_access_token({"user_id": user_id, "email": user.email})
        return {
            "token": token,
            "user": {
                "id": user_id,
                "email": user.email,
                "full_name": user.full_name
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
async def login(user: UserLogin):
    try:
        # Find user
        results = users_collection.get(where={"email": user.email})
        
        if not results['ids']:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_data = results['metadatas'][0]
        user_id = results['ids'][0]
        
        # Verify password
        if not verify_password(user.password, user_data['password']):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_access_token({"user_id": user_id, "email": user.email})
        return {
            "token": token,
            "user": {
                "id": user_id,
                "email": user_data['email'],
                "full_name": user_data['full_name']
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/me")
async def get_current_user(payload: dict = Depends(verify_token)):
    try:
        user_id = payload['user_id']
        results = users_collection.get(ids=[user_id])
        
        if not results['ids']:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = results['metadatas'][0]
        return {
            "id": user_id,
            "email": user_data['email'],
            "full_name": user_data['full_name']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat Endpoints
@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Chat endpoint - requires authentication"""
    try:
        # Verify token to get user_id
        try:
            token = credentials.credentials
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get('user_id')
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        try:
            from rag_engine import get_rag_agent
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="RAG engine not initialized. Run: python setup_vectordb.py"
            )
        
        # Generate session ID if not provided
        session_id = message.session_id or str(uuid.uuid4())
        
        # Get chat history for this session
        chat_history = []
        try:
            # Query by session_id (ChromaDB requires single where condition)
            history_results = chats_collection.get(
                where={"session_id": session_id}
            )
            if history_results['ids']:
                for i in range(len(history_results['ids'])):
                    metadata = history_results['metadatas'][i]
                    # Only add if belongs to same user
                    if metadata.get('user_id') == user_id:
                        chat_history.append({
                            "role": "user",
                            "content": metadata['user_message']
                        })
                        chat_history.append({
                            "role": "assistant",
                            "content": metadata['bot_response']
                        })
        except Exception as e:
            print(f"Warning: Could not retrieve chat history: {e}")
            chat_history = []
        
        # Use RAG agent to generate response
        agent = get_rag_agent()
        result = agent.query(message.message, chat_history=chat_history)
        
        response_text = result['response']
        sources = result.get('sources', [])
        
        # Store chat
        chat_id = str(uuid.uuid4())
        try:
            chats_collection.add(
                ids=[chat_id],
                documents=[message.message],
                metadatas=[{
                    "user_id": user_id,
                    "session_id": session_id,
                    "user_message": message.message,
                    "bot_response": response_text,
                    "timestamp": datetime.utcnow().isoformat()
                }]
            )
        except Exception as e:
            print(f"Warning: Could not store chat: {e}")
        
        return ChatResponse(
            response=response_text,
            sources=sources,
            session_id=session_id
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/api/chat/history/{session_id}")
async def get_session_chat_history(session_id: str, payload: dict = Depends(verify_token)):
    """Get chat history for a specific session (requires auth)"""
    try:
        user_id = payload['user_id']
        # Query by session_id only
        results = chats_collection.get(where={"session_id": session_id})
        
        chats = []
        if results['ids']:
            for i, chat_id in enumerate(results['ids']):
                metadata = results['metadatas'][i]
                # Filter by user_id to prevent accessing other users' chats
                if metadata.get('user_id') == user_id:
                    chats.append({
                        "id": chat_id,
                        "user_message": metadata['user_message'],
                        "bot_response": metadata['bot_response'],
                        "sources": metadata.get('sources', []),
                        "timestamp": metadata['timestamp']
                    })
        
        # Sort by timestamp (oldest first)
        chats.sort(key=lambda x: x['timestamp'])
        return {"session_id": session_id, "chats": chats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/history")
async def get_chat_history(payload: dict = Depends(verify_token)):
    try:
        user_id = payload['user_id']
        results = chats_collection.get(where={"user_id": user_id})
        
        chats = []
        if results['ids']:
            for i, chat_id in enumerate(results['ids']):
                metadata = results['metadatas'][i]
                chats.append({
                    "id": chat_id,
                    "session_id": metadata['session_id'],
                    "user_message": metadata['user_message'],
                    "bot_response": metadata['bot_response'],
                    "timestamp": metadata['timestamp']
                })
        
        # Sort by timestamp
        chats.sort(key=lambda x: x['timestamp'], reverse=True)
        return {"chats": chats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/sessions")
async def get_sessions(payload: dict = Depends(verify_token)):
    try:
        user_id = payload['user_id']
        results = chats_collection.get(where={"user_id": user_id})
        
        sessions = {}
        if results['ids']:
            for i, chat_id in enumerate(results['ids']):
                metadata = results['metadatas'][i]
                session_id = metadata['session_id']
                
                if session_id not in sessions:
                    sessions[session_id] = {
                        "session_id": session_id,
                        "first_message": metadata['user_message'][:50],
                        "timestamp": metadata['timestamp'],
                        "message_count": 0
                    }
                sessions[session_id]['message_count'] += 1
        
        return {"sessions": list(sessions.values())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat/session/{session_id}")
async def delete_session(session_id: str, payload: dict = Depends(verify_token)):
    try:
        user_id = payload['user_id']
        results = chats_collection.get(where={"user_id": user_id, "session_id": session_id})
        
        if results['ids']:
            chats_collection.delete(ids=results['ids'])
        
        return {"message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health Check
@app.get("/")
async def root():
    return {"message": "NELFUND Navigator API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)