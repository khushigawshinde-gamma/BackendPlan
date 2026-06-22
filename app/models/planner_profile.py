from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class PlannerProfile(Base):
    __tablename__ = "planner_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True
    )

    business_name = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    city = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)

    instagram = Column(String, nullable=True)
    experience = Column(Integer, nullable=True)