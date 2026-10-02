from pathlib import Path
import csv
import json
from collections import defaultdict


# =========================================================
# BREEDVISION AI
# PHASE 4 - CROSS-CLASS EXACT DUPLICATE AUDIT
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_ROOT = PROJECT_ROOT / "data" / "raw"

REPORTS_DIR = PROJECT_ROOT / "reports"


DUPLICATES_CSV = (
    REPORTS_DIR
    / "exact_duplicates.csv"
)

LABEL_REVIEW_CSV = (
    REPORTS_DIR
    / "label_normalization_review.csv"
)


OUTPUT_CSV = (
    REPORTS_DIR
    / "duplicate_label_conflicts.csv"
)

OUTPUT_JSON = (
    REPORTS_DIR
    / "duplicate_label_conflicts_summary.json"
)


IICBD_BREEDS = {
    "bargur": "Bargur",
    "gir": "Gir",
    "hallikar": "Hallikar",
    "kankrej": "Kankrej",
    "ongole": "Ongole",
    "pulikulam": "Pulikulam",
    "rathi": "Rathi",
    "sahiwal": "Sahiwal",
    "tharparkar": "Tharparkar",
}


def normalize_key(value):
    return (
        value.strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )


def load_secondary_label_map():
    mapping = {}

    if not LABEL_REVIEW_CSV.exists():
        return mapping

    with LABEL_REVIEW_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if (
                row["source"]
                !=
                "indian_bovine_secondary"
            ):
                continue

            original = normalize_key(
                row["original_label"]
            )

            normalized = (
                row["normalized_label"]
                .strip()
            )

            mapping[original] = normalized

    return mapping


def detect_label(
    path_string,
    secondary_map,
):
    path = Path(path_string)

    parts = list(path.parts)


    # =====================================================
    # IICBD
    # =====================================================

    if "iicbd_2026" in parts:

        for part in parts:

            key = normalize_key(part)

            if key in IICBD_BREEDS:
                return (
                    IICBD_BREEDS[key],
                    "iicbd_2026",
                )


    # =====================================================
    # SECONDARY BOVINE DATASET
    # =====================================================

    if "indian_bovine_kaggle" in parts:

        original_label = normalize_key(
            path.parent.name
        )

        normalized = secondary_map.get(
            original_label
        )

        if normalized:
            return (
                normalized,
                "indian_bovine_secondary",
            )

        return (
            path.parent.name,
            "indian_bovine_secondary_unknown",
        )


    return (
        "UNKNOWN",
        "unknown",
    )


def main():

    print("=" * 78)
    print("BREEDVISION AI - CROSS-CLASS DUPLICATE AUDIT")
    print("=" * 78)


    if not DUPLICATES_CSV.exists():

        raise FileNotFoundError(
            "\nExact duplicate report not found:\n"
            f"{DUPLICATES_CSV}\n\n"
            "Run 04_audit_exact_duplicates.py first."
        )


    secondary_map = (
        load_secondary_label_map()
    )


    # =====================================================
    # REBUILD DUPLICATE GROUPS
    # =====================================================

    groups = defaultdict(set)


    with DUPLICATES_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            sha256 = (
                row["sha256"]
                .strip()
            )

            keeper = (
                row["keeper"]
                .strip()
            )

            duplicate = (
                row["duplicate"]
                .strip()
            )

            groups[sha256].add(
                keeper
            )

            groups[sha256].add(
                duplicate
            )


    conflict_rows = []

    same_class_groups = 0

    cross_class_groups = 0

    unknown_groups = 0


    # =====================================================
    # ANALYZE EACH DUPLICATE GROUP
    # =====================================================

    for sha256, paths in groups.items():

        labelled_paths = []

        labels = set()


        for path in sorted(paths):

            label, source = detect_label(
                path,
                secondary_map,
            )

            labels.add(label)

            labelled_paths.append(
                {
                    "path": path,
                    "label": label,
                    "source": source,
                }
            )


        if "UNKNOWN" in labels:

            status = "unknown_label"

            unknown_groups += 1


        elif len(labels) == 1:

            status = "same_class_duplicate"

            same_class_groups += 1


        else:

            status = "cross_class_conflict"

            cross_class_groups += 1


        # Only cross-class / unknown groups need detailed report

        if status != "same_class_duplicate":

            for item in labelled_paths:

                conflict_rows.append(
                    {
                        "sha256":
                            sha256,

                        "status":
                            status,

                        "group_labels":
                            " | ".join(
                                sorted(labels)
                            ),

                        "detected_label":
                            item["label"],

                        "source":
                            item["source"],

                        "path":
                            item["path"],
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
            "sha256",
            "status",
            "group_labels",
            "detected_label",
            "source",
            "path",
        ]


        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            conflict_rows
        )


    # =====================================================
    # SUMMARY JSON
    # =====================================================

    summary = {
        "duplicate_groups_checked":
            len(groups),

        "same_class_duplicate_groups":
            same_class_groups,

        "cross_class_conflict_groups":
            cross_class_groups,

        "unknown_label_groups":
            unknown_groups,

        "policy": {
            "same_class_duplicates":
                "Keep only one copy in processed dataset.",

            "cross_class_conflicts":
                "Exclude all files in conflicting groups until manually reviewed.",

            "unknown_label_groups":
                "Exclude until label provenance is resolved."
        }
    }


    with OUTPUT_JSON.open(
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
        "Duplicate groups checked       :",
        len(groups),
    )

    print(
        "Same-class duplicate groups    :",
        same_class_groups,
    )

    print(
        "Cross-class conflict groups    :",
        cross_class_groups,
    )

    print(
        "Unknown-label duplicate groups :",
        unknown_groups,
    )


    print()

    if cross_class_groups == 0:

        print(
            "No exact duplicate label conflicts detected."
        )

    else:

        print(
            "WARNING: Cross-class duplicate conflicts detected."
        )

        print(
            "These groups will be excluded from the processed dataset."
        )


    print()

    print(
        "CSV report :",
        OUTPUT_CSV,
    )

    print(
        "JSON report:",
        OUTPUT_JSON,
    )


    print()

    print(
        "No raw files were modified or deleted."
    )


if __name__ == "__main__":
    main()