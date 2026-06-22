from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.schemas.auth import UserLogin
from app.services.auth_services import create_planner_profile, create_request, login_user
from app.core.security import get_current_user,get_token

from app.core.database import get_db
from app.schemas.auth import UserRegister
from app.services.auth_services import create_user
from fastapi import FastAPI
from app.services.email_service import send_otp_email
from app.schemas.auth import OTPVerify
from app.services.auth_services import verify_otp_user
from fastapi import HTTPException
from app.schemas.auth import PlannerProfileCreate
from app.schemas.auth import RequestCreate, RequestResponse
from app.schemas.auth import PlannerInboxResponse
from app.services.auth_services import get_planner_requests
from app.services.auth_services import reject_request
from app.services.auth_services import accept_request
from app.models.revoked_token import RevokedToken





router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    return create_user(
        db=db,
        user_data=user_data
    )


@router.post("/login")
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    return login_user(
        db=db,
        user_data=user_data
    )


@router.post("/verify-otp")
def verify_otp(
    otp_data: OTPVerify,
    db: Session = Depends(get_db)
):
    return verify_otp_user(
        db=db,
        otp_data=otp_data
    )
@router.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return current_user


@router.post("/profile")
def create_profile(
    profile_data:PlannerProfileCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_planner_profile(
        db=db,
        profile_data=profile_data,
        current_user=current_user
    )


@router.post("/", response_model=RequestResponse)
def send_request(
    request: RequestCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if current_user["role"] != "user":
        raise HTTPException(
            status_code=403,
            detail="Only users can send requests"
        )

    new_request = create_request(
        db=db,
        user_id=current_user["user_id"],
        planner_id=request.planner_id,
        event_name=request.event_name
    )

    return new_request


@router.get( "/inbox",
    response_model=list[PlannerInboxResponse]
)
def planner_inbox(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_planner_requests(
        db=db,
        current_user=current_user
    )


@router.patch("/requests/{request_id}/reject")
def reject_user_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return reject_request(
        db=db,
        request_id=request_id,
        current_user=current_user
        
    )


@router.patch("/requests/{request_id}/accept")
def accept_user_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return accept_request(
        db=db,
        request_id=request_id,
        current_user=current_user
    )



@router.delete("/logout")
def logout(
    token: str = Depends(get_token),
    db: Session = Depends(get_db)
):
    existing = db.query(RevokedToken).filter(
        RevokedToken.token == token
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Already logged out"
        )

    revoked_token = RevokedToken(
        token=token
    )

    db.add(revoked_token)
    db.commit()

    return {
        "message": "Logout successful"
    }


@router.get("/test")
def test(
    authorization: str = Header(None)
):
    return {"header": authorization}