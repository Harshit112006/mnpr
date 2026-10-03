from pathlib import Path
import csv
import json
import random
from collections import Counter, defaultdict


# =========================================================
# BREEDVISION AI
# PHASE 6.7
# GLOBAL BUFFALO GROUP-AWARE 70/15/15 SPLIT
#
# Rules:
# - Existing cattle splits remain unchanged.
# - Buffalo near-duplicate groups are indivisible.
# - Cross-class near-duplicate groups are also indivisible.
# - Split balance is optimized across every buffalo breed.
# =========================================================


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)


INPUT_MANIFEST = (
    REPORTS_DIR
    / "classifier_v2_master_manifest.csv"
)

OUTPUT_MANIFEST = (
    REPORTS_DIR
    / "classifier_v2_final_manifest.csv"
)

OUTPUT_SUMMARY = (
    REPORTS_DIR
    / "classifier_v2_split_summary.json"
)


RANDOM_SEED = 42

SEARCH_TRIALS = 1000


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
# HELPERS
# =========================================================


def load_csv(path):

    if not path.exists():

        raise FileNotFoundError(
            f"Required manifest missing:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        return list(
            csv.DictReader(file)
        )


def build_groups(rows):

    groups = defaultdict(
        list
    )

    for row in rows:

        group_id = (
            row["group_id"]
            .strip()
        )

        if not group_id:

            raise RuntimeError(
                "Buffalo row has empty group_id:\n"
                f"{row['image_path']}"
            )

        groups[
            group_id
        ].append(
            row
        )

    return dict(
        groups
    )


def calculate_targets(
    buffalo_rows,
    breeds,
):

    global_total = len(
        buffalo_rows
    )


    global_targets = {

        split:
            global_total
            *
            SPLIT_RATIOS[
                split
            ]

        for split in SPLITS
    }


    breed_totals = Counter(
        row["breed"]
        for row in buffalo_rows
    )


    breed_targets = {

        breed: {

            split:
                breed_totals[
                    breed
                ]
                *
                SPLIT_RATIOS[
                    split
                ]

            for split in SPLITS
        }

        for breed in breeds
    }


    return (
        global_targets,
        breed_targets,
        breed_totals,
    )


def group_breed_counts(
    rows,
):

    return Counter(
        row["breed"]
        for row in rows
    )


def calculate_candidate_score(
    selected_split,
    group_rows,
    global_counts,
    breed_counts,
    global_targets,
    breed_targets,
    breeds,
):

    group_size = len(
        group_rows
    )


    group_classes = (
        group_breed_counts(
            group_rows
        )
    )


    score = 0.0


    # =====================================================
    # GLOBAL SPLIT BALANCE
    # =====================================================

    for split in SPLITS:

        future_value = (
            global_counts[
                split
            ]
            +
            (
                group_size
                if split
                ==
                selected_split
                else 0
            )
        )


        target = (
            global_targets[
                split
            ]
        )


        score += (
            0.35
            *
            abs(
                future_value
                -
                target
            )
            /
            max(
                target,
                1.0
            )
        )


    # =====================================================
    # PER-BREED BALANCE
    # =====================================================

    for breed in breeds:

        amount_from_group = (
            group_classes[
                breed
            ]
        )


        for split in SPLITS:

            future_value = (
                breed_counts[
                    breed
                ][
                    split
                ]
                +
                (
                    amount_from_group
                    if split
                    ==
                    selected_split
                    else 0
                )
            )


            target = (
                breed_targets[
                    breed
                ][
                    split
                ]
            )


            score += (
                abs(
                    future_value
                    -
                    target
                )
                /
                max(
                    target,
                    1.0
                )
            )


    return score


def evaluate_final_assignment(
    global_counts,
    breed_counts,
    global_targets,
    breed_targets,
    breeds,
):

    # Every breed must exist in every split.

    for breed in breeds:

        for split in SPLITS:

            if (
                breed_counts[
                    breed
                ][
                    split
                ]
                ==
                0
            ):

                return None


    score = 0.0


    for split in SPLITS:

        score += (
            abs(
                global_counts[
                    split
                ]
                -
                global_targets[
                    split
                ]
            )
            /
            max(
                global_targets[
                    split
                ],
                1.0
            )
        )


    for breed in breeds:

        for split in SPLITS:

            score += (
                abs(
                    breed_counts[
                        breed
                    ][
                        split
                    ]
                    -
                    breed_targets[
                        breed
                    ][
                        split
                    ]
                )
                /
                max(
                    breed_targets[
                        breed
                    ][
                        split
                    ],
                    1.0
                )
            )


    return score


