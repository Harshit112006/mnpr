from pathlib import Path
import csv
import json
from collections import defaultdict


# =========================================================
# BREEDVISION AI
# PHASE 4 - HARD EXCLUSION MANIFEST
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORTS_DIR = PROJECT_ROOT / "reports"


CORRUPT_CSV = (
    REPORTS_DIR
    / "corrupt_images.csv"
)

QUALITY_CSV = (
    REPORTS_DIR
    / "image_quality_audit.csv"
)

CONFLICT_CSV = (
    REPORTS_DIR
    / "duplicate_label_conflicts.csv"
)


OUTPUT_CSV = (
    REPORTS_DIR
    / "hard_exclusion_manifest.csv"
)

OUTPUT_JSON = (
    REPORTS_DIR
    / "hard_exclusion_manifest.json"
)

SUMMARY_JSON = (
    REPORTS_DIR
    / "hard_exclusion_summary.json"
)


def normalize_path(path_string):
    return str(
        Path(path_string)
        .resolve()
    )


def main():

    print("=" * 80)
    print("BREEDVISION AI - HARD EXCLUSION MANIFEST")
    print("=" * 80)


    exclusions = defaultdict(
        lambda: {
            "reasons": set(),
            "details": set(),
        }
    )


    # =====================================================
    # 1. CORRUPT IMAGES
    # =====================================================

    corrupt_count = 0


    if CORRUPT_CSV.exists():

        with CORRUPT_CSV.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:

            reader = csv.DictReader(file)


            for row in reader:

                path = (
                    row.get(
                        "path",
                        ""
                    )
                    .strip()
                )


                if not path:
                    continue


                path = normalize_path(
                    path
                )


                exclusions[
                    path
                ][
                    "reasons"
                ].add(
                    "corrupt_or_unreadable"
                )


                error = (
                    row.get(
                        "error",
                        ""
                    )
                    .strip()
                )


                if error:

                    exclusions[
                        path
                    ][
                        "details"
                    ].add(
                        error
                    )


                corrupt_count += 1


    # =====================================================
    # 2. TOO-SMALL IMAGES
    # =====================================================

    small_count = 0


    if QUALITY_CSV.exists():

        with QUALITY_CSV.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:

            reader = csv.DictReader(file)


            for row in reader:

                too_small = (
                    row.get(
                        "too_small",
                        ""
                    )
                    .strip()
                    .lower()
                )


                if too_small not in {
                    "true",
                    "1",
                    "yes",
                }:
                    continue


                path = (
                    row.get(
                        "path",
                        ""
                    )
                    .strip()
                )


                if not path:
                    continue


                path = normalize_path(
                    path
                )


                exclusions[
                    path
                ][
                    "reasons"
                ].add(
                    "below_minimum_dimensions"
                )


                width = (
                    row.get(
                        "width",
                        ""
                    )
                    .strip()
                )

                height = (
                    row.get(
                        "height",
                        ""
                    )
                    .strip()
                )


                exclusions[
                    path
                ][
                    "details"
                ].add(
                    f"{width}x{height}"
                )


                small_count += 1


    # =====================================================
    # 3. CROSS-CLASS DUPLICATE CONFLICTS
    # =====================================================

    conflict_rows = 0

    conflict_groups = set()


    if CONFLICT_CSV.exists():

        with CONFLICT_CSV.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:

            reader = csv.DictReader(file)


            for row in reader:

                status = (
                    row.get(
                        "status",
                        ""
                    )
                    .strip()
                )


                if status != "cross_class_conflict":
                    continue


                path = (
                    row.get(
                        "path",
                        ""
                    )
                    .strip()
                )


                sha256 = (
                    row.get(
                        "sha256",
                        ""
                    )
                    .strip()
                )


                labels = (
                    row.get(
                        "group_labels",
                        ""
                    )
                    .strip()
                )


                if not path:
                    continue


                path = normalize_path(
                    path
                )


                exclusions[
                    path
                ][
                    "reasons"
                ].add(
                    "cross_class_duplicate_conflict"
                )


                if labels:

                    exclusions[
                        path
                    ][
                        "details"
                    ].add(
                        f"conflicting labels: {labels}"
                    )


                if sha256:

                    conflict_groups.add(
                        sha256
                    )


                conflict_rows += 1


    # =====================================================
    # BUILD FINAL MANIFEST
    # =====================================================

    manifest_rows = []


    for path, info in sorted(
        exclusions.items()
    ):

        reasons = sorted(
            info[
                "reasons"
            ]
        )


        details = sorted(
            info[
                "details"
            ]
        )


        manifest_rows.append(
            {
                "path":
                    path,

                "reason":
                    " | ".join(
                        reasons
                    ),

                "details":
                    " | ".join(
                        details
                    ),

                "exclude_from_processed":
                    True,
            }
        )


    # =====================================================
    # CSV
    # =====================================================

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        fieldnames = [
            "path",
            "reason",
            "details",
            "exclude_from_processed",
        ]


        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            manifest_rows
        )


    # =====================================================
    # JSON
    # =====================================================

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            manifest_rows,
            file,
            indent=4,
        )


    # =====================================================
    # SUMMARY
    # =====================================================

    reason_counts = defaultdict(
        int
    )


    for row in manifest_rows:

        for reason in (
            row[
                "reason"
            ].split(
                " | "
            )
        ):

            if reason:

                reason_counts[
                    reason
                ] += 1


    summary = {
        "unique_excluded_images":
            len(
                manifest_rows
            ),

        "corrupt_rows_found":
            corrupt_count,

        "small_image_rows_found":
            small_count,

        "cross_class_conflict_rows_found":
            conflict_rows,

        "cross_class_conflict_groups":
            len(
                conflict_groups
            ),

        "unique_image_counts_by_reason":
            dict(
                sorted(
                    reason_counts.items()
                )
            ),

        "policy": {
            "raw_data_modified":
                False,

            "corrupt_images":
                "Exclude",

            "images_below_224x224":
                "Exclude",

            "cross_class_exact_duplicates":
                "Exclude all copies pending manual review",

            "same_class_exact_duplicates":
                (
                    "Not handled here. "
                    "Processed-dataset builder will retain one eligible copy."
                ),
        },
    }


    with SUMMARY_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
        )


    # =====================================================
    # TERMINAL OUTPUT
    # =====================================================

    print()

    print(
        "Unique images excluded          :",
        len(
            manifest_rows
        ),
    )

    print(
        "Corrupt-image rows              :",
        corrupt_count,
    )

    print(
        "Below-minimum-dimension rows    :",
        small_count,
    )

    print(
        "Cross-class conflict rows       :",
        conflict_rows,
    )

    print(
        "Cross-class conflict groups     :",
        len(
            conflict_groups
        ),
    )


    print()
    print("-" * 80)
    print("UNIQUE EXCLUSIONS BY REASON")
    print("-" * 80)


    for reason, count in sorted(
        reason_counts.items()
    ):

        print(
            f"{reason:<40} : {count}"
        )


    print()

    print(
        "CSV manifest :",
        OUTPUT_CSV
    )

    print(
        "JSON manifest:",
        OUTPUT_JSON
    )

    print(
        "Summary      :",
        SUMMARY_JSON
    )


    print()
    print(
        "No raw images were modified or deleted."
    )


if __name__ == "__main__":
    main()