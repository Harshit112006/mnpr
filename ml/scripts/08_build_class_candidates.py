from pathlib import Path
import csv
import json
from collections import defaultdict


# =========================================================
# BREEDVISION AI
# PHASE 4 - FINAL CLASS CANDIDATE REPORT
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)


INPUT_CSV = (
    REPORTS_DIR
    / "label_normalization_review.csv"
)


OUTPUT_CSV = (
    REPORTS_DIR
    / "class_candidate_report.csv"
)


OUTPUT_JSON = (
    REPORTS_DIR
    / "class_candidate_report.json"
)


# =========================================================
# KNOWN SPECIES MAPPING
#
# This is only used for labels we explicitly recognize.
# Unknown labels remain "review_required".
# =========================================================

SPECIES_MAP = {
    # CATTLE
    "Bargur": "cattle",
    "Gir": "cattle",
    "Hallikar": "cattle",
    "Kankrej": "cattle",
    "Ongole": "cattle",
    "Pulikulam": "cattle",
    "Rathi": "cattle",
    "Sahiwal": "cattle",
    "Tharparkar": "cattle",

    # BUFFALO
    "Murrah": "buffalo",
    "Jaffarabadi": "buffalo",
    "Mehsana": "buffalo",
    "Surti": "buffalo",
    "Banni": "buffalo",
}


# =========================================================
# DATA STRENGTH CATEGORY
#
# These categories do NOT automatically decide inclusion.
# They only describe dataset size.
# =========================================================

def get_strength(total_images):
    if total_images >= 500:
        return "strong"

    if total_images >= 200:
        return "usable"

    if total_images >= 100:
        return "weak"

    return "insufficient"


def load_rows():
    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            "\nLabel review CSV not found:\n"
            f"{INPUT_CSV}\n\n"
            "Run 07_prepare_label_review.py first."
        )

    with INPUT_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as csv_file:

        return list(
            csv.DictReader(
                csv_file
            )
        )


