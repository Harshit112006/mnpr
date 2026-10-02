from pathlib import Path
import csv
import json


# =========================================================
# BREEDVISION AI
# PHASE 4 - FREEZE CLASSIFIER V1 CLASSES
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)

CONFIGS_DIR = (
    PROJECT_ROOT
    / "configs"
)


INPUT_CSV = (
    REPORTS_DIR
    / "class_candidate_report.csv"
)


FINAL_CSV = (
    REPORTS_DIR
    / "final_class_freeze.csv"
)

FINAL_JSON = (
    REPORTS_DIR
    / "final_class_freeze.json"
)


CLASS_TO_INDEX_PATH = (
    CONFIGS_DIR
    / "class_to_index.json"
)

SPECIES_MAPPING_PATH = (
    CONFIGS_DIR
    / "species_mapping.json"
)

DATASET_CONFIG_PATH = (
    CONFIGS_DIR
    / "dataset_config.json"
)


# =========================================================
# POLICY
# =========================================================

MIN_IMAGES_FOR_V1 = 200

ALLOWED_SPECIES = {
    "cattle",
    "buffalo",
}


def load_candidates():
    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            "\nCandidate report not found:\n"
            f"{INPUT_CSV}\n\n"
            "Run 08_build_class_candidates.py first."
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
    print("=" * 80)
    print("BREEDVISION AI - CLASSIFIER V1 CLASS FREEZE")
    print("=" * 80)


    CONFIGS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    candidates = (
        load_candidates()
    )


    final_rows = []


    # =====================================================
    # CLASS DECISION
    # =====================================================

    for row in candidates:

        breed = (
            row[
                "breed"
            ].strip()
        )

        species = (
            row[
                "species"
            ].strip().lower()
        )


        try:
            total_images = int(
                row[
                    "total_images"
                ]
            )

        except (
            TypeError,
            ValueError,
        ):
            total_images = 0


        # =================================================
        # DECISION LOGIC
        # =================================================

        if species not in ALLOWED_SPECIES:

            include = False

            decision = (
                "exclude_unverified_species"
            )

            reason = (
                "Species is not verified as cattle or buffalo."
            )


        elif total_images < MIN_IMAGES_FOR_V1:

            include = False

            decision = (
                "exclude_low_data"
            )

            reason = (
                f"Only {total_images} images available; "
                f"v1 minimum is {MIN_IMAGES_FOR_V1}."
            )


        else:

            include = True

            decision = (
                "include_v1"
            )

            reason = (
                f"Verified {species} breed with "
                f"{total_images} audited images."
            )


        final_rows.append(
            {
                "breed":
                    breed,

                "species":
                    species,

                "total_images":
                    total_images,

                "sources":
                    row.get(
                        "sources",
                        "",
                    ),

                "include_v1":
                    include,

                "decision":
                    decision,

                "reason":
                    reason,
            }
        )


    # =====================================================
    # INCLUDED CLASSES
    # =====================================================

    included = [
        row
        for row in final_rows
        if row[
            "include_v1"
        ]
    ]


    # Deterministic class ordering:
    # cattle alphabetically,
    # then buffalo alphabetically.

    species_order = {
        "cattle": 0,
        "buffalo": 1,
    }


    included.sort(
        key=lambda row: (
            species_order.get(
                row[
                    "species"
                ],
                99,
            ),
            row[
                "breed"
            ].lower(),
        )
    )


    # =====================================================
    # CLASS -> INDEX
    # =====================================================

    class_to_index = {
        row[
            "breed"
        ]: index

        for index, row
        in enumerate(
            included
        )
    }


    # =====================================================
    # SPECIES MAPPING
    # =====================================================

    species_mapping = {
        row[
            "breed"
        ]:
        row[
            "species"
        ]

        for row in included
    }


    # =====================================================
    # DATASET CONFIG
    # =====================================================

    cattle_classes = [
        row[
            "breed"
        ]
        for row in included
        if row[
            "species"
        ] == "cattle"
    ]


    buffalo_classes = [
        row[
            "breed"
        ]
        for row in included
        if row[
            "species"
        ] == "buffalo"
    ]


    dataset_config = {
        "project":
            "BreedVision AI",

        "classifier_version":
            "v1",

        "minimum_images_per_class":
            MIN_IMAGES_FOR_V1,

        "num_classes":
            len(
                included
            ),

        "num_cattle_classes":
            len(
                cattle_classes
            ),

        "num_buffalo_classes":
            len(
                buffalo_classes
            ),

        "classes":
            [
                row[
                    "breed"
                ]
                for row in included
            ],

        "cattle_classes":
            cattle_classes,

        "buffalo_classes":
            buffalo_classes,

        "class_to_index":
            class_to_index,

        "species_mapping":
            species_mapping,

        "split_policy": {
            "train":
                0.70,

            "validation":
                0.15,

            "test":
                0.15,
        },

        "image_policy": {
            "minimum_width":
                224,

            "minimum_height":
                224,

            "raw_data_modified":
                False,

            "synthetic_primary_training":
                False,

            "validation_augmentation":
                False,

            "test_augmentation":
                False,
        },
    }


    # =====================================================
    # SAVE FINAL CSV
    # =====================================================

    with FINAL_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        fieldnames = [
            "breed",
            "species",
            "total_images",
            "sources",
            "include_v1",
            "decision",
            "reason",
        ]


        writer = csv.DictWriter(
            csv_file,
            fieldnames=
                fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            final_rows
        )


    # =====================================================
    # SAVE FINAL JSON
    # =====================================================

    with FINAL_JSON.open(
        "w",
        encoding="utf-8",
    ) as json_file:

        json.dump(
            final_rows,
            json_file,
            indent=4,
        )


    # =====================================================
    # SAVE CONFIG FILES
    # =====================================================

    with CLASS_TO_INDEX_PATH.open(
        "w",
        encoding="utf-8",
    ) as json_file:

        json.dump(
            class_to_index,
            json_file,
            indent=4,
        )


    with SPECIES_MAPPING_PATH.open(
        "w",
        encoding="utf-8",
    ) as json_file:

        json.dump(
            species_mapping,
            json_file,
            indent=4,
        )


    with DATASET_CONFIG_PATH.open(
        "w",
        encoding="utf-8",
    ) as json_file:

        json.dump(
            dataset_config,
            json_file,
            indent=4,
        )


    # =====================================================
    # TERMINAL OUTPUT
    # =====================================================

    print()
    print("-" * 80)
    print("BREEDVISION CLASSIFIER V1")
    print("-" * 80)


    print()
    print("CATTLE")


    if cattle_classes:
        for index, breed in enumerate(
            cattle_classes,
            start=1,
        ):
            count = next(
                row[
                    "total_images"
                ]

                for row in included

                if row[
                    "breed"
                ] == breed
            )

            print(
                f"  {index:02d}. "
                f"{breed:<20} "
                f"{count} images"
            )

    else:
        print(
            "  No eligible cattle classes."
        )


    print()
    print("BUFFALO")


    if buffalo_classes:
        for index, breed in enumerate(
            buffalo_classes,
            start=1,
        ):
            count = next(
                row[
                    "total_images"
                ]

                for row in included

                if row[
                    "breed"
                ] == breed
            )

            print(
                f"  {index:02d}. "
                f"{breed:<20} "
                f"{count} images"
            )

    else:
        print(
            "  No eligible buffalo classes."
        )


    # =====================================================
    # EXCLUDED
    # =====================================================

    excluded = [
        row
        for row in final_rows
        if not row[
            "include_v1"
        ]
    ]


    print()
    print("-" * 80)

    print(
        "Included classes :",
        len(
            included
        ),
    )

    print(
        "Cattle classes   :",
        len(
            cattle_classes
        ),
    )

    print(
        "Buffalo classes  :",
        len(
            buffalo_classes
        ),
    )

    print(
        "Excluded classes :",
        len(
            excluded
        ),
    )


    if excluded:
        print()
        print("EXCLUDED / HELD CLASSES")


        for row in excluded:
            print(
                f"  {row['breed']:<25} "
                f"{row['total_images']:<7} "
                f"{row['decision']}"
            )


    print()
    print("=" * 80)
    print("CONFIGURATION FILES CREATED")
    print("=" * 80)


    print(
        CLASS_TO_INDEX_PATH
    )

    print(
        SPECIES_MAPPING_PATH
    )

    print(
        DATASET_CONFIG_PATH
    )


    print()
    print(
        "BreedVision Classifier v1 class list is now frozen."
    )


if __name__ == "__main__":
    main()