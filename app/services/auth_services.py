from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.core.security import create_access_token
from app.models.User import User
import random
from datetime import datetime, timedelta
from app.schemas.auth import UserRegister, UserLogin, OTPVerify
from app.services.email_service import send_otp_email
from app.schemas.auth import PlannerProfileCreate
from app.models.planner_profile import PlannerProfile
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.request import Request




pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_user(
    db: Session,
    user_data: UserRegister
):

    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
        role=user_data.role,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }


def login_user(
    db: Session,
    user_data: UserLogin
):

    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not verify_password(
        user_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    otp = generate_otp()

    user.otp_code = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)

    db.commit()

    send_otp_email(
    user.email,
    otp
)

    return {
    "message": "OTP sent successfully"
}


def generate_otp():
    return str(random.randint(100000, 999999))



def verify_otp_user(
    db: Session,
    otp_data: OTPVerify
):

    user = (
        db.query(User)
        .filter(User.email == otp_data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not user.otp_expiry:
        raise HTTPException(
        status_code=400,
        detail="OTP not found"
    )
    if user.otp_code != otp_data.otp:
        raise HTTPException(
        status_code=400,
        detail="Invalid OTP"
    )

    if datetime.utcnow() > user.otp_expiry:
        raise HTTPException(
            status_code=400,
            detail="OTP expired"
        )

    user.is_verified = True

    user.otp_code = None
    user.otp_expiry = None

    db.commit()

    token = create_access_token(
        {
            "user_id": user.id,
            "email": user.email,
            "role": user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

def create_planner_profile(
db: Session,
profile_data: PlannerProfileCreate,
current_user
):
    if current_user["role"] != "planner":
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only planners can create profile"
    )

    existing_profile = (
    db.query(PlannerProfile)
    .filter(
        PlannerProfile.user_id ==current_user["user_id"]
    )
    .first()
)

    if existing_profile:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Profile already exists"
    )
    new_profile = PlannerProfile(
    user_id=current_user["user_id"],
    business_name=profile_data.business_name,
    bio=profile_data.bio,
    city=profile_data.city,
    contact_number=profile_data.contact_number,
    instagram=profile_data.instagram,
    experience=profile_data.experience
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return {
    "message": "Planner profile created successfully",
    "profile_id": new_profile.id
    }


def create_request(
    db: Session,
    user_id: int,
    planner_id: int,
    event_name: str
):
    
    # Check planner exists
    planner = db.query(User).filter(
        User.id == planner_id,
        User.role == "planner"
    ).first()

    if not planner:
        raise HTTPException(
            status_code=404,
            detail="Planner not found"
        )
     # Create request
    new_request = Request(
        user_id=user_id,
        planner_id=planner_id,
        event_name=event_name,
        status="pending"
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request

def get_planner_requests(
    db: Session,
    current_user
):
    if current_user["role"] != "planner":
        raise HTTPException(
            status_code=403,
            detail="Only planners can view inbox"
        )

    requests = (
        db.query(Request)
        .filter(
            Request.planner_id == current_user["user_id"]
        )
        .order_by(Request.created_at.desc())
        .all()
    )

    return requests


def reject_request(
    db: Session,
    request_id: int,
    current_user
):
    if current_user["role"] != "planner":
        raise HTTPException(
            status_code=403,
            detail="Only planners can reject requests"
        )

    request = (
        db.query(Request)
        .filter(
            Request.id == request_id,
            Request.planner_id == current_user["user_id"]
        )
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    request.status = "rejected"

    db.commit()
    db.refresh(request)

    return {
        "message": "Request rejected successfully"
    }

def accept_request(
    db: Session,
    request_id: int,
    current_user
):

    if current_user["role"] != "planner":
        raise HTTPException(
            status_code=403,
            detail="Only planners can accept requests"
        )

    request = (
        db.query(Request)
        .filter(
            Request.id == request_id,
            Request.planner_id == current_user["user_id"]
        )
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    if request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Request already processed"
        )

    request.status = "accepted"

    db.commit()
    db.refresh(request)

    return {
        "message": "Request accepted successfully"
    }