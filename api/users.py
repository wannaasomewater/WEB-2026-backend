from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.user import User
from schemas.user import UserRegisterSchema, UserResponseSchema

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register", status_code=201, response_model=UserResponseSchema)
async def register_user(data: UserRegisterSchema, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.username == data.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Уже существует")

    password_hash = f"hash_{data.password}"

    new_user = User(
        username=data.username,
        full_name=data.full_name,
        password_hash=password_hash,
        role="user",
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserResponseSchema.model_validate(new_user)


@router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or user.password_hash != f"hash_{password}":
        raise HTTPException(status_code=401, detail="Неверные данные")

    return {"status": "success", "message": "Заглушка", "user_id": user.id}


@router.post("/logout")
async def logout():
    return {"status": "success", "message": "Заглушка"}
