from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "welcome to vstore api"}

@router.get("/health")
async def health_check():
    return {"status": "ok"}
