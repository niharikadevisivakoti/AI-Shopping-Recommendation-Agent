from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from backend.agent import agent_chat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from recommendation_engine.recommender import RecommendationEngine
from backend.agent import agent_chat


engine = RecommendationEngine(
    ROOT / "data" / "products.csv"
)


app = FastAPI(
    title="Product Recommendation System API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class RecommendationRequest(BaseModel):
    viewed_product_ids: list[int] = Field(
        default_factory=list
    )
    category: str | None = None
    limit: int = Field(
        default=6,
        ge=1,
        le=20
    )


class AgentChatRequest(BaseModel):
    message: str


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/categories")
def categories():
    return engine.categories()


@app.get("/api/products")
def products(
    q: str | None = Query(None),
    category: str | None = Query(None)
):
    return engine.products(q, category)


@app.get("/api/products/{product_id}")
def product(product_id: int):
    x = engine.product(product_id)

    if not x:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return x


@app.get("/api/products/{product_id}/similar")
def similar(
    product_id: int,
    limit: int = Query(6, ge=1, le=20)
):
    if not engine.product(product_id):
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return engine.similar(product_id, limit)


@app.post("/api/recommendations")
def recommendations(req: RecommendationRequest):
    return engine.personalized(
        req.viewed_product_ids,
        req.category,
        req.limit
    )


# AI SHOPPING AGENT
@app.post("/api/agent/chat")
def agent_chat_endpoint(req: AgentChatRequest):
    return agent_chat(req.message)