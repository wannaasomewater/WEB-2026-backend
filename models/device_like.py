from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from db.base import Base


class DeviceLike(Base):
    __tablename__ = "device_likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("electronic_devices.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
