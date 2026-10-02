from pathlib import Path
import csv
import json
import random
from collections import defaultdict


# =========================================================
# BREEDVISION AI
# PHASE 4
# BALANCED GROUP-AWARE TRAIN / VAL / TEST SPLIT
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


SPLITS = [
    "train",
    "validation",
    "test",
]


# =========================================================
# LOAD HELPERS
# =========================================================


def load_json(path):

    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def load_csv(path):

    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        return list(
            csv.DictReader(file)
        )


# =========================================================
# OBJECTIVE FUNCTION
#
# IMPORTANT:
# We score the ENTIRE dataset distribution after every
# possible group assignment.
#
# The older implementation scored only the candidate split,
# which biased the result toward ~42/29/29.
# =========================================================


def calculate_score(
    current_total_counts,
    current_class_counts,
    target_total_counts,
    target_class_counts,
    classes,
):

    total_error = 0.0
    class_error = 0.0
    overshoot_penalty = 0.0


    # =====================================================
    # OVERALL SPLIT RATIO ERROR
    # =====================================================

    for split in SPLITS:

        target = max(
            target_total_counts[split],
            1.0,
        )

        current = (
            current_total_counts[
                split
            ]
        )


        relative_error = (
            current - target
        ) / target


        total_error += (
            relative_error
            *
            relative_error
        )


        # Strongly discourage unnecessary overshoot

        if current > target:

            overshoot = (
                current - target
            ) / target


            overshoot_penalty += (
                overshoot
                *
                overshoot
            )


    # =====================================================
    # CLASS DISTRIBUTION ERROR
    # =====================================================

    class_terms = 0


    for split in SPLITS:

        for breed in classes:

            target = max(
                target_class_counts[
                    split
                ][
                    breed
                ],
                1.0,
            )


            current = (
                current_class_counts[
                    split
                ][
                    breed
                ]
            )


            relative_error = (
                current - target
            ) / target


            class_error += (
                relative_error
                *
                relative_error
            )


            class_terms += 1


    if class_terms:

        class_error /= (
            class_terms
        )


    # Overall dataset ratio gets strongest priority.
    # Class balance remains important.

    score = (
        3.0
        *
        total_error
        +
        1.5
        *
        class_error
        +
        4.0
        *
        overshoot_penalty
    )


    return score


# =========================================================
# APPLY / REMOVE GROUP
# =========================================================


def apply_group(
    split,
    group,
    current_total_counts,
    current_class_counts,
):

    current_total_counts[
        split
    ] += group[
        "size"
    ]


    for breed, count in (
        group[
            "breed_counts"
        ].items()
    ):

        current_class_counts[
            split
        ][
            breed
        ] += count


