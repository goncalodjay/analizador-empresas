from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import RedisClient

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {e}")

    try:
        await RedisClient.ping()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis unhealthy: {e}")

    return {"status": "ok", "database": "ok", "redis": "ok"}
