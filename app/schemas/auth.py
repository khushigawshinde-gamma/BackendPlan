from typing import Annotated

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str =  Field(
        min_length=8,
        max_length=50,
        description="Password must be between 8 and 50 characters"
    )
    confirm_password: str 
    role:str


class UserLogin(BaseModel): 
    email: EmailStr
    password: str


class OTPVerify(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


from pydantic import BaseModel, Field


class PlannerProfileCreate(BaseModel):

    business_name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    bio: str = Field(
        ...,
        min_length=10,
        max_length=500
    )

    city: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    contact_number: Annotated[
    str,
    Field(pattern=r"^\d{10}$")
]

    instagram: str | None = None

    experience: int | None = None

class RequestCreate(BaseModel):
    planner_id: int
    event_name: str


class RequestResponse(BaseModel):
    id: int
    user_id: int
    planner_id: int
    event_name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class PlannerInboxResponse(BaseModel):
    id: int
    user_id: int
    planner_id: int
    event_name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

