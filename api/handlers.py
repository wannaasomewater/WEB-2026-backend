from sqlalchemy import select, text
from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from db.session import get_db
from models.electronic_device import ElectronicDevice
from models.device_like import DeviceLike
from models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Константа: ID текущего пользователя (singleton)
CURRENT_USER_ID = 1


async def get_likes_count(db: AsyncSession, device_id: int) -> int:
    """Подсчёт лайков через ORM"""
    stmt = select(DeviceLike).where(DeviceLike.device_id == device_id)
    result = await db.execute(stmt)
    return len(result.scalars().all())


# ============ GET 1: СПИСОК ПРИБОРОВ (ПЛИТКА) ============
@router.get("/")
async def get_devices_list(
    request: Request,
    max_power: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ElectronicDevice).where(ElectronicDevice.status == "published")
    
    if max_power is not None:
        stmt = stmt.where(ElectronicDevice.power_consumption <= max_power)
    
    result = await db.execute(stmt)
    devices = result.scalars().all()
    
    devices_with_likes = []
    for device in devices:
        likes_count = await get_likes_count(db, device.id)
        devices_with_likes.append({
            "device": device,
            "likes_count": likes_count
        })
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "devices": devices_with_likes,
            "max_power": max_power if max_power else ""
        }
    )


# ============ GET 2: ЧЕРНОВИК ============
@router.get("/draft")
async def get_draft_device(request: Request, db: AsyncSession = Depends(get_db)):
    stmt = select(ElectronicDevice).where(ElectronicDevice.status == "draft")
    result = await db.execute(stmt)
    draft_device = result.scalar_one_or_none()
    
    return templates.TemplateResponse(
        request=request,
        name="draft.html",
        context={"device": draft_device}
    )


# ============ GET 3: ЛЕНТА ============
@router.get("/device/{device_id}")
async def get_device_feed(
    request: Request,
    device_id: int,
    show_next: Optional[bool] = Query(False, alias="next"),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ElectronicDevice).where(
        ElectronicDevice.id == device_id,
        ElectronicDevice.status != "deleted"
    )
    result = await db.execute(stmt)
    device = result.scalar_one_or_none()
    
    if show_next and device:
        avail_stmt = select(ElectronicDevice).where(ElectronicDevice.status != "deleted")
        result = await db.execute(avail_stmt)
        available = result.scalars().all()
        
        current_index = None
        for i, d in enumerate(available):
            if d.id == device.id:
                current_index = i
                break
        
        if current_index is not None:
            next_index = (current_index + 1) % len(available)
            device = available[next_index]
    
    likes_count = 0
    if device:
        likes_count = await get_likes_count(db, device.id)
    
    return templates.TemplateResponse(
        request=request,
        name="device.html",
        context={"device": device, "likes_count": likes_count}
    )


# ============ POST 1: ДОБАВЛЕНИЕ ЧЕРЕЗ ORM ============
@router.post("/draft/create")
async def create_draft(
    device_name: str = Form(...),
    device_type: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Создание карточки (кнопка Далее)"""
    new_device = ElectronicDevice(
        device_name=device_name,
        device_type=device_type,
        power_consumption=0,
        emf_level=0.0,
        frequency_range="",
        safety_distance=0.0,
        description="",
        status="draft",
        created_by="user1"
    )
    db.add(new_device)
    await db.commit()
    return RedirectResponse(url="/draft", status_code=303)


# ============ POST 2: ПУБЛИКАЦИЯ ЧЕРЕЗ ORM ============
@router.post("/draft/{device_id}/publish")
async def publish_device(
    device_id: int,
    description: str = Form(...),
    power_consumption: int = Form(...),
    emf_level: float = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Публикация карточки (кнопка Опубликовать)"""
    stmt = select(ElectronicDevice).where(ElectronicDevice.id == device_id)
    result = await db.execute(stmt)
    device = result.scalar_one_or_none()
    
    if device:
        device.description = description
        device.power_consumption = power_consumption
        device.emf_level = emf_level
        device.status = "published"
        device.published_at = datetime.now()
        await db.commit()
    
    return RedirectResponse(url="/", status_code=303)


# ============ POST 3: УДАЛЕНИЕ ЧЕРЕЗ SQL КУРСОР ============
@router.post("/device/{device_id}/delete")
async def delete_device(device_id: int, db: AsyncSession = Depends(get_db)):
    """Мягкое удаление через Raw SQL (без ORM)"""
    update_query = """
        UPDATE electronic_devices 
        SET status = 'deleted' 
        WHERE id = :id
    """
    await db.execute(text(update_query), {"id": device_id})
    await db.commit()
    return RedirectResponse(url="/", status_code=303)
