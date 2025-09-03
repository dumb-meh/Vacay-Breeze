import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.services.ai_suggestion.ai_suggestion_route import router as ai_suggestion_router
from app.services.regenerate_plan.regenerate_plan_route import router as regenerate_plan_router


app = FastAPI(
    title="Study Buddy AI",
    description="An AI-powered learning companion for ADHD-friendly study tools",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_suggestion_router, tags=["AI Suggestion"])
app.include_router(regenerate_plan_router, tags=["Regenerate Plan"])


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health checks"""
    return {
        "message": "Welcome to the Vacay Breeze AI!",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Docker/monitoring"""
    return {
        "status": "healthy",
        "service": "Vacay Breeze AI"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=9013, 
        reload=True
    )