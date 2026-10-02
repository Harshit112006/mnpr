import io
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError


router = APIRouter(
    prefix="/api",
    tags=["Detection"],
)


BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


@router.post("/detect")
async def upload_detection_image(
    image: UploadFile = File(...)
):
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG and WEBP images are supported.",
        )

    file_bytes = await image.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty.",
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image size must be less than 10 MB.",
        )

    try:
        pil_image = Image.open(
            io.BytesIO(file_bytes)
        )

        pil_image.load()

        width, height = pil_image.size

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

    extension = ALLOWED_TYPES[
        image.content_type
    ]

    detection_id = str(
        uuid.uuid4()
    )

    saved_filename = (
        f"{detection_id}{extension}"
    )

    saved_path = (
        UPLOAD_DIR /
        saved_filename
    )

    saved_path.write_bytes(
        file_bytes
    )

    return {
        "success": True,
        "message": "Image uploaded successfully.",
        "detection_id": detection_id,
        "original_filename": image.filename,
        "saved_filename": saved_filename,
        "content_type": image.content_type,
        "size_bytes": len(file_bytes),
        "width": width,
        "height": height,
        "upload_status": "stored",
        "model_status": "not_connected",
        "prediction": None,
    }