import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.services.affirmation.affirmation_route import router as affirmation_router
from app.services.empowerment.empowerment_route import router as empowerment_router
from app.services.flashcard_quiz.flashcard_quiz_route import router as flashcard_quiz_router
from app.services.mnemonic.mnemonic_route import router as mnemonic_router
from app.services.story.story_route import router as story_router
from app.services.summary.summary_route import router as summary_router
from app.services.task_suggestion.task_suggestion_route import router as task_suggestion_router

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

app.include_router(affirmation_router, tags=["Affirmation"])
app.include_router(empowerment_router, tags=["Empowerment"])
app.include_router(flashcard_quiz_router, tags=["Flashcard Quiz"])
app.include_router(mnemonic_router, tags=["Mnemonic"])
app.include_router(story_router, tags=["Story"])
app.include_router(summary_router, tags=["Summary"])
app.include_router(task_suggestion_router, tags=["Task Suggestion"])

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health checks"""
    return {
        "message": "Welcome to the Study Buddy AI!",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Docker/monitoring"""
    return {
        "status": "healthy",
        "service": "Study Buddy AI"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=9013, 
        reload=True
    )