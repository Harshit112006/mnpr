from pathlib import Path
import csv
import json
import re


# =========================================================
# BREEDVISION AI
# PHASE 4 - LABEL NORMALIZATION REVIEW
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)


IICBD_REPORT = (
    REPORTS_DIR
    / "iicbd_inventory.json"
)

BOVINE_REPORT = (
    REPORTS_DIR
    / "indian_bovine_inventory.json"
)


OUTPUT_CSV = (
    REPORTS_DIR
    / "label_normalization_review.csv"
)

OUTPUT_JSON = (
    REPORTS_DIR
    / "label_normalization_review.json"
)


# =========================================================
# STANDARD LABEL SPELLINGS
# =========================================================

STANDARD_LABELS = {
    "bargur": "Bargur",
    "gir": "Gir",
    "hallikar": "Hallikar",
    "kankrej": "Kankrej",
    "ongole": "Ongole",
    "pulikulam": "Pulikulam",
    "rathi": "Rathi",
    "sahiwal": "Sahiwal",
    "tharparkar": "Tharparkar",

    "murrah": "Murrah",
    "jaffarabadi": "Jaffarabadi",
    "mehsana": "Mehsana",
    "surti": "Surti",
    "banni": "Banni",
}


def load_json(path):
    if not path.exists():
        return None

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def normalize_key(value):
    value = value.strip().lower()

    value = re.sub(
        r"[_\-]+",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value


def canonicalize_label(label):
    normalized = normalize_key(
        label
    )

    if normalized in STANDARD_LABELS:
        return (
            STANDARD_LABELS[
                normalized
            ],
            "recognized"
        )

    title_case = " ".join(
        word.capitalize()
        for word in normalized.split()
    )

    return (
        title_case,
        "review_required"
    )


def main():
    print("=" * 72)
    print("BREEDVISION AI - LABEL NORMALIZATION REVIEW")
    print("=" * 72)


    iicbd = load_json(
        IICBD_REPORT
    )

    bovine = load_json(
        BOVINE_REPORT
    )


    rows = []


    # =====================================================
    # IICBD
    # =====================================================

    if iicbd:
        breed_counts = (
            iicbd.get(
                "breed_counts",
                {}
            )
        )

        for (
            original_label,
            count,
        ) in breed_counts.items():

            if count <= 0:
                continue


            (
                normalized_label,
                status,
            ) = canonicalize_label(
                original_label
            )


            rows.append(
                {
                    "source":
                        "iicbd_2026",

                    "original_label":
                        original_label,

                    "normalized_label":
                        normalized_label,

                    "image_count":
                        count,

                    "status":
                        status,

                    "species":
                        "cattle",

                    "include":
                        "",

                    "notes":
                        "",
                }
            )


    # =====================================================
    # SECONDARY BOVINE DATASET
    # =====================================================

    if bovine:
        class_counts = (
            bovine.get(
                "class_counts",
                {}
            )
        )

        for (
            original_label,
            count,
        ) in class_counts.items():

            (
                normalized_label,
                status,
            ) = canonicalize_label(
                original_label
            )


            rows.append(
                {
                    "source":
                        "indian_bovine_secondary",

                    "original_label":
                        original_label,

                    "normalized_label":
                        normalized_label,

                    "image_count":
                        count,

                    "status":
                        status,

                    "species":
                        "",

                    "include":
                        "",

                    "notes":
                        "",
                }
            )


    # =====================================================
    # SORT
    # =====================================================

    rows.sort(
        key=lambda row: (
            row[
                "normalized_label"
            ].lower(),
            row[
                "source"
            ],
        )
    )


    # =====================================================
    # CSV
    # =====================================================

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        fieldnames = [
            "source",
            "original_label",
            "normalized_label",
            "image_count",
            "status",
            "species",
            "include",
            "notes",
        ]


        writer = csv.DictWriter(
            csv_file,
            fieldnames=
                fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


    # =====================================================
    # JSON
    # =====================================================

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as json_file:

        json.dump(
            rows,
            json_file,
            indent=4,
        )


    # =====================================================
    # TERMINAL SUMMARY
    # =====================================================

    print()
    print(
        f"Total label entries: {len(rows)}"
    )


    recognized = [
        row
        for row in rows
        if row["status"] ==
        "recognized"
    ]


    review_required = [
        row
        for row in rows
        if row["status"] ==
        "review_required"
    ]


    print(
        "Recognized labels   :",
        len(recognized),
    )

    print(
        "Need manual review  :",
        len(
            review_required
        ),
    )


    print()
    print("-" * 72)
    print("NORMALIZED LABELS")
    print("-" * 72)


    for row in rows:
        print(
            f"{row['source']:<25} "
            f"{row['original_label']:<28} "
            f"-> "
            f"{row['normalized_label']:<22} "
            f"({row['image_count']})"
        )


    if review_required:
        print()
        print("-" * 72)
        print("LABELS REQUIRING REVIEW")
        print("-" * 72)


        for row in review_required:
            print(
                f"{row['original_label']} "
                f"-> "
                f"{row['normalized_label']}"
            )


    print()
    print(
        "CSV:",
        OUTPUT_CSV,
    )

    print(
        "JSON:",
        OUTPUT_JSON,
    )


if __name__ == "__main__":
    main()