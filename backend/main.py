from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from .api.v1.api import api_router
# from .core.config import settings
from .database import Base, engine
from .models import User
from .api.users import user_router 

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CricTracler",
    description="A cricket statistics tracking API",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Adjust for your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(user_router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Welcome to CricTracker API"}

print("CricTracker API is running...")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}