from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas import UserBase, UserResponse, UserLogin
from backend.models import User
from backend.utils import verify_password, get_password_hash

user_router = APIRouter()

@user_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserBase, db: Session = Depends(get_db)):
    print("Registering user:")
    print(user)
    try:
        # Check if username exists
        if (db.query(User).filter(User.username == user.username).first()) or (db.query(User).filter(User.email == user.email).first()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Create new user with hashed password
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)  # Refresh to get the updated user with ID
        
        # Create response that matches UserResponse schema
        return UserResponse(
            content="User registered successfully",
            id=db_user.id,
            username=db_user.username,
            email=db_user.email
        )
        
    except Exception as e:
        db.rollback()  # Rollback the transaction on any error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@user_router.post("/login")
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    # Find user by username
    print("Logging in user:")
    print(user_credentials)
    user = db.query(User).filter(User.username == user_credentials.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid username or password"
        )
    
    return {"message": "Login successful", "user_id": user.id}