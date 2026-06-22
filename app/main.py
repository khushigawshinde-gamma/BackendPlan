from fastapi import FastAPI

from app.core.database import engine, Base

from app.models.User import User
from app.routes.auth import router as auth_router
from app.routes.auth import router as request_router
from app.models.revoked_token import RevokedToken


Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router)



@app.get("/")
def home():
    return {"message": "Planners.in Backend Running"}

app.include_router(
    request_router,
    prefix="/requests",
    tags=["Requests"]
)