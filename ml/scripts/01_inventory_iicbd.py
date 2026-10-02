from pathlib import Path
import csv
import json


# =========================================================
# BREEDVISION AI
# PHASE 4 - IICBD RAW DATASET INVENTORY
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_ROOT = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "iicbd_2026"
)

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)


EXPECTED_BREEDS = [
    "Bargur",
    "Gir",
    "Hallikar",
    "Kankrej",
    "Ongole",
    "Pulikulam",
    "Rathi",
    "Sahiwal",
    "Tharparkar",
]


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
}


def normalize_name(value):
    return (
        value
        .strip()
        .lower()
        .replace("_", "")
        .replace("-", "")
        .replace(" ", "")
    )


BREED_LOOKUP = {
    normalize_name(breed): breed
    for breed in EXPECTED_BREEDS
}


def detect_breed_from_path(file_path):
    for part in file_path.parts:
        normalized = normalize_name(part)

        if normalized in BREED_LOOKUP:
            return BREED_LOOKUP[normalized]

    return None


def main():
    print("=" * 65)
    print("BreedVision AI - IICBD Raw Dataset Inventory")
    print("=" * 65)

    print()
    print(f"Dataset path: {DATASET_ROOT}")


    if not DATASET_ROOT.exists():
        raise FileNotFoundError(
            "\nIICBD dataset folder was not found.\n"
            "Expected location:\n"
            f"{DATASET_ROOT}"
        )


    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    image_files = [
        path
        for path in DATASET_ROOT.rglob("*")
        if (
            path.is_file()
            and path.suffix.lower()
            in IMAGE_EXTENSIONS
        )
    ]


    counts = {
        breed: 0
        for breed in EXPECTED_BREEDS
    }


    unknown_files = []


    extension_counts = {}


    for image_path in image_files:
        extension = (
            image_path
            .suffix
            .lower()
        )

        extension_counts[extension] = (
            extension_counts.get(
                extension,
                0,
            )
            + 1
        )


        breed = detect_breed_from_path(
            image_path
        )


        if breed is None:
            unknown_files.append(
                image_path
            )

            continue


        counts[breed] += 1


    # =====================================================
    # CSV REPORT
    # =====================================================

    csv_path = (
        REPORTS_DIR
        / "iicbd_inventory.csv"
    )


    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.writer(
            csv_file
        )

        writer.writerow(
            [
                "breed",
                "image_count",
            ]
        )


        for breed in EXPECTED_BREEDS:
            writer.writerow(
                [
                    breed,
                    counts[breed],
                ]
            )


    # =====================================================
    # JSON SUMMARY
    # =====================================================

    summary = {
        "dataset":
            "IICBD 2026",

        "dataset_root":
            str(DATASET_ROOT),

        "expected_breeds":
            EXPECTED_BREEDS,

        "total_image_files_found":
            len(image_files),

        "recognized_images":
            sum(
                counts.values()
            ),

        "unrecognized_images":
            len(
                unknown_files
            ),

        "breed_counts":
            counts,

        "extension_counts":
            extension_counts,
    }


    json_path = (
        REPORTS_DIR
        / "iicbd_inventory.json"
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
    # TERMINAL OUTPUT
    # =====================================================

    print()
    print("-" * 65)
    print("BREED COUNTS")
    print("-" * 65)


    for breed, count in counts.items():
        print(
            f"{breed:<15} : {count}"
        )


    print()
    print("-" * 65)

    print(
        "Total image files found :",
        len(image_files),
    )

    print(
        "Recognized images        :",
        sum(
            counts.values()
        ),
    )

    print(
        "Unrecognized images      :",
        len(
            unknown_files
        ),
    )


    print()
    print("Extensions:")

    for extension, count in sorted(
        extension_counts.items()
    ):
        print(
            f"  {extension:<8} : {count}"
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


    # =====================================================
    # BASIC VALIDATION
    # =====================================================

    missing_breeds = [
        breed
        for breed, count
        in counts.items()
        if count == 0
    ]


    print()
    print("=" * 65)
    print("BASIC VALIDATION")
    print("=" * 65)


    if missing_breeds:
        print(
            "WARNING: No images found for:"
        )

        for breed in missing_breeds:
            print(
                f"  - {breed}"
            )

    else:
        print(
            "All 9 expected breed folders/classes were detected."
        )


    if len(image_files) == 9598:
        print(
            "Image count matches the published IICBD total: 9,598."
        )

    else:
        print(
            "NOTE: Local image count differs from the published "
            "9,598-image total."
        )

        print(
            "Do not modify anything yet. "
            "We will inspect the reason in the next audit step."
        )


    print()
    print(
        "Inventory completed."
    )


if __name__ == "__main__":
    main()