def remove_group(
    split,
    group,
    current_total_counts,
    current_class_counts,
):

    current_total_counts[
        split
    ] -= group[
        "size"
    ]


    for breed, count in (
        group[
            "breed_counts"
        ].items()
    ):

        current_class_counts[
            split
        ][
            breed
        ] -= count


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 84)
    print(
        "BREEDVISION AI - BALANCED GROUP-AWARE DATASET SPLIT"
    )
    print("=" * 84)


    random.seed(
        RANDOM_SEED
    )


    config = load_json(
        DATASET_CONFIG
    )


    classes = (
        config[
            "classes"
        ]
    )


    rows = load_csv(
        GROUPS_CSV
    )


    if not rows:

        raise RuntimeError(
            "Near-duplicate grouping manifest is empty."
        )


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
    # BUILD GROUPS
    # =====================================================

    raw_groups = defaultdict(
        list
    )


    for row in rows:

        group_id = (
            row[
                "group_id"
            ].strip()
        )


        raw_groups[
            group_id
        ].append(
            row
        )


    groups = []


    for (
        group_id,
        group_rows,
    ) in raw_groups.items():

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


        groups.append(
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

                "num_breeds":
                    len(
                        breed_counts
                    ),
            }
        )


    print(
        "Near-duplicate groups:",
        len(groups),
    )


    # =====================================================
    # DATASET TOTALS
    # =====================================================

    total_images = len(
        rows
    )


    total_class_counts = {
        breed: 0
        for breed in classes
    }


    for row in rows:

        breed = (
            row[
                "breed"
            ].strip()
        )


        if breed in total_class_counts:

            total_class_counts[
                breed
            ] += 1


    # =====================================================
    # TARGET COUNTS
    # =====================================================

    target_total_counts = {

        split:
            total_images
            *
            SPLIT_RATIOS[
                split
            ]

        for split in SPLITS
    }


    target_class_counts = {

        split: {

            breed:
                total_class_counts[
                    breed
                ]
                *
                SPLIT_RATIOS[
                    split
                ]

            for breed in classes
        }

        for split in SPLITS
    }


    # =====================================================
    # CURRENT COUNTS
    # =====================================================

    current_total_counts = {

        split: 0

        for split in SPLITS
    }


    current_class_counts = {

        split: {

            breed: 0

            for breed in classes
        }

        for split in SPLITS
    }


    # =====================================================
    # GROUP ORDER
    #
    # Cross-class and large groups first because they are
    # hardest to place correctly.
    # =====================================================

    random_tiebreak = {

        group[
            "group_id"
        ]:
            random.random()

        for group in groups
    }


    groups.sort(
        key=lambda group: (
            -group[
                "num_breeds"
            ],

            -group[
                "size"
            ],

            random_tiebreak[
                group[
                    "group_id"
                ]
            ],
        )
    )


    # =====================================================
    # INITIAL GLOBAL GREEDY ASSIGNMENT
    # =====================================================

    assignment = {}


    print()
    print(
        "Generating initial balanced split..."
    )


    for group in groups:

        best_split = None
        best_score = None


        for split in SPLITS:

            apply_group(
                split,
                group,
                current_total_counts,
                current_class_counts,
            )


            score = calculate_score(
                current_total_counts,
                current_class_counts,
                target_total_counts,
                target_class_counts,
                classes,
            )


            remove_group(
                split,
                group,
                current_total_counts,
                current_class_counts,
            )


            if (
                best_score is None
                or
                score < best_score
            ):

                best_score = score
                best_split = split


        assignment[
            group[
                "group_id"
            ]
        ] = best_split


        apply_group(
            best_split,
            group,
            current_total_counts,
            current_class_counts,
        )


    # =====================================================
    # LOCAL OPTIMIZATION
    #
    # Try moving complete groups between splits.
    # A move is kept only when the GLOBAL objective improves.
    # =====================================================

    print(
        "Optimizing split distribution..."
    )


    group_lookup = {

        group[
            "group_id"
        ]:
            group

        for group in groups
    }


    current_score = calculate_score(
        current_total_counts,
        current_class_counts,
        target_total_counts,
        target_class_counts,
        classes,
    )


    MAX_PASSES = 8


    for pass_number in range(
        1,
        MAX_PASSES + 1,
    ):

        improved = False


        shuffled_groups = list(
            groups
        )


        random.shuffle(
            shuffled_groups
        )


        for group in shuffled_groups:

            group_id = (
                group[
                    "group_id"
                ]
            )


            current_split = (
                assignment[
                    group_id
                ]
            )


            best_split = (
                current_split
            )

            best_score = (
                current_score
            )


            # Temporarily remove from current split

            remove_group(
                current_split,
                group,
                current_total_counts,
                current_class_counts,
            )


            for candidate_split in SPLITS:

                if (
                    candidate_split
                    ==
                    current_split
                ):
                    continue


                apply_group(
                    candidate_split,
                    group,
                    current_total_counts,
                    current_class_counts,
                )


                candidate_score = (
                    calculate_score(
                        current_total_counts,
                        current_class_counts,
                        target_total_counts,
                        target_class_counts,
                        classes,
                    )
                )


                remove_group(
                    candidate_split,
                    group,
                    current_total_counts,
                    current_class_counts,
                )


                if (
                    candidate_score
                    <
                    best_score
                    -
                    1e-12
                ):

                    best_score = (
                        candidate_score
                    )

                    best_split = (
                        candidate_split
                    )


            # Re-apply group to best split

            apply_group(
                best_split,
                group,
                current_total_counts,
                current_class_counts,
            )


            if (
                best_split
                !=
                current_split
            ):

                assignment[
                    group_id
                ] = best_split

                current_score = (
                    best_score
                )

                improved = True


        print(
            f"Optimization pass {pass_number}: "
            f"{'improved' if improved else 'stable'}"
        )


        if not improved:

            break


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
            assignment[
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
    # SORT MANIFEST
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
            fieldnames=fieldnames,
        )


        writer.writeheader()

        writer.writerows(
            output_rows
        )


    # =====================================================
    # FINAL STATISTICS
    # =====================================================

    final_split_counts = {

        split: 0
        for split in SPLITS
    }


    final_class_split_counts = {

        breed: {

            split: 0

            for split in SPLITS
        }

        for breed in classes
    }


    group_splits = defaultdict(
        set
    )


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

        group_id = (
            row[
                "group_id"
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


        group_splits[
            group_id
        ].add(
            split
        )


    leaking_groups = {

        group_id:
            sorted(
                splits
            )

        for group_id, splits
        in group_splits.items()

        if len(
            splits
        ) > 1
    }


    percentages = {

        split:
            round(
                final_split_counts[
                    split
                ]
                /
                total_images
                *
                100,
                2,
            )

        for split in SPLITS
    }


    summary = {

        "random_seed":
            RANDOM_SEED,

        "split_ratios":
            SPLIT_RATIOS,

        "total_images":
            total_images,

        "total_groups":
            len(
                groups
            ),

        "split_counts":
            final_split_counts,

        "split_percentages":
            percentages,

        "class_split_counts":
            final_class_split_counts,

        "group_leakage_count":
            len(
                leaking_groups
            ),

        "leaking_groups":
            leaking_groups,

        "optimization_score":
            current_score,

        "policy":
            (
                "Every near-duplicate group is assigned "
                "entirely to one split."
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
    # OUTPUT
    # =====================================================

    print()
    print("=" * 84)
    print("FINAL BALANCED SPLIT")
    print("=" * 84)


    for split in SPLITS:

        print(
            f"{split:<12}: "
            f"{final_split_counts[split]:<7} "
            f"({percentages[split]:.2f}%)"
        )


    print()
    print("-" * 84)
    print("CLASS-WISE COUNTS")
    print("-" * 84)


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
        "Group leakage:",
        len(
            leaking_groups
        ),
    )


    if not leaking_groups:

        print(
            "PASS: All near-duplicate groups remain "
            "inside exactly one split."
        )


    print()
    print(
        "Manifest:",
        OUTPUT_CSV
    )

    print(
        "Summary :",
        OUTPUT_JSON
    )


if __name__ == "__main__":
    main()