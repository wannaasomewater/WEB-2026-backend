from fastapi import APIRouter, Depends, HTTPException, Form, Response, Cookie
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from typing import Optional

from db.session import get_db
from core.redis_client import get_redis
from core.security import hash_password, verify_password
from core.session import create_session, delete_session, get_user_id_from_session
from models.user import User
from schemas.user import UserRegisterSchema, UserResponseSchema

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register", status_code=201, response_model=UserResponseSchema)
async def register_user(data: UserRegisterSchema, db: AsyncSession = Depends(get_db)):
    """Регистрация пользователя"""
    stmt = select(User).where(User.username == data.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    new_user = User(
        username=data.username,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
        role="user",
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserResponseSchema.model_validate(new_user)


@router.post("/login")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Аутентификация — создаёт сессию в Redis и ставит куку"""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверные данные")

    session_id = await create_session(redis, user.id)

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=3600,
        samesite="lax",
    )

    return {
        "status": "success",
        "message": "Успешный вход",
        "user_id": user.id,
        "session_id": session_id,
    }


@router.post("/logout")
async def logout(
    response: Response,
    session_id: Optional[str] = Cookie(None),
    redis: Redis = Depends(get_redis),
):
    """Деавторизация — удаляет сессию из Redis"""
    if session_id:
        await delete_session(redis, session_id)
        response.delete_cookie("session_id")

    return {"status": "success", "message": "Выход выполнен"}


@router.get("/me", response_model=UserResponseSchema)
async def get_me(
    session_id: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Текущий пользователь"""
    if not session_id:
        raise HTTPException(status_code=401, detail="Не авторизован")

    user_id = await get_user_id_from_session(redis, session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Сессия истекла")

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return UserResponseSchema.model_validate(user)
