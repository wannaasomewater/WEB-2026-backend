from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ApplianceListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    appliance_name: str
    power_consumption: Optional[int] = None
    frequency: Optional[float] = None
    emf_level: Optional[float] = None
    safety_distance: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    status: str
    is_creator: int = 0


class ApplianceFeedSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    appliance_name: str
    power_consumption: Optional[int] = None
    frequency: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    is_liked: int = 0


class ApplianceDraftSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    appliance_name: str
    power_consumption: Optional[int] = None
    frequency: Optional[float] = None
    emf_level: Optional[float] = None
    safety_distance: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    status: str
