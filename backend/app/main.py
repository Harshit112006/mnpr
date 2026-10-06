import os

from fastapi import (
    FastAPI,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.api.assistant import (
    router as assistant_router,
)

from app.api.detection import (
    router as detection_router,
)


DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
]


def get_cors_origins():

    raw_origins = os.getenv(
        "CORS_ORIGINS",
        "",
    ).strip()


    if not raw_origins:

        return (
            DEFAULT_CORS_ORIGINS
            .copy()
        )


    return [

        origin
        .strip()
        .rstrip("/")

        for origin
        in raw_origins.split(",")

        if origin.strip()
    ]


app = FastAPI(
    title=
        "BreedVision AI API",

    description=(
        "Backend API for BreedVision AI bovine "
        "breed identification and AI Assistant."
    ),

    version=
        "0.2.0",
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=
        get_cors_origins(),

    allow_credentials=
        True,

    allow_methods=[
        "*",
    ],

    allow_headers=[
        "*",
    ],
)


app.include_router(
    detection_router
)


app.include_router(
    assistant_router
)


@app.get("/")
def root():

    return {
        "application":
            "BreedVision AI",

        "status":
            "running",
    }


@app.get(
    "/api/health"
)
def health_check():

    return {
        "status":
            "healthy",

        "service":
            "BreedVision AI Backend",

        "version":
            "0.2.0",
    }