from pathlib import Path
import json


# =========================================================
# BREEDVISION AI
# PHASE 4 - COMBINED DATASET AUDIT SUMMARY
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)


def load_json(filename):
    path = (
        REPORTS_DIR
        / filename
    )

    if not path.exists():
        return None

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():
    print("=" * 72)
    print("BREEDVISION AI - PHASE 4 COMBINED AUDIT SUMMARY")
    print("=" * 72)


    # =====================================================
    # LOAD REPORTS
    # =====================================================

    iicbd = load_json(
        "iicbd_inventory.json"
    )

    bovine = load_json(
        "indian_bovine_inventory.json"
    )

    corrupt = load_json(
        "corrupt_images_summary.json"
    )

    duplicates = load_json(
        "exact_duplicates_summary.json"
    )

    quality = load_json(
        "image_quality_summary.json"
    )


    # =====================================================
    # IICBD
    # =====================================================

    print()
    print("-" * 72)
    print("1. IICBD PRIMARY CATTLE DATA")
    print("-" * 72)


    if iicbd:
        print(
            "Total images:",
            iicbd.get(
                "total_image_files_found",
                0,
            ),
        )

        print(
            "Recognized:",
            iicbd.get(
                "recognized_images",
                0,
            ),
        )

        print(
            "Unrecognized:",
            iicbd.get(
                "unrecognized_images",
                0,
            ),
        )


        print()
        print("Breed counts:")


        breed_counts = (
            iicbd.get(
                "breed_counts",
                {}
            )
        )


        for breed, count in breed_counts.items():
            if count > 0:
                print(
                    f"  {breed:<20} : {count}"
                )

    else:
        print(
            "IICBD inventory report not found."
        )


    # =====================================================
    # SECONDARY BOVINE DATASET
    # =====================================================

    print()
    print("-" * 72)
    print("2. SECONDARY INDIAN BOVINE DATA")
    print("-" * 72)


    if bovine:
        print(
            "Total images:",
            bovine.get(
                "total_images",
                0,
            ),
        )

        print(
            "Detected classes:",
            bovine.get(
                "total_detected_classes",
                0,
            ),
        )


        print()
        print("Class counts:")


        class_counts = (
            bovine.get(
                "class_counts",
                {}
            )
        )


        for class_name, count in class_counts.items():
            print(
                f"  {class_name:<30} : {count}"
            )

    else:
        print(
            "Secondary bovine inventory report not found."
        )


    # =====================================================
    # CORRUPTION AUDIT
    # =====================================================

    print()
    print("-" * 72)
    print("3. CORRUPT IMAGE AUDIT")
    print("-" * 72)


    if corrupt:
        print(
            "Total checked :",
            corrupt.get(
                "total_images_checked",
                0,
            ),
        )

        print(
            "Valid         :",
            corrupt.get(
                "valid_images",
                0,
            ),
        )

        print(
            "Corrupt       :",
            corrupt.get(
                "corrupt_images",
                0,
            ),
        )

    else:
        print(
            "Corrupt-image report not found."
        )


    # =====================================================
    # DUPLICATE AUDIT
    # =====================================================

    print()
    print("-" * 72)
    print("4. EXACT DUPLICATE AUDIT")
    print("-" * 72)


    if duplicates:
        print(
            "Total images     :",
            duplicates.get(
                "total_images",
                0,
            ),
        )

        print(
            "Unique hashes    :",
            duplicates.get(
                "unique_hashes",
                0,
            ),
        )

        print(
            "Duplicate groups :",
            duplicates.get(
                "duplicate_groups",
                0,
            ),
        )

        print(
            "Duplicate files  :",
            duplicates.get(
                "duplicate_files",
                0,
            ),
        )

    else:
        print(
            "Duplicate report not found."
        )


    # =====================================================
    # IMAGE DIMENSIONS
    # =====================================================

    print()
    print("-" * 72)
    print("5. IMAGE DIMENSION AUDIT")
    print("-" * 72)


    if quality:
        print(
            "Total images          :",
            quality.get(
                "total_images",
                0,
            ),
        )

        print(
            "Acceptable dimensions :",
            quality.get(
                "acceptable_dimensions",
                0,
            ),
        )

        print(
            "Below 224x224         :",
            quality.get(
                "too_small",
                0,
            ),
        )

        print(
            "Failed reads          :",
            quality.get(
                "failed",
                0,
            ),
        )

    else:
        print(
            "Image-quality report not found."
        )


    # =====================================================
    # FINAL JSON SUMMARY
    # =====================================================

    combined = {
        "iicbd":
            iicbd,

        "secondary_bovine":
            bovine,

        "corrupt_audit":
            corrupt,

        "duplicate_audit":
            duplicates,

        "dimension_audit":
            quality,
    }


    output_path = (
        REPORTS_DIR
        / "phase4_combined_audit.json"
    )


    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            combined,
            file,
            indent=4,
        )


    print()
    print("=" * 72)
    print("SUMMARY SAVED")
    print("=" * 72)

    print(
        output_path
    )


if __name__ == "__main__":
    main()