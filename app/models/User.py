from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy import DateTime

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False, index=True)

    password = Column(String(255), nullable=False)

    role = Column(String(20), nullable=False)

    is_verified = Column(Boolean, default=False)
    otp_code = Column(String(6), nullable=True)
    otp_expiry = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )