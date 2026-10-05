from sqlalchemy import select, text
from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from db.session import get_db
from models.electrical_appliance import ElectricalAppliance
from models.device_like import DeviceLike

router = APIRouter()
templates = Jinja2Templates(directory="templates")


async def get_likes_count(db: AsyncSession, appliance_id: int) -> int:
    stmt = select(DeviceLike).where(DeviceLike.appliance_id == appliance_id)
    result = await db.execute(stmt)
    return len(result.scalars().all())


# ============ GET 1: СПИСОК ============
@router.get("/")
async def get_appliances_list(
    request: Request,
    max_power: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ElectricalAppliance).where(ElectricalAppliance.status == "published")
    
    if max_power is not None:
        stmt = stmt.where(ElectricalAppliance.power_consumption <= max_power)
    
    result = await db.execute(stmt)
    appliances = result.scalars().all()
    
    appliances_with_likes = []
    for appliance in appliances:
        likes_count = await get_likes_count(db, appliance.id)
        appliances_with_likes.append({
            "appliance": appliance,
            "likes_count": likes_count
        })
    
    return templates.TemplateResponse(
        request=request,
        name="electrical_appliances_list.html",
        context={
            "appliances": appliances_with_likes,
            "max_power": max_power if max_power else ""
        }
    )


# ============ GET 2: ЧЕРНОВИК ============
@router.get("/draft")
async def get_draft_appliance(request: Request, db: AsyncSession = Depends(get_db)):
    stmt = select(ElectricalAppliance).where(ElectricalAppliance.status == "draft")
    result = await db.execute(stmt)
    draft_appliance = result.scalar_one_or_none()
    
    return templates.TemplateResponse(
        request=request,
        name="electrical_appliance_draft.html",
        context={"appliance": draft_appliance}
    )


# ============ GET 3: ЛЕНТА ============
@router.get("/appliance/{appliance_id}")
async def get_appliance_feed(
    request: Request,
    appliance_id: int,
    show_next: Optional[bool] = Query(False, alias="next"),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ElectricalAppliance).where(
        ElectricalAppliance.id == appliance_id,
        ElectricalAppliance.status != "deleted"
    )
    result = await db.execute(stmt)
    appliance = result.scalar_one_or_none()
    
    if show_next and appliance:
        avail_stmt = select(ElectricalAppliance).where(ElectricalAppliance.status != "deleted")
        result = await db.execute(avail_stmt)
        available = result.scalars().all()
        
        current_index = None
        for i, a in enumerate(available):
            if a.id == appliance.id:
                current_index = i
                break
        
        if current_index is not None:
            next_index = (current_index + 1) % len(available)
            appliance = available[next_index]
    
    likes_count = 0
    if appliance:
        likes_count = await get_likes_count(db, appliance.id)
    
    return templates.TemplateResponse(
        request=request,
        name="electrical_appliance_feed.html",
        context={"appliance": appliance, "likes_count": likes_count}
    )


# ============ POST 1: ДОБАВЛЕНИЕ (Далее) ============
@router.post("/draft/create")
async def create_draft(
    appliance_name: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    new_appliance = ElectricalAppliance(
        appliance_name=appliance_name,
        power_consumption=None,
        frequency=None,
        status="draft",
        created_by="user1"
    )
    db.add(new_appliance)
    await db.commit()
    return RedirectResponse(url="/draft", status_code=303)


# ============ POST 2: ПУБЛИКАЦИЯ ============
@router.post("/draft/{appliance_id}/publish")
async def publish_appliance(
    appliance_id: int,
    description: str = Form(None),
    power_consumption: int = Form(None),
    frequency: float = Form(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ElectricalAppliance).where(ElectricalAppliance.id == appliance_id)
    result = await db.execute(stmt)
    appliance = result.scalar_one_or_none()
    
    if appliance:
        appliance.description = description
        appliance.power_consumption = power_consumption
        appliance.frequency = frequency
        appliance.status = "published"
        appliance.published_at = datetime.now()
        await db.commit()
    
    return RedirectResponse(url="/", status_code=303)


# ============ POST 3: УДАЛЕНИЕ ЧЕРЕЗ SQL КУРСОР ============
@router.post("/appliance/{appliance_id}/delete")
async def delete_appliance(appliance_id: int, db: AsyncSession = Depends(get_db)):
    update_query = """
        UPDATE electrical_appliances 
        SET status = 'deleted' 
        WHERE id = :id
    """
    await db.execute(text(update_query), {"id": appliance_id})
    await db.commit()
    return RedirectResponse(url="/", status_code=303)
