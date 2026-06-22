from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from app.core.database import Base


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    planner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    event_name = Column(String, nullable=False)

    status = Column(String, default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)