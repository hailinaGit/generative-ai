"""FastAPI Service for Cambodia HR RAG Knowledge Assistant.

Endpoints:
- GET  /health   : Health check and ChromaDB collection status.
- POST /query    : Natural language question answering with grounded context and citations.
- POST /retrieve : Pure retrieval endpoint returning top-k chunks and citations without LLM synthesis.

Run:
    uvicorn src.api:app --reload --port 8000
"""
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

STATIC_DIR = Path(__file__).resolve().parent / "static"

try:
    from src.retrieve import get_collection, retrieve_relevant_chunks
    from src.generate import generate_answer
except ModuleNotFoundError:
    from retrieve import get_collection, retrieve_relevant_chunks
    from generate import generate_answer

app = FastAPI(
    title="Cambodia HR & Labor Law RAG Knowledge Assistant",
    description="Internal RAG API for HR officers and employees to query verified Cambodian Labor Law policies.",
    version="1.0.0",
)


# --- Request & Response Schemas ---
class QueryRequest(BaseModel):
    question: str = Field(..., examples=["How many days of annual leave do employees receive in Cambodia?"])
    model: str = Field(default="llama3.2", description="Ollama model name")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of context chunks to retrieve")
    temperature: float = Field(default=0.0, ge=0.0, le=1.0, description="Generation temperature (0.0 for strict facts)")


class Citation(BaseModel):
    source: str
    section: str
    distance: float


class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: list[Citation]


class RetrieveRequest(BaseModel):
    query: str = Field(..., examples=["What are the overtime pay rates?"])
    top_k: int = Field(default=3, ge=1, le=10)


class ChunkResult(BaseModel):
    content: str
    source: str
    section: str
    chunk_index: int
    distance: float


class RetrieveResponse(BaseModel):
    query: str
    count: int
    results: list[ChunkResult]


class HealthResponse(BaseModel):
    status: str
    collection_name: str
    total_chunks: int


# --- API Routes ---
@app.get("/")
def root():
    """Serve the interactive web interface, or API overview if UI file is absent."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": "Welcome to Cambodia HR & Labor Law RAG Knowledge Assistant API",
        "docs_url": "/docs",
        "health_check": "/health",
        "endpoints": {
            "GET /health": "Check database status and total ingested chunks",
            "POST /retrieve": "Query top-k chunks and citations without LLM generation",
            "POST /query": "Natural language question answering with grounded citations"
        }
    }


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Verify vector DB connection and chunk counts."""
    try:
        col = get_collection()
        return HealthResponse(
            status="healthy",
            collection_name=col.name,
            total_chunks=col.count(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


@app.post("/retrieve", response_model=RetrieveResponse)
def retrieve_endpoint(req: RetrieveRequest):
    """Retrieve raw chunks and citations matching query without invoking LLM."""
    try:
        chunks = retrieve_relevant_chunks(query=req.query, top_k=req.top_k)
        return RetrieveResponse(
            query=req.query,
            count=len(chunks),
            results=[ChunkResult(**c) for c in chunks],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


@app.post("/query", response_model=QueryResponse)
def query_endpoint(req: QueryRequest):
    """Grounded RAG generation using local LangChain Ollama model."""
    try:
        res = generate_answer(
            query=req.question,
            model_name=req.model,
            top_k=req.top_k,
            temperature=req.temperature,
        )
        return QueryResponse(
            question=res["query"],
            answer=res["answer"],
            citations=[Citation(**c) for c in res["citations"]],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}. Make sure Ollama is running and model '{req.model}' is available."
        )

