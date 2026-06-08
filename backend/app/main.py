from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import auth, health, portfolio, watchlists


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Stock Analyzer API",
    description="Portfolio intelligence platform backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(watchlists.router)
app.include_router(health.router)
