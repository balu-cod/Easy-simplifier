from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from contextlib import asynccontextmanager

from config.settings import settings
from database.postgresql import init_db
from database.mongodb import init_mongo
from routers import auth, images, games, feedback, users, chat
from middleware.auth import get_current_user
from services.ai_service import AIService

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await init_mongo()
    print("🚀 AI Image Processor API Started Successfully!")
    yield
    # Shutdown
    print("👋 AI Image Processor API Shutting Down...")

app = FastAPI(
    title="AI Image Processor API",
    description="Sophisticated AI-powered image processing with interactive gaming",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(images.router, prefix="/api/images", tags=["Image Processing"])
app.include_router(games.router, prefix="/api/games", tags=["Gaming"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to AI Image Processor API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "ai_service": "available"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )