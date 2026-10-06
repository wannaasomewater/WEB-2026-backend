from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

from db.session import get_db
from models.electrical_appliance import ElectricalAppliance
from models.device_like import DeviceLike
from schemas.appliance import (
    ApplianceListSchema,
    ApplianceFeedSchema,
    ApplianceDraftSchema,
)
from core.current_user import get_current_user_id
from services.s3_service import s3_service

router = APIRouter(prefix="/api/appliances", tags=["appliances"])


async def is_liked_by_user(db: AsyncSession, appliance_id: int, user_id: int) -> bool:
    stmt = select(DeviceLike).where(
        DeviceLike.appliance_id == appliance_id,
        DeviceLike.user_id == user_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


# ============ GET список с фильтром ============
@router.get("", response_model=List[ApplianceListSchema])
async def get_appliances_list(
    max_power: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Список опубликованных с фильтром по мощности"""
    stmt = select(ElectricalAppliance).where(ElectricalAppliance.status == "published")
    if max_power is not None:
        stmt = stmt.where(ElectricalAppliance.power_consumption <= max_power)

    result = await db.execute(stmt)
    appliances = result.scalars().all()

    user_id = get_current_user_id()

    return [
        ApplianceListSchema(
            **{
                **a.__dict__,
                "is_creator": 1 if a.created_by == str(user_id) else 0,
            }
        )
        for a in appliances
    ]


# ============ GET лента ============
@router.get("/feed", response_model=List[ApplianceFeedSchema])
async def get_appliances_feed(db: AsyncSession = Depends(get_db)):
    """Лента опубликованных с признаком лайка"""
    stmt = select(ElectricalAppliance).where(ElectricalAppliance.status == "published")
    result = await db.execute(stmt)
    appliances = result.scalars().all()

    user_id = get_current_user_id()
    feed = []

    for a in appliances:
        liked = await is_liked_by_user(db, a.id, user_id)
        feed.append(
            ApplianceFeedSchema(
                **{
                    **a.__dict__,
                    "is_liked": 1 if liked else 0,
                }
            )
        )

    return feed


# ============ GET черновик ============
@router.get("/draft", response_model=Optional[ApplianceDraftSchema])
async def get_appliance_draft(db: AsyncSession = Depends(get_db)):
    """Черновик текущего пользователя"""
    user_id = get_current_user_id()
    stmt = select(ElectricalAppliance).where(
        ElectricalAppliance.status == "draft",
        ElectricalAppliance.created_by == str(user_id),
    )
    result = await db.execute(stmt)
    draft = result.scalar_one_or_none()

    if not draft:
        return None

    return ApplianceDraftSchema(**draft.__dict__)


# ============ POST добавление с файлами ============
@router.post("", status_code=201)
async def create_appliance(
    appliance_name: str = Form(...),
    power_consumption: Optional[int] = Form(None),
    frequency: Optional[float] = Form(None),
    emf_level: Optional[float] = Form(None),
    safety_distance: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    """Создание с загрузкой файлов"""
    user_id = get_current_user_id()

    # Проверяем что нет другого черновика
    stmt = select(ElectricalAppliance).where(
        ElectricalAppliance.status == "draft",
        ElectricalAppliance.created_by == str(user_id),
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="У вас уже есть черновик")

    new_appliance = ElectricalAppliance(
        appliance_name=appliance_name,
        power_consumption=power_consumption,
        frequency=frequency,
        emf_level=emf_level,
        safety_distance=safety_distance,
        description=description,
        status="draft",
        created_by=str(user_id),
    )
    db.add(new_appliance)
    await db.flush()

    # Загружаем файлы
    if image and image.filename:
        content = await image.read()
        file_name = s3_service.generate_file_name(image.filename, new_appliance.id, "image")
        url = await s3_service.upload_file(content, file_name, image.content_type or "image/jpeg")
        new_appliance.image_url = url

    if video and video.filename:
        content = await video.read()
        file_name = s3_service.generate_file_name(video.filename, new_appliance.id, "video")
        url = await s3_service.upload_file(content, file_name, video.content_type or "video/mp4")
        new_appliance.video_url = url

    await db.commit()
    await db.refresh(new_appliance)

    return {"status": "success", "id": new_appliance.id, "message": "Услуга создана"}


# ============ PUT публикация ============
@router.put("/{appliance_id}/publish")
async def publish_appliance(appliance_id: int, db: AsyncSession = Depends(get_db)):
    user_id = get_current_user_id()

    stmt = select(ElectricalAppliance).where(
        ElectricalAppliance.id == appliance_id,
        ElectricalAppliance.created_by == str(user_id),
        ElectricalAppliance.status == "draft",
    )
    result = await db.execute(stmt)
    appliance = result.scalar_one_or_none()

    if not appliance:
        raise HTTPException(status_code=404, detail="Черновик не найден")

    appliance.status = "published"
    appliance.published_at = datetime.now()

    await db.commit()
    return {"status": "success", "message": "Опубликовано"}


# ============ DELETE soft delete ============
@router.delete("/{appliance_id}")
async def delete_appliance(appliance_id: int, db: AsyncSession = Depends(get_db)):
    user_id = get_current_user_id()

    stmt = select(ElectricalAppliance).where(
        ElectricalAppliance.id == appliance_id,
        ElectricalAppliance.created_by == str(user_id),
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Можно удалять только свои")

    update_query = """
        UPDATE electrical_appliances 
        SET status = 'deleted' 
        WHERE id = :id
    """
    await db.execute(text(update_query), {"id": appliance_id})
    await db.commit()

    return {"status": "success", "message": "Удалено"}


# ============ POST лайк (0/1) ============
@router.post("/{appliance_id}/like")
async def like_appliance(
    appliance_id: int,
    value: int = Form(...),
    db: AsyncSession = Depends(get_db),
):
    if value not in [0, 1]:
        raise HTTPException(status_code=400, detail="Значение 0 или 1")

    user_id = get_current_user_id()

    stmt = select(ElectricalAppliance).where(ElectricalAppliance.id == appliance_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Не найдено")

    like_stmt = select(DeviceLike).where(
        DeviceLike.appliance_id == appliance_id,
        DeviceLike.user_id == user_id,
    )
    like_result = await db.execute(like_stmt)
    existing_like = like_result.scalar_one_or_none()

    if value == 1 and not existing_like:
        db.add(DeviceLike(user_id=user_id, appliance_id=appliance_id))
    elif value == 0 and existing_like:
        await db.delete(existing_like)

    await db.commit()
    return {"status": "success", "message": "Лайк обновлён"}
