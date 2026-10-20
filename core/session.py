import uuid
from typing import Optional
from redis.asyncio import Redis
from core.config import settings


async def create_session(redis: Redis, user_id: int) -> str:
    session_id = str(uuid.uuid4())
    key = f"session:{session_id}"
    await redis.setex(key, settings.SESSION_TTL, str(user_id))
    return session_id


async def get_user_id_from_session(redis: Redis, session_id: str) -> Optional[int]:
    key = f"session:{session_id}"
    user_id = await redis.get(key)
    if user_id:
        return int(user_id)
    return None


async def delete_session(redis: Redis, session_id: str) -> None:
    key = f"session:{session_id}"
    await redis.delete(key)
