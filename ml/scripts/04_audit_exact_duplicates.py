from pathlib import Path
import csv
import hashlib
import json
from collections import defaultdict

from tqdm import tqdm


# =========================================================
# BREEDVISION AI
# PHASE 4 - EXACT DUPLICATE IMAGE AUDIT
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


def calculate_sha256(
    file_path,
):
    sha256 = hashlib.sha256()

    with file_path.open(
        "rb"
    ) as file:
        while True:
            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            sha256.update(
                chunk
            )

    return sha256.hexdigest()


def main():
    print("=" * 70)
    print("BreedVision AI - Exact Duplicate Audit")
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


    hash_groups = defaultdict(
        list
    )


    for image_path in tqdm(
        image_files,
        desc="Hashing images",
    ):
        try:
            image_hash = (
                calculate_sha256(
                    image_path
                )
            )

            hash_groups[
                image_hash
            ].append(
                image_path
            )

        except OSError as error:
            print(
                f"Unable to hash {image_path}: {error}"
            )


    duplicate_groups = {
        image_hash: paths

        for image_hash, paths
        in hash_groups.items()

        if len(paths) > 1
    }


    duplicate_rows = []


    for (
        image_hash,
        paths,
    ) in duplicate_groups.items():

        keeper = paths[0]


        for duplicate in paths[1:]:
            duplicate_rows.append(
                {
                    "sha256":
                        image_hash,

                    "keeper":
                        str(
                            keeper
                        ),

                    "duplicate":
                        str(
                            duplicate
                        ),
                }
            )


    # =====================================================
    # CSV
    # =====================================================

    csv_path = (
        REPORTS_DIR
        / "exact_duplicates.csv"
    )


    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "sha256",
                "keeper",
                "duplicate",
            ],
        )

        writer.writeheader()

        writer.writerows(
            duplicate_rows
        )


    # =====================================================
    # JSON
    # =====================================================

    duplicate_files_count = sum(
        len(paths) - 1

        for paths
        in duplicate_groups.values()
    )


    summary = {
        "total_images":
            len(image_files),

        "unique_hashes":
            len(hash_groups),

        "duplicate_groups":
            len(
                duplicate_groups
            ),

        "duplicate_files":
            duplicate_files_count,
    }


    json_path = (
        REPORTS_DIR
        / "exact_duplicates_summary.json"
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
    print("DUPLICATE RESULT")
    print("=" * 70)


    print(
        "Total images          :",
        len(image_files),
    )

    print(
        "Unique files          :",
        len(hash_groups),
    )

    print(
        "Duplicate groups      :",
        len(
            duplicate_groups
        ),
    )

    print(
        "Extra duplicate files :",
        duplicate_files_count,
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


    print()
    print(
        "No files were deleted."
    )


if __name__ == "__main__":
    main()