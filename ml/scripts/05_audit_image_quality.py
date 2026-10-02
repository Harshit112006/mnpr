from pathlib import Path
import csv
import json

from PIL import Image
from tqdm import tqdm


# =========================================================
# BREEDVISION AI
# PHASE 4 - IMAGE QUALITY / DIMENSION AUDIT
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


MIN_WIDTH = 224
MIN_HEIGHT = 224


def main():
    print("=" * 70)
    print("BreedVision AI - Image Dimension Audit")
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


    rows = []

    small_images = 0

    valid_images = 0

    failed_images = 0


    for image_path in tqdm(
        image_files,
        desc="Reading dimensions",
    ):
        try:
            with Image.open(
                image_path
            ) as image:

                width, height = (
                    image.size
                )


                is_too_small = (
                    width < MIN_WIDTH
                    or
                    height < MIN_HEIGHT
                )


                if is_too_small:
                    small_images += 1

                else:
                    valid_images += 1


                rows.append(
                    {
                        "path":
                            str(
                                image_path
                            ),

                        "width":
                            width,

                        "height":
                            height,

                        "megapixels":
                            round(
                                (
                                    width
                                    *
                                    height
                                )
                                /
                                1_000_000,
                                3,
                            ),

                        "too_small":
                            is_too_small,
                    }
                )


        except Exception as error:
            failed_images += 1

            rows.append(
                {
                    "path":
                        str(
                            image_path
                        ),

                    "width":
                        None,

                    "height":
                        None,

                    "megapixels":
                        None,

                    "too_small":
                        None,

                    "error":
                        str(
                            error
                        ),
                }
            )


    csv_path = (
        REPORTS_DIR
        / "image_quality_audit.csv"
    )


    fieldnames = [
        "path",
        "width",
        "height",
        "megapixels",
        "too_small",
        "error",
    ]


    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=
                fieldnames,
            extrasaction=
                "ignore",
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


    summary = {
        "minimum_width":
            MIN_WIDTH,

        "minimum_height":
            MIN_HEIGHT,

        "total_images":
            len(
                image_files
            ),

        "acceptable_dimensions":
            valid_images,

        "too_small":
            small_images,

        "failed":
            failed_images,
    }


    json_path = (
        REPORTS_DIR
        / "image_quality_summary.json"
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


    print()
    print("=" * 70)
    print("QUALITY RESULT")
    print("=" * 70)


    print(
        "Total images          :",
        len(image_files),
    )

    print(
        "Acceptable dimensions :",
        valid_images,
    )

    print(
        "Below 224x224         :",
        small_images,
    )

    print(
        "Unable to read        :",
        failed_images,
    )


    print()
    print(
        "CSV report :",
        csv_path
    )

    print(
        "JSON report:",
        json_path
    )


if __name__ == "__main__":
    main()