def generate_assignment(
    groups,
    breeds,
    global_targets,
    breed_targets,
    random_seed,
):

    rng = random.Random(
        random_seed
    )


    group_items = list(
        groups.items()
    )


    # Randomized tie-breaking

    rng.shuffle(
        group_items
    )


    # Larger and cross-class groups first.

    group_items.sort(
        key=lambda item: (
            len(
                item[1]
            ),
            len(
                set(
                    row[
                        "breed"
                    ]
                    for row in item[1]
                )
            ),
        ),
        reverse=True,
    )


    assignments = {}


    global_counts = Counter()

    breed_counts = defaultdict(
        Counter
    )


    for (
        group_id,
        group_rows,
    ) in group_items:

        candidate_scores = []


        for split in SPLITS:

            score = calculate_candidate_score(
                selected_split=
                    split,

                group_rows=
                    group_rows,

                global_counts=
                    global_counts,

                breed_counts=
                    breed_counts,

                global_targets=
                    global_targets,

                breed_targets=
                    breed_targets,

                breeds=
                    breeds,
            )


            # Random tiny tie-break only.

            score += (
                rng.random()
                *
                0.000001
            )


            candidate_scores.append(
                (
                    score,
                    split,
                )
            )


        candidate_scores.sort()


        selected_split = (
            candidate_scores[
                0
            ][
                1
            ]
        )


        assignments[
            group_id
        ] = (
            selected_split
        )


        global_counts[
            selected_split
        ] += len(
            group_rows
        )


        group_classes = (
            group_breed_counts(
                group_rows
            )
        )


        for breed, count in (
            group_classes.items()
        ):

            breed_counts[
                breed
            ][
                selected_split
            ] += count


    final_score = (
        evaluate_final_assignment(
            global_counts=
                global_counts,

            breed_counts=
                breed_counts,

            global_targets=
                global_targets,

            breed_targets=
                breed_targets,

            breeds=
                breeds,
        )
    )


    return (
        assignments,
        global_counts,
        breed_counts,
        final_score,
    )


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 92)
    print(
        "BREEDVISION AI - GLOBAL CLASSIFIER V2 GROUP-AWARE SPLIT"
    )
    print("=" * 92)


    rows = load_csv(
        INPUT_MANIFEST
    )


    cattle_rows = [
        row

        for row in rows

        if (
            row[
                "species"
            ]
            ==
            "cattle"
        )
    ]


    buffalo_rows = [
        row

        for row in rows

        if (
            row[
                "species"
            ]
            ==
            "buffalo"
        )
    ]


    if not buffalo_rows:

        raise RuntimeError(
            "No buffalo rows found."
        )


    # =====================================================
    # CATTLE MUST ALREADY HAVE VALID SPLITS
    # =====================================================

    for row in cattle_rows:

        if (
            row[
                "split"
            ]
            not in
            set(
                SPLITS
            )
        ):

            raise RuntimeError(
                "Invalid preserved cattle split:\n"
                f"{row['image_path']}"
            )


    breeds = sorted(
        {
            row[
                "breed"
            ]

            for row in buffalo_rows
        }
    )


    groups = build_groups(
        buffalo_rows
    )


    (
        global_targets,
        breed_targets,
        breed_totals,
    ) = calculate_targets(
        buffalo_rows=
            buffalo_rows,

        breeds=
            breeds,
    )


    print()
    print(
        "Cattle images :",
        len(
            cattle_rows
        )
    )

    print(
        "Buffalo images:",
        len(
            buffalo_rows
        )
    )

    print(
        "Buffalo groups:",
        len(
            groups
        )
    )

    print(
        "Buffalo breeds:",
        breeds
    )


    # =====================================================
    # VALIDATE GROUP AVAILABILITY
    # =====================================================

    breed_group_counts = Counter()


    for (
        group_id,
        group_rows,
    ) in groups.items():

        breeds_in_group = set(
            row[
                "breed"
            ]
            for row in group_rows
        )


        for breed in breeds_in_group:

            breed_group_counts[
                breed
            ] += 1


    for breed in breeds:

        if (
            breed_group_counts[
                breed
            ]
            <
            3
        ):

            raise RuntimeError(
                f"{breed} has only "
                f"{breed_group_counts[breed]} groups. "
                f"At least 3 are required."
            )


    # =====================================================
    # RANDOMIZED SEARCH
    # =====================================================

    print()
    print(
        f"Searching {SEARCH_TRIALS} "
        f"group-aware split candidates..."
    )


    best_assignments = None
    best_global_counts = None
    best_breed_counts = None
    best_score = None
    best_trial = None


    for trial in range(
        SEARCH_TRIALS
    ):

        (
            assignments,
            global_counts,
            breed_counts,
            final_score,
        ) = generate_assignment(
            groups=
                groups,

            breeds=
                breeds,

            global_targets=
                global_targets,

            breed_targets=
                breed_targets,

            random_seed=
                RANDOM_SEED
                +
                trial,
        )


        if final_score is None:

            continue


        if (
            best_score is None
            or
            final_score
            <
            best_score
        ):

            best_score = (
                final_score
            )

            best_assignments = (
                assignments
            )

            best_global_counts = (
                global_counts
            )

            best_breed_counts = (
                breed_counts
            )

            best_trial = (
                trial
            )


    if best_assignments is None:

        raise RuntimeError(
            "Unable to produce a valid group-aware "
            "split where every buffalo breed appears "
            "in train, validation and test."
        )


    # =====================================================
    # APPLY SPLITS
    # =====================================================

    for row in buffalo_rows:

        group_id = (
            row[
                "group_id"
            ]
        )


        row[
            "split"
        ] = (
            best_assignments[
                group_id
            ]
        )


        row[
            "split_status"
        ] = (
            "phase6_global_group_aware_split"
        )


    # =====================================================
    # HARD GROUP LEAKAGE CHECK BEFORE SAVE
    # =====================================================

    group_splits = defaultdict(
        set
    )


    for row in buffalo_rows:

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

        if len(
            splits
        ) > 1
    }


    if leaking_groups:

        raise RuntimeError(
            "Internal error: generated split "
            "contains group leakage."
        )


    # =====================================================
    # RECOMBINE
    # =====================================================

    final_rows = (
        cattle_rows
        +
        buffalo_rows
    )


    final_rows.sort(
        key=lambda row:
            row[
                "record_id"
            ]
    )


    fieldnames = [
        "record_id",
        "image_path",
        "breed",
        "species",
        "class_index",
        "source_dataset",
        "sha256",
        "group_id",
        "group_origin",
        "split",
        "split_status",
    ]


    with OUTPUT_MANIFEST.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=
                fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            final_rows
        )


    # =====================================================
    # SUMMARY
    # =====================================================

    total_split_counts = Counter(
        row[
            "split"
        ]
        for row in final_rows
    )


    buffalo_split_counts = Counter(
        row[
            "split"
        ]
        for row in buffalo_rows
    )


    breed_summary = {}


    for breed in breeds:

        breed_rows = [
            row

            for row in buffalo_rows

            if (
                row[
                    "breed"
                ]
                ==
                breed
            )
        ]


        counts = Counter(
            row[
                "split"
            ]
            for row in breed_rows
        )


        breed_summary[
            breed
        ] = {

            "images":
                len(
                    breed_rows
                ),

            "groups":
                breed_group_counts[
                    breed
                ],

            "counts":
                dict(
                    counts
                ),

            "ratios": {

                split:
                    round(
                        counts[
                            split
                        ]
                        /
                        len(
                            breed_rows
                        ),
                        4,
                    )

                for split in SPLITS
            },
        }


    summary = {

        "phase":
            "Phase 6.7 - Global Buffalo Group-Aware Split",

        "random_seed":
            RANDOM_SEED,

        "search_trials":
            SEARCH_TRIALS,

        "selected_trial":
            best_trial,

        "optimization_score":
            best_score,

        "target_ratios":
            SPLIT_RATIOS,

        "total_images":
            len(
                final_rows
            ),

        "buffalo_images":
            len(
                buffalo_rows
            ),

        "buffalo_groups":
            len(
                groups
            ),

        "buffalo_group_leakage":
            len(
                leaking_groups
            ),

        "total_split_counts":
            dict(
                total_split_counts
            ),

        "buffalo_split_counts":
            dict(
                buffalo_split_counts
            ),

        "buffalo_breed_splits":
            breed_summary,

        "policy":
            (
                "All buffalo near-duplicate groups, "
                "including cross-class groups, are "
                "globally indivisible."
            ),
    }


    with OUTPUT_SUMMARY.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
        )


    # =====================================================
    # DISPLAY
    # =====================================================

    print()
    print("-" * 92)

    print(
        "Selected trial          :",
        best_trial
    )

    print(
        "Optimization score      :",
        round(
            best_score,
            6,
        )
    )

    print(
        "Buffalo group leakage   :",
        len(
            leaking_groups
        )
    )

    print(
        "Buffalo split counts    :",
        dict(
            buffalo_split_counts
        )
    )


    print()
    print("-" * 92)
    print("BUFFALO BREED SPLITS")
    print("-" * 92)


    for breed, info in (
        breed_summary.items()
    ):

        print()
        print(
            breed
        )

        print(
            " Images:",
            info[
                "images"
            ]
        )

        print(
            " Groups:",
            info[
                "groups"
            ]
        )

        print(
            " Counts:",
            info[
                "counts"
            ]
        )

        print(
            " Ratios:",
            info[
                "ratios"
            ]
        )


    print()
    print("=" * 92)
    print(
        "GLOBAL GROUP-AWARE SPLIT: PASS"
    )
    print("=" * 92)


if __name__ == "__main__":

    main()