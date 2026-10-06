from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from db.base import Base


class ElectricalAppliance(Base):
    __tablename__ = "electrical_appliances"

    id = Column(Integer, primary_key=True, index=True)
    appliance_name = Column(String(100), nullable=False)
    power_consumption = Column(Integer, nullable=True)
    frequency = Column(Float, nullable=True)
    emf_level = Column(Float, nullable=True)
    safety_distance = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="draft", nullable=False)
    image_url = Column(String(255), nullable=True)
    video_url = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    created_by = Column(String(50), nullable=False)

    published_at = Column(DateTime(timezone=True), nullable=True)
