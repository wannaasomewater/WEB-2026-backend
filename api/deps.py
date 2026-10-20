from fastapi import Depends, Cookie, HTTPException
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from db.session import get_db
from core.redis_client import get_redis
from core.session import get_user_id_from_session
from models.user import User


async def get_current_user_id(
    session_id: Optional[str] = Cookie(None, alias="session_id"),
    redis: Redis = Depends(get_redis),
) -> Optional[int]:
    if not session_id:
        return None
    return await get_user_id_from_session(redis, session_id)


async def require_auth(
    user_id: Optional[int] = Depends(get_current_user_id),
) -> int:
    if user_id is None:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    return user_id
