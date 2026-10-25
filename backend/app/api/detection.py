from io import BytesIO

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from PIL import (
    Image,
    UnidentifiedImageError,
)

from starlette.concurrency import (
    run_in_threadpool,
)

from app.services.ml.inference_pipeline import (
    get_inference_pipeline,
)

from app.services.ml.paths import (
    validate_ml_paths,
)


router = APIRouter(
    prefix="/api",
    tags=["Detection"],
)


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = (
    10
    *
    1024
    *
    1024
)



@router.get("/ml/health")
async def ml_health():
    path_status = validate_ml_paths()

    if not path_status["ready"]:
        return {
            "status": "not_ready",
            "paths": path_status,
        }

    return {
        "status": "files_ready",
        "paths": path_status,
        "models_loaded": False,
        "note": (
            "Models load lazily on the first "
            "/api/detect request to conserve RAM."
        ),
    }



@router.post(
    "/detect"
)
async def detect_animal(
    file: UploadFile = File(...)
):

    # =====================================================
    # FILE TYPE
    # =====================================================

    if (
        file.content_type
        not in
        ALLOWED_CONTENT_TYPES
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Please upload JPG, PNG or WEBP."
            ),
        )


    # =====================================================
    # READ
    # =====================================================

    file_bytes = await file.read()

    if not file_bytes:

        raise HTTPException(
            status_code=400,
            detail=(
                "Uploaded file is empty."
            ),
        )


    if len(
        file_bytes
    ) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=400,
            detail=(
                "Image must be smaller than 10 MB."
            ),
        )


    # =====================================================
    # DECODE
    # =====================================================

    try:

        image = Image.open(
            BytesIO(
                file_bytes
            )
        )

        image.load()

    except UnidentifiedImageError:

        raise HTTPException(
            status_code=400,
            detail=(
                "Uploaded file is not a valid image."
            ),
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unable to process uploaded image."
            ),
        )


    width, height = (
        image.size
    )

    original_mode = (
        image.mode
    )

    image_format = (
        image.format
        if image.format
        else "UNKNOWN"
    )

    size_mb = round(
        len(
            file_bytes
        )
        /
        (
            1024
            *
            1024
        ),
        2,
    )

# Resize large images to reduce inference memory usage
image.thumbnail(
    (1280, 1280),
    Image.Resampling.LANCZOS,
)


    # =====================================================
    # ML INFERENCE
    # =====================================================

    try:

        pipeline = await run_in_threadpool(
            get_inference_pipeline
        )

        inference = await run_in_threadpool(
            pipeline.predict,
            image.convert(
                "RGB"
            ),
        )

    except Exception as error:

        raise HTTPException(
            status_code=503,
            detail=(
                "BreedVision ML inference "
                f"is unavailable: {error}"
            ),
        )


    pipeline_status = (
        inference[
            "pipeline_status"
        ]
    )

    if (
        pipeline_status
        ==
        "no_bovine"
    ):

        message = (
            "Image processed successfully, "
            "but no bovine was detected."
        )

    elif (
        pipeline_status
        ==
        "unknown"
    ):

        message = (
            "Bovine detected, but the breed "
            "could not be identified reliably."
        )

    else:

        message = (
            "Bovine detected and breed "
            "analysis completed successfully."
        )


    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "success":
            True,

        "message":
            message,

        "image": {
            "filename":
                file.filename,

            "content_type":
                file.content_type,

            "format":
                image_format,

            "mode":
                original_mode,

            "width":
                width,

            "height":
                height,

            "size_bytes":
                len(
                    file_bytes
                ),

            "size_mb":
                size_mb,
        },

        "pipeline_status":
            pipeline_status,

        "bovine":
            inference[
                "bovine"
            ],

        "prediction":
            inference[
                "prediction"
            ],
    }