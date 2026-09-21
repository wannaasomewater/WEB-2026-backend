from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from db.base import Base


class ElectronicDevice(Base):
    __tablename__ = "electronic_devices"

    id = Column(Integer, primary_key=True, index=True)
    device_name = Column(String(100), nullable=False)
    device_type = Column(String(50), nullable=False)
    power_consumption = Column(Integer, nullable=False)
    emf_level = Column(Float, nullable=False)
    frequency_range = Column(String(50), nullable=False)
    safety_distance = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default="draft", nullable=False)
    image_url = Column(String(255), nullable=True)
    video_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String(50), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
