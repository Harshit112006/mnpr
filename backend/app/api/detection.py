from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError


router = APIRouter(
    prefix="/api",
    tags=["Detection"],
)


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/detect")
async def detect_animal(
    file: UploadFile = File(...)
):
    # -----------------------------
    # 1. Validate file type
    # -----------------------------

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Please upload JPG, PNG or WEBP."
            ),
        )

    # -----------------------------
    # 2. Read uploaded file
    # -----------------------------

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # -----------------------------
    # 3. Validate file size
    # -----------------------------

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image must be smaller than 10 MB.",
        )

    # -----------------------------
    # 4. Decode real image
    # -----------------------------

    try:
        image = Image.open(
            BytesIO(file_bytes)
        )

        image.load()

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid image.",
        )

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unable to process uploaded image.",
        )

    # -----------------------------
    # 5. Extract image information
    # -----------------------------

    width, height = image.size

    image_format = (
        image.format
        if image.format
        else "UNKNOWN"
    )

    size_mb = round(
        len(file_bytes) / (1024 * 1024),
        2,
    )

    # -----------------------------
    # 6. Temporary API response
    # -----------------------------
    # ML prediction will be added later.

    return {
        "success": True,

        "message": (
            "Image received successfully. "
            "ML inference is not connected yet."
        ),

        "image": {
            "filename": file.filename,
            "content_type": file.content_type,
            "format": image_format,
            "mode": image.mode,
            "width": width,
            "height": height,
            "size_bytes": len(file_bytes),
            "size_mb": size_mb,
        },

        "prediction": None,
    }