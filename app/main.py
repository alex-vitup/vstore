from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.admin import setup_admin
from app.models.base import Base, User, Role
from app.core.config import settings
from app.core.db import engine, SessionLocal

# init fastApi
app = FastAPI(title=settings.PROJECT_NAME)

# db setup
# Base.metadata.create_all(bind=engine)

# api routes
app.include_router(api_router, prefix="/api/v1")

# admin setup
setup_admin(app)

@app.get("/")
async def read_root():
    return {"message": "vstore is running. go to /admin"}