def main():
    print("=" * 78)
    print("BREEDVISION AI - FINAL CLASS CANDIDATE REPORT")
    print("=" * 78)


    rows = load_rows()


    # =====================================================
    # AGGREGATE SAME NORMALIZED LABEL ACROSS SOURCES
    # =====================================================

    aggregated = defaultdict(
        lambda: {
            "total_images": 0,
            "sources": [],
            "original_labels": [],
        }
    )


    for row in rows:
        normalized_label = (
            row[
                "normalized_label"
            ].strip()
        )


        if not normalized_label:
            continue


        try:
            image_count = int(
                row[
                    "image_count"
                ]
            )
        except (
            TypeError,
            ValueError,
        ):
            image_count = 0


        aggregated[
            normalized_label
        ][
            "total_images"
        ] += image_count


        source = (
            row[
                "source"
            ].strip()
        )


        original_label = (
            row[
                "original_label"
            ].strip()
        )


        if (
            source
            and source
            not in
            aggregated[
                normalized_label
            ][
                "sources"
            ]
        ):
            aggregated[
                normalized_label
            ][
                "sources"
            ].append(
                source
            )


        if (
            original_label
            and original_label
            not in
            aggregated[
                normalized_label
            ][
                "original_labels"
            ]
        ):
            aggregated[
                normalized_label
            ][
                "original_labels"
            ].append(
                original_label
            )


    # =====================================================
    # BUILD REPORT
    # =====================================================

    candidate_rows = []


    for (
        breed,
        info,
    ) in aggregated.items():

        species = (
            SPECIES_MAP.get(
                breed
            )
        )


        total_images = (
            info[
                "total_images"
            ]
        )


        strength = (
            get_strength(
                total_images
            )
        )


        if species is None:
            recommendation = (
                "manual_review"
            )

            reason = (
                "Species mapping is unknown."
            )

        elif strength == "strong":
            recommendation = (
                "strong_candidate"
            )

            reason = (
                "Recognized breed with at least 500 images."
            )

        elif strength == "usable":
            recommendation = (
                "candidate"
            )

            reason = (
                "Recognized breed with 200-499 images."
            )

        elif strength == "weak":
            recommendation = (
                "review_low_data"
            )

            reason = (
                "Recognized breed has only 100-199 images."
            )

        else:
            recommendation = (
                "insufficient_data"
            )

            reason = (
                "Recognized breed has fewer than 100 images."
            )


        candidate_rows.append(
            {
                "breed":
                    breed,

                "species":
                    species
                    or "unknown",

                "total_images":
                    total_images,

                "source_count":
                    len(
                        info[
                            "sources"
                        ]
                    ),

                "sources":
                    " | ".join(
                        info[
                            "sources"
                        ]
                    ),

                "original_labels":
                    " | ".join(
                        info[
                            "original_labels"
                        ]
                    ),

                "strength":
                    strength,

                "recommendation":
                    recommendation,

                "reason":
                    reason,

                "final_include":
                    "",

                "final_notes":
                    "",
            }
        )


    candidate_rows.sort(
        key=lambda row: (
            row[
                "species"
            ],
            -row[
                "total_images"
            ],
            row[
                "breed"
            ].lower(),
        )
    )


    # =====================================================
    # CSV
    # =====================================================

    fieldnames = [
        "breed",
        "species",
        "total_images",
        "source_count",
        "sources",
        "original_labels",
        "strength",
        "recommendation",
        "reason",
        "final_include",
        "final_notes",
    ]


    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=
                fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            candidate_rows
        )


    # =====================================================
    # JSON
    # =====================================================

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as json_file:

        json.dump(
            candidate_rows,
            json_file,
            indent=4,
        )


    # =====================================================
    # TERMINAL OUTPUT
    # =====================================================

    print()

    print(
        f"{'Breed':<24}"
        f"{'Species':<12}"
        f"{'Images':<10}"
        f"{'Strength':<14}"
        f"{'Recommendation'}"
    )

    print("-" * 78)


    for row in candidate_rows:
        print(
            f"{row['breed']:<24}"
            f"{row['species']:<12}"
            f"{row['total_images']:<10}"
            f"{row['strength']:<14}"
            f"{row['recommendation']}"
        )


    # =====================================================
    # SUMMARY
    # =====================================================

    cattle = [
        row
        for row in candidate_rows
        if row[
            "species"
        ] == "cattle"
    ]


    buffalo = [
        row
        for row in candidate_rows
        if row[
            "species"
        ] == "buffalo"
    ]


    unknown = [
        row
        for row in candidate_rows
        if row[
            "species"
        ] == "unknown"
    ]


    strong = [
        row
        for row in candidate_rows
        if row[
            "strength"
        ] == "strong"
    ]


    usable = [
        row
        for row in candidate_rows
        if row[
            "strength"
        ] == "usable"
    ]


    weak = [
        row
        for row in candidate_rows
        if row[
            "strength"
        ] == "weak"
    ]


    insufficient = [
        row
        for row in candidate_rows
        if row[
            "strength"
        ] == "insufficient"
    ]


    print()
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)


    print(
        "Total normalized breeds :",
        len(
            candidate_rows
        ),
    )

    print(
        "Known cattle breeds     :",
        len(
            cattle
        ),
    )

    print(
        "Known buffalo breeds    :",
        len(
            buffalo
        ),
    )

    print(
        "Unknown labels          :",
        len(
            unknown
        ),
    )


    print()
    print(
        "Strong classes          :",
        len(
            strong
        ),
    )

    print(
        "Usable classes          :",
        len(
            usable
        ),
    )

    print(
        "Weak classes            :",
        len(
            weak
        ),
    )

    print(
        "Insufficient classes    :",
        len(
            insufficient
        ),
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


    print()
    print(
        "IMPORTANT:"
    )

    print(
        "This script does not automatically freeze classes."
    )

    print(
        "Final class selection will be based on this audited report."
    )


if __name__ == "__main__":
    main()