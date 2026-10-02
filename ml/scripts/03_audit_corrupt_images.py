from pathlib import Path
import csv
import json

from PIL import Image, UnidentifiedImageError
from tqdm import tqdm


# =========================================================
# BREEDVISION AI
# PHASE 4 - CORRUPT / UNREADABLE IMAGE AUDIT
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_ROOT = (
    PROJECT_ROOT
    / "data"
    / "raw"
)

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
}


def get_source_name(path):
    relative = path.relative_to(
        RAW_ROOT
    )

    return relative.parts[0]


def main():
    print("=" * 70)
    print("BreedVision AI - Corrupt Image Audit")
    print("=" * 70)

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    image_files = [
        path
        for path in RAW_ROOT.rglob("*")
        if (
            path.is_file()
            and path.suffix.lower()
            in IMAGE_EXTENSIONS
        )
    ]


    print()
    print(
        f"Images discovered: {len(image_files)}"
    )


    corrupt_images = []

    valid_count = 0


    for image_path in tqdm(
        image_files,
        desc="Checking images",
    ):
        try:
            with Image.open(
                image_path
            ) as image:
                image.verify()


            # Open again because verify()
            # invalidates the first image object.
            with Image.open(
                image_path
            ) as image:
                image.load()


            valid_count += 1


        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
            SyntaxError,
        ) as error:
            corrupt_images.append(
                {
                    "source":
                        get_source_name(
                            image_path
                        ),

                    "path":
                        str(
                            image_path
                        ),

                    "filename":
                        image_path.name,

                    "error":
                        str(
                            error
                        ),
                }
            )


    # =====================================================
    # CSV REPORT
    # =====================================================

    csv_path = (
        REPORTS_DIR
        / "corrupt_images.csv"
    )


    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "source",
                "path",
                "filename",
                "error",
            ],
        )

        writer.writeheader()

        writer.writerows(
            corrupt_images
        )


    # =====================================================
    # JSON SUMMARY
    # =====================================================

    summary = {
        "total_images_checked":
            len(image_files),

        "valid_images":
            valid_count,

        "corrupt_images":
            len(
                corrupt_images
            ),

        "corrupt_report":
            str(
                csv_path
            ),
    }


    json_path = (
        REPORTS_DIR
        / "corrupt_images_summary.json"
    )


    with json_path.open(
        "w",
        encoding="utf-8",
    ) as json_file:
        json.dump(
            summary,
            json_file,
            indent=4,
        )


    # =====================================================
    # OUTPUT
    # =====================================================

    print()
    print("=" * 70)
    print("AUDIT RESULT")
    print("=" * 70)

    print(
        "Total images checked :",
        len(image_files),
    )

    print(
        "Valid images         :",
        valid_count,
    )

    print(
        "Corrupt images       :",
        len(
            corrupt_images
        ),
    )

    print()
    print(
        "CSV report :",
        csv_path,
    )

    print(
        "JSON report:",
        json_path,
    )


    if corrupt_images:
        print()
        print(
            "IMPORTANT:"
        )

        print(
            "Corrupt images were detected."
        )

        print(
            "Do NOT delete files from data/raw."
        )

        print(
            "They will be excluded when the processed dataset is created."
        )

    else:
        print()
        print(
            "No corrupt images detected."
        )


if __name__ == "__main__":
    main()