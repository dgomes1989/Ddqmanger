from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import documents, knowledge_base, requests
from app.config import settings

app = FastAPI(title="DDQ Manager", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(knowledge_base.router, prefix="/api/knowledge-base", tags=["knowledge-base"])
app.include_router(requests.router, prefix="/api/requests", tags=["requests"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
