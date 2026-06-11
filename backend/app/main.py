from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analysis, auth, health, ingestion, news, portfolio, strategies, watchlists


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Stock Analyzer API",
    description="Portfolio intelligence platform backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router)
app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(watchlists.router)
app.include_router(ingestion.router)
app.include_router(news.router)
app.include_router(strategies.router)
app.include_router(health.router)
