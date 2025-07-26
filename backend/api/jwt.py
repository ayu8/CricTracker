from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

auth_router = APIRouter(tags=["Authentication"])

@auth_router.get("/login")
async def login():
    return {"message": "Login endpoint"}