from sqlalchemy import Column, Integer, ForeignKey
from db.base import Base


class DeviceLike(Base):
    __tablename__ = "device_likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appliance_id = Column(Integer, ForeignKey("electrical_appliances.id"), nullable=False)
