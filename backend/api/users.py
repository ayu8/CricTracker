from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas import UserBase, UserResponse, Token
from backend.models import User
from backend.utils import verify_password, get_password_hash
from . import jwt

user_router = APIRouter()

@user_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserBase, db: Session = Depends(get_db)):
    try:
        # Check if username exists
        if (db.query(User).filter(User.username == user.username).first()) or (db.query(User).filter(User.email == user.email).first()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
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

# JSON-based login (for frontend fetch requests) - THIS IS WHAT YOUR FRONTEND NEEDS
@user_router.post("/login", response_model=Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Find user by username
    user = db.query(User).filter(User.username == user_credentials.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid username or password"
        )
    
    # Create access token
    access_token = jwt.create_access_token(data={"user_id": user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}

# OAuth2 form-based login (for Swagger UI and OAuth2 compatibility)
@user_router.post("/login/form", response_model=Token)
async def login_form(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with form data (for Swagger UI)"""
    user = db.query(User).filter(User.username == user_credentials.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid username or password"
        )
    
    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid username or password"
        )
    
    access_token = jwt.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}