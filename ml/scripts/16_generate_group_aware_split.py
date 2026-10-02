from pathlib import Path
import csv
import json
import random
from collections import defaultdict


# =========================================================
# BREEDVISION AI
# PHASE 4 - GROUP-AWARE TRAIN / VAL / TEST SPLIT
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORTS_DIR = PROJECT_ROOT / "reports"
CONFIGS_DIR = PROJECT_ROOT / "configs"


GROUPS_CSV = (
    REPORTS_DIR
    / "near_duplicate_groups.csv"
)

DATASET_CONFIG = (
    CONFIGS_DIR
    / "dataset_config.json"
)


OUTPUT_CSV = (
    REPORTS_DIR
    / "dataset_split_manifest.csv"
)

OUTPUT_JSON = (
    REPORTS_DIR
    / "dataset_split_summary.json"
)


RANDOM_SEED = 42


SPLIT_RATIOS = {
    "train": 0.70,
    "validation": 0.15,
    "test": 0.15,
}


# =========================================================
# LOADERS
# =========================================================


def load_json(path):

    if not path.exists():
        raise FileNotFoundError(
            f"Missing required file:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def load_group_rows():

    if not GROUPS_CSV.exists():

        raise FileNotFoundError(
            f"\nNear-duplicate grouping file not found:\n"
            f"{GROUPS_CSV}\n\n"
            "Run 15_group_near_duplicates.py first."
        )


    with GROUPS_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        return list(
            csv.DictReader(file)
        )


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 82)
    print("BREEDVISION AI - GROUP-AWARE TRAIN / VAL / TEST SPLIT")
    print("=" * 82)


    random.seed(
        RANDOM_SEED
    )


    config = load_json(
        DATASET_CONFIG
    )


    classes = config[
        "classes"
    ]


    rows = load_group_rows()


    print()
    print(
        "Images loaded:",
        len(rows),
    )

    print(
        "Classes:",
        len(classes),
    )


    # =====================================================
    # GROUP IMAGES BY GROUP_ID
    # =====================================================

    groups = defaultdict(
        list
    )


    for row in rows:

        group_id = (
            row[
                "group_id"
            ].strip()
        )

        groups[
            group_id
        ].append(
            row
        )


    print(
        "Groups loaded:",
        len(groups),
    )


    # =====================================================
    # TOTAL CLASS COUNTS
    # =====================================================

    total_class_counts = defaultdict(
        int
    )


    for row in rows:

        breed = (
            row[
                "breed"
            ].strip()
        )

        total_class_counts[
            breed
        ] += 1


    # =====================================================
    # TARGET COUNTS
    # =====================================================

    target_total_counts = {

        split:
            len(rows)
            *
            ratio

        for split, ratio
        in SPLIT_RATIOS.items()
    }


    target_class_counts = {

        split: {

            breed:
                total_class_counts[
                    breed
                ]
                *
                ratio

            for breed in classes
        }

        for split, ratio
        in SPLIT_RATIOS.items()
    }


    # =====================================================
    # CURRENT COUNTS
    # =====================================================

    current_total_counts = {

        split: 0

        for split in SPLIT_RATIOS
    }


    current_class_counts = {

        split: {

            breed: 0

            for breed in classes
        }

        for split in SPLIT_RATIOS
    }


    # =====================================================
    # PREPARE GROUP DATA
    # =====================================================

    group_data = []


    for group_id, group_rows in groups.items():

        breed_counts = defaultdict(
            int
        )


        for row in group_rows:

            breed = (
                row[
                    "breed"
                ].strip()
            )

            breed_counts[
                breed
            ] += 1


        group_data.append(
            {
                "group_id":
                    group_id,

                "rows":
                    group_rows,

                "size":
                    len(
                        group_rows
                    ),

                "breed_counts":
                    dict(
                        breed_counts
                    ),
            }
        )


    # =====================================================
    # LARGE GROUPS FIRST
    #
    # Random value only acts as deterministic tie-breaker.
    # =====================================================

    random_keys = {

        group[
            "group_id"
        ]:
            random.random()

        for group in group_data
    }


    group_data.sort(
        key=lambda group: (
            -group[
                "size"
            ],

            random_keys[
                group[
                    "group_id"
                ]
            ],
        )
    )


    # =====================================================
    # GREEDY ASSIGNMENT
    # =====================================================

    group_assignment = {}


    for group in group_data:

        best_split = None
        best_score = None


        for split in SPLIT_RATIOS:

            # ---------------------------------------------
            # Total dataset-size deviation
            # ---------------------------------------------

            projected_total = (
                current_total_counts[
                    split
                ]
                +
                group[
                    "size"
                ]
            )


            target_total = (
                target_total_counts[
                    split
                ]
            )


            total_deviation = abs(
                projected_total
                -
                target_total
            ) / max(
                target_total,
                1,
            )


            # ---------------------------------------------
            # Per-class deviation
            # ---------------------------------------------

            class_deviation = 0.0


            for breed in classes:

                projected_class = (
                    current_class_counts[
                        split
                    ][
                        breed
                    ]
                    +
                    group[
                        "breed_counts"
                    ].get(
                        breed,
                        0,
                    )
                )


                target_class = (
                    target_class_counts[
                        split
                    ][
                        breed
                    ]
                )


                class_deviation += abs(
                    projected_class
                    -
                    target_class
                ) / max(
                    target_class,
                    1,
                )


            # Average class deviation

            class_deviation /= max(
                len(classes),
                1,
            )


            # ---------------------------------------------
            # Combined score
            #
            # Class balance weighted more heavily.
            # ---------------------------------------------

            score = (
                class_deviation
                *
                0.75
                +
                total_deviation
                *
                0.25
            )


            if (
                best_score is None
                or
                score < best_score
            ):

                best_score = score

                best_split = split


        # =================================================
        # ASSIGN WHOLE GROUP
        # =================================================

        group_assignment[
            group[
                "group_id"
            ]
        ] = best_split


        current_total_counts[
            best_split
        ] += group[
            "size"
        ]


        for breed, count in (
            group[
                "breed_counts"
            ].items()
        ):

            current_class_counts[
                best_split
            ][
                breed
            ] += count


    # =====================================================
    # BUILD OUTPUT MANIFEST
    # =====================================================

    output_rows = []


    for row in rows:

        group_id = (
            row[
                "group_id"
            ].strip()
        )


        split = (
            group_assignment[
                group_id
            ]
        )


        output_rows.append(
            {
                "image_path":
                    row[
                        "image_path"
                    ],

                "breed":
                    row[
                        "breed"
                    ],

                "group_id":
                    group_id,

                "group_size":
                    row[
                        "group_size"
                    ],

                "group_type":
                    row[
                        "group_type"
                    ],

                "split":
                    split,
            }
        )


    # =====================================================
    # SORT OUTPUT
    # =====================================================

    split_order = {
        "train": 0,
        "validation": 1,
        "test": 2,
    }


    output_rows.sort(
        key=lambda row: (
            split_order[
                row[
                    "split"
                ]
            ],
            row[
                "breed"
            ],
            row[
                "group_id"
            ],
            row[
                "image_path"
            ],
        )
    )


    # =====================================================
    # SAVE CSV
    # =====================================================

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        fieldnames = [
            "image_path",
            "breed",
            "group_id",
            "group_size",
            "group_type",
            "split",
        ]


        writer = csv.DictWriter(
            file,
            fieldnames=
                fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            output_rows
        )


    # =====================================================
    # FINAL COUNTS
    # =====================================================

    final_split_counts = defaultdict(
        int
    )


    final_class_split_counts = {

        breed: {
            "train": 0,
            "validation": 0,
            "test": 0,
        }

        for breed in classes
    }


    for row in output_rows:

        split = (
            row[
                "split"
            ]
        )

        breed = (
            row[
                "breed"
            ]
        )


        final_split_counts[
            split
        ] += 1


        if breed in final_class_split_counts:

            final_class_split_counts[
                breed
            ][
                split
            ] += 1


    # =====================================================
    # GROUP LEAKAGE INTERNAL CHECK
    # =====================================================

    group_splits = defaultdict(
        set
    )


    for row in output_rows:

        group_splits[
            row[
                "group_id"
            ]
        ].add(
            row[
                "split"
            ]
        )


    leaking_groups = {

        group_id:
            sorted(
                splits
            )

        for group_id, splits
        in group_splits.items()

        if len(splits) > 1
    }


    # =====================================================
    # SUMMARY JSON
    # =====================================================

    summary = {

        "random_seed":
            RANDOM_SEED,

        "split_ratios":
            SPLIT_RATIOS,

        "total_images":
            len(
                output_rows
            ),

        "total_groups":
            len(
                groups
            ),

        "split_counts":
            dict(
                final_split_counts
            ),

        "split_percentages": {

            split:
                round(
                    (
                        final_split_counts[
                            split
                        ]
                        /
                        max(
                            len(
                                output_rows
                            ),
                            1,
                        )
                    )
                    *
                    100,
                    2,
                )

            for split in SPLIT_RATIOS
        },

        "class_split_counts":
            final_class_split_counts,

        "group_leakage_count":
            len(
                leaking_groups
            ),

        "leaking_groups":
            leaking_groups,

        "policy":
            (
                "Every near-duplicate group is assigned entirely "
                "to one split."
            ),
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
    print("=" * 82)
    print("SPLIT RESULT")
    print("=" * 82)


    for split in [
        "train",
        "validation",
        "test",
    ]:

        count = (
            final_split_counts[
                split
            ]
        )


        percentage = (
            count
            /
            max(
                len(
                    output_rows
                ),
                1,
            )
            *
            100
        )


        print(
            f"{split:<12} : "
            f"{count:<8} "
            f"({percentage:.2f}%)"
        )


    print()
    print("-" * 82)
    print("CLASS-WISE SPLIT COUNTS")
    print("-" * 82)


    print(
        f"{'Breed':<25}"
        f"{'Train':>10}"
        f"{'Validation':>14}"
        f"{'Test':>10}"
    )


    for breed in classes:

        counts = (
            final_class_split_counts[
                breed
            ]
        )


        print(
            f"{breed:<25}"
            f"{counts['train']:>10}"
            f"{counts['validation']:>14}"
            f"{counts['test']:>10}"
        )


    print()
    print(
        "Group leakage detected:",
        len(
            leaking_groups
        ),
    )


    if len(
        leaking_groups
    ) == 0:

        print(
            "PASS: No near-duplicate group was split "
            "across train/validation/test."
        )

    else:

        print(
            "WARNING: Group leakage detected."
        )


    print()
    print(
        "Split manifest:",
        OUTPUT_CSV
    )

    print(
        "Summary:",
        OUTPUT_JSON
    )


    print()
    print(
        "No images were copied, moved or deleted."
    )


if __name__ == "__main__":
    main()