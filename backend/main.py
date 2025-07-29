from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import Base, engine
from .models import User, Match                  # necessary to import here for creating tables
from .api.users import user_router
from .api.matches import match_router
from .api.bat_stats import batsman_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CricTracker",
    description="A cricket statistics tracking API",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

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
app.include_router(match_router, prefix="/api/v1/matches", tags=["matches"])
app.include_router(batsman_router, prefix="/api/v1/bat_stats", tags=["batting_stats"])
  
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy"}