from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from fastapi import HTTPException, Header, status,Depends
from app.models.revoked_token import RevokedToken
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.revoked_token import RevokedToken


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {"exp": expire}
    )

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

def verify_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload


    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    

def get_token(token: str = Header(...)):
    return token



def get_current_user(
    token: str = Depends(get_token),
    db: Session = Depends(get_db)
):

    revoked = db.query(RevokedToken).filter(
        RevokedToken.token == token
    ).first()


    if revoked:
        raise HTTPException(
            status_code=401,
            detail="Session expired. Please login again"
        )


    payload = verify_access_token(token)

    return payload


