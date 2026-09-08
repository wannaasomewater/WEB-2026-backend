from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from typing import Optional
from data.collections import emf_devices_db, device_likes

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_likes_count(device_id: int) -> int:
    return len([like for like in device_likes if like["device_id"] == device_id])

@router.get("/")
def get_devices_list(
    request: Request,
    max_power: Optional[int] = Query(None, description="Максимальная мощность (Вт)")
):
    devices = [d for d in emf_devices_db if d["status"] == "published"]

    if max_power is not None:
        devices = [d for d in devices if d["power_consumption"] <= max_power]

    for device in devices:
        device["likes_count"] = get_likes_count(device["id"])

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "devices": devices,
            "max_power": max_power if max_power else ""
        }
    )

@router.get("/draft")
def get_draft_device(request: Request):
    draft_device = next(
        (d for d in emf_devices_db if d["status"] == "draft"),
        None
    )

    if draft_device:
        draft_device["likes_count"] = get_likes_count(draft_device["id"])

    return templates.TemplateResponse(
        request=request,
        name="draft.html",
        context={"device": draft_device}
    )

@router.get("/device/{device_id}")
def get_device_feed(
    request: Request,
    device_id: int,
    show_next: Optional[bool] = Query(False, alias="next", description="Показать следующий прибор")
):
    # Используем find вместо next, чтобы избежать конфликта
    device = None
    for d in emf_devices_db:
        if d["id"] == device_id and d["status"] != "deleted":
            device = d
            break

    if show_next and device:
        available_devices = [d for d in emf_devices_db if d["status"] != "deleted"]
        current_index = None
        for i, d in enumerate(available_devices):
            if d["id"] == device["id"]:
                current_index = i
                break

        if current_index is not None:
            next_index = (current_index + 1) % len(available_devices)
            device = available_devices[next_index]

    if device:
        device["likes_count"] = get_likes_count(device["id"])

    return templates.TemplateResponse(
        request=request,
        name="device.html",
        context={"device": device}
    )
