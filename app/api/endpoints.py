from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.base import User, Role
from app.schemas import UserCreate, UserLogin, UserOut
from typing import List

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "welcome to vstore api"}

# for simple front
@router.get("/users/public")
async def get_public_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "role_name": u.role.name
        }
        for u in users
    ]


# for admin-panel
@router.get("/admin/users")
async def get_admin_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "phone": u.phone,
            "role_name": u.role.name,
            "is_banned": u.is_banned
        }
        for u in users
    ]

@router.post("/auth/register", response_model=UserOut)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user_in.username) | (User.email == user_in.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username or email already registered"
        )

    # get user's role
    role = db.query(Role).filter(Role.name == "User").first()

    # create new user
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        phone=user_in.phone,
        role_id=role.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # construct UserOut manually to include role_name
    return UserOut(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        phone=new_user.phone,
        role_name=new_user.role.name
    )

@router.post("/auth/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or user.password != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid username or password"
        )

    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="this account has been banned"
        )

    return {
        "message": "login successful",
        "username": user.username,
        "role": user.role.name,
        "permissions": {
            "can_buy": user.role.can_buy,
            "can_message": user.role.can_message,
            "can_ban": user.role.can_ban
        }
    }

@router.post("/admin/users/{user_id}/toggle-ban")
async def toggle_user_ban(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )

    user.is_banned = not user.is_banned
    db.commit()
    db.refresh(user)

    status_text = "banned" if user.is_banned else "unbanned"
    return {
        "message": f"user {user.username} has been {status_text}", 
        "is_banned": user.is_banned
    }