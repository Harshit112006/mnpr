from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.detection import router as detection_router


app = FastAPI(
    title="BreedVision AI API",
    description=(
        "Backend API for BreedVision AI "
        "bovine breed identification platform."
    ),
    version="0.2.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    detection_router
)


@app.get("/")
def root():
    return {
        "application": "BreedVision AI",
        "status": "running",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "BreedVision AI Backend",
        "version": "0.2.0",
    }