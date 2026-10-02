from pathlib import Path
import csv
import json
from collections import Counter


# =========================================================
# BREEDVISION AI
# PHASE 4 - SECONDARY INDIAN BOVINE DATASET INVENTORY
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_ROOT = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "indian_bovine_kaggle"
    / "extracted"
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


def normalize_folder_name(name):
    return (
        name.strip()
        .replace("_", " ")
        .replace("-", " ")
    )


def main():
    print("=" * 70)
    print("BreedVision AI - Indian Bovine Dataset Inventory")
    print("=" * 70)

    print()
    print(f"Dataset root: {DATASET_ROOT}")


    if not DATASET_ROOT.exists():
        raise FileNotFoundError(
            "\nDataset extraction folder not found:\n"
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


    if not image_files:
        raise RuntimeError(
            "No image files found in the extracted dataset."
        )


    # =====================================================
    # DETECT CLASS FOLDER
    #
    # Assumption:
    # immediate parent directory of each image is class label.
    # We are ONLY auditing here, not accepting labels yet.
    # =====================================================

    class_counts = Counter()

    extension_counts = Counter()


    for image_path in image_files:
        class_name = normalize_folder_name(
            image_path.parent.name
        )

        class_counts[class_name] += 1

        extension_counts[
            image_path.suffix.lower()
        ] += 1


    # =====================================================
    # CSV
    # =====================================================

    csv_path = (
        REPORTS_DIR
        / "indian_bovine_inventory.csv"
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
                "class_name",
                "image_count",
            ]
        )


        for class_name, count in sorted(
            class_counts.items()
        ):
            writer.writerow(
                [
                    class_name,
                    count,
                ]
            )


    # =====================================================
    # JSON
    # =====================================================

    summary = {
        "dataset":
            "Indian Bovine Breeds - Kaggle",

        "dataset_root":
            str(DATASET_ROOT),

        "total_images":
            len(image_files),

        "total_detected_classes":
            len(class_counts),

        "class_counts":
            dict(
                sorted(
                    class_counts.items()
                )
            ),

        "extension_counts":
            dict(
                sorted(
                    extension_counts.items()
                )
            ),
    }


    json_path = (
        REPORTS_DIR
        / "indian_bovine_inventory.json"
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
    print("-" * 70)
    print("CLASS COUNTS")
    print("-" * 70)


    for class_name, count in sorted(
        class_counts.items()
    ):
        print(
            f"{class_name:<30} : {count}"
        )


    print()
    print("-" * 70)

    print(
        "Total image files :",
        len(image_files),
    )

    print(
        "Detected classes  :",
        len(class_counts),
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
    # TARGET BREED CHECK
    # =====================================================

    target_breeds = [
        "Kankrej",
        "Pulikulam",
        "Rathi",
        "Sahiwal",
        "Murrah",
        "Jaffarabadi",
        "Mehsana",
        "Surti",
        "Banni",
    ]


    print()
    print("=" * 70)
    print("TARGET BREED CHECK")
    print("=" * 70)


    normalized_classes = {
        key.lower(): (
            key,
            value,
        )
        for key, value in class_counts.items()
    }


    for breed in target_breeds:
        match = normalized_classes.get(
            breed.lower()
        )


        if match:
            print(
                f"[FOUND]   {breed:<15} : {match[1]}"
            )

        else:
            print(
                f"[MISSING] {breed}"
            )


    print()
    print(
        "Inventory completed."
    )


if __name__ == "__main__":
    main()