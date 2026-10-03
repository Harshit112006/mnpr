from pathlib import Path
import csv
import hashlib
import json
from collections import defaultdict, Counter


# =========================================================
# BREEDVISION AI
# PHASE 6.2
# BUFFALO EXACT DUPLICATE + LABEL CONFLICT AUDIT
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


INPUT_CSV = (
    REPORTS_DIR
    / "phase6_buffalo_candidate_inventory.csv"
)


OUTPUT_DUPLICATES_CSV = (
    REPORTS_DIR
    / "phase6_buffalo_exact_duplicates.csv"
)


OUTPUT_CONFLICTS_CSV = (
    REPORTS_DIR
    / "phase6_buffalo_cross_class_conflicts.csv"
)


OUTPUT_UNIQUE_CSV = (
    REPORTS_DIR
    / "phase6_buffalo_unique_candidates.csv"
)


OUTPUT_SUMMARY_JSON = (
    REPORTS_DIR
    / "phase6_buffalo_duplicate_summary.json"
)


# =========================================================
# HELPERS
# =========================================================


def parse_bool(value):

    return (
        str(value)
        .strip()
        .lower()
        in {
            "true",
            "1",
            "yes",
        }
    )


def sha256_file(path):

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(
                chunk
            )

    return digest.hexdigest()


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 88)
    print(
        "BREEDVISION AI - PHASE 6 BUFFALO DUPLICATE AUDIT"
    )
    print("=" * 88)


    if not INPUT_CSV.exists():

        raise FileNotFoundError(
            f"Previous Phase 6 inventory missing:\n"
            f"{INPUT_CSV}"
        )


    # =====================================================
    # LOAD ELIGIBLE AUDIT ROWS
    #
    # Only:
    # - readable
    # - >= 224x224
    # =====================================================


    with INPUT_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        rows = list(
            csv.DictReader(file)
        )


    usable_rows = []


    for row in rows:

        if (
            parse_bool(
                row[
                    "readable"
                ]
            )
            and
            parse_bool(
                row[
                    "minimum_size_pass"
                ]
            )
        ):

            usable_rows.append(
                row
            )


    print()
    print(
        "Candidate inventory rows:",
        len(
            rows
        )
    )

    print(
        "Readable >=224 rows   :",
        len(
            usable_rows
        )
    )


    # =====================================================
    # HASH FILES
    # =====================================================


    hash_groups = defaultdict(
        list
    )


    missing_files = []


    print()
    print(
        "Calculating SHA256 hashes..."
    )


    total = len(
        usable_rows
    )


    for index, row in enumerate(
        usable_rows,
        start=1,
    ):

        image_path = Path(
            row[
                "image_path"
            ]
        )


        if not image_path.exists():

            missing_files.append(
                str(
                    image_path
                )
            )

            continue


        sha256 = sha256_file(
            image_path
        )


        enriched = dict(
            row
        )


        enriched[
            "sha256"
        ] = sha256


        hash_groups[
            sha256
        ].append(
            enriched
        )


        if (
            index % 250 == 0
            or
            index == total
        ):

            print(
                f"  Hashed {index}/{total}"
            )


    # =====================================================
    # CLASSIFY DUPLICATE GROUPS
    # =====================================================


    duplicate_rows = []

    conflict_rows = []

    unique_rows = []


    exact_duplicate_groups = 0

    same_class_duplicate_groups = 0

    cross_class_conflict_groups = 0


    same_class_removed_images = 0

    cross_class_conflict_images = 0


    breed_raw_counts = Counter()

    breed_unique_counts = Counter()

    breed_conflict_counts = Counter()


    for row in usable_rows:

        breed_raw_counts[
            row[
                "candidate_breed"
            ]
        ] += 1


    # =====================================================
    # PROCESS EACH HASH GROUP
    # =====================================================


    duplicate_group_id = 0

    conflict_group_id = 0


    for sha256, group in (
        hash_groups.items()
    ):

        breeds = sorted(
            {
                row[
                    "candidate_breed"
                ]
                for row in group
            }
        )


        sources = sorted(
            {
                row[
                    "source_dataset"
                ]
                for row in group
            }
        )


        # -------------------------------------------------
        # UNIQUE IMAGE
        # -------------------------------------------------

        if len(
            group
        ) == 1:

            row = dict(
                group[0]
            )

            row[
                "duplicate_status"
            ] = "unique"

            unique_rows.append(
                row
            )


            breed_unique_counts[
                row[
                    "candidate_breed"
                ]
            ] += 1

            continue


        # -------------------------------------------------
        # DUPLICATE GROUP
        # -------------------------------------------------

        exact_duplicate_groups += 1


        # -------------------------------------------------
        # SAME CLASS DUPLICATE
        #
        # Keep deterministic first path only.
        # -------------------------------------------------

        if len(
            breeds
        ) == 1:

            same_class_duplicate_groups += 1

            duplicate_group_id += 1


            ordered_group = sorted(
                group,
                key=lambda row:
                    row[
                        "image_path"
                    ],
            )


            keeper = dict(
                ordered_group[0]
            )


            keeper[
                "duplicate_status"
            ] = (
                "same_class_duplicate_keeper"
            )


            unique_rows.append(
                keeper
            )


            breed_unique_counts[
                keeper[
                    "candidate_breed"
                ]
            ] += 1


            for row_index, row in enumerate(
                ordered_group
            ):

                duplicate_rows.append(
                    {
                        "duplicate_group_id":
                            (
                                f"BDUP_"
                                f"{duplicate_group_id:06d}"
                            ),

                        "sha256":
                            sha256,

                        "candidate_breed":
                            row[
                                "candidate_breed"
                            ],

                        "source_dataset":
                            row[
                                "source_dataset"
                            ],

                        "image_path":
                            row[
                                "image_path"
                            ],

                        "group_size":
                            len(
                                ordered_group
                            ),

                        "keeper":
                            row_index == 0,
                    }
                )


            same_class_removed_images += (
                len(
                    ordered_group
                )
                - 1
            )


        # -------------------------------------------------
        # CROSS CLASS EXACT CONFLICT
        #
        # Exclude ENTIRE hash group.
        # -------------------------------------------------

        else:

            cross_class_conflict_groups += 1

            conflict_group_id += 1


            cross_class_conflict_images += (
                len(
                    group
                )
            )


            for row in group:

                breed_conflict_counts[
                    row[
                        "candidate_breed"
                    ]
                ] += 1


                conflict_rows.append(
                    {
                        "conflict_group_id":
                            (
                                f"BCONFLICT_"
                                f"{conflict_group_id:06d}"
                            ),

                        "sha256":
                            sha256,

                        "candidate_breed":
                            row[
                                "candidate_breed"
                            ],

                        "source_dataset":
                            row[
                                "source_dataset"
                            ],

                        "image_path":
                            row[
                                "image_path"
                            ],

                        "group_size":
                            len(
                                group
                            ),

                        "breeds_in_group":
                            " | ".join(
                                breeds
                            ),

                        "sources_in_group":
                            " | ".join(
                                sources
                            ),

                        "action":
                            (
                                "exclude_pending_review"
                            ),
                    }
                )


    # =====================================================
    # WRITE SAME-CLASS DUPLICATES
    # =====================================================


    with OUTPUT_DUPLICATES_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        fieldnames = [
            "duplicate_group_id",
            "sha256",
            "candidate_breed",
            "source_dataset",
            "image_path",
            "group_size",
            "keeper",
        ]


        writer = csv.DictWriter(
            file,
            fieldnames=
                fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            duplicate_rows
        )


    # =====================================================
    # WRITE CROSS CLASS CONFLICTS
    # =====================================================


    with OUTPUT_CONFLICTS_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        fieldnames = [
            "conflict_group_id",
            "sha256",
            "candidate_breed",
            "source_dataset",
            "image_path",
            "group_size",
            "breeds_in_group",
            "sources_in_group",
            "action",
        ]


        writer = csv.DictWriter(
            file,
            fieldnames=
                fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            conflict_rows
        )


    # =====================================================
    # WRITE UNIQUE TRAINING CANDIDATES
    # =====================================================


    unique_rows.sort(
        key=lambda row: (
            row[
                "candidate_breed"
            ],
            row[
                "source_dataset"
            ],
            row[
                "image_path"
            ],
        )
    )


    unique_fieldnames = [
        "source_dataset",
        "candidate_breed",
        "image_path",
        "readable",
        "width",
        "height",
        "minimum_size_pass",
        "error",
        "sha256",
        "duplicate_status",
    ]


    with OUTPUT_UNIQUE_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=
                unique_fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            unique_rows
        )


    # =====================================================
    # SOURCE DISTRIBUTION AFTER CLEANING
    # =====================================================


    source_unique_counts = defaultdict(
        Counter
    )


    for row in unique_rows:

        source_unique_counts[
            row[
                "source_dataset"
            ]
        ][
            row[
                "candidate_breed"
            ]
        ] += 1


    # =====================================================
    # FINAL BREED SUMMARY
    # =====================================================


    breed_summary = {}


    all_breeds = sorted(
        set(
            breed_raw_counts.keys()
        )
        |
        set(
            breed_unique_counts.keys()
        )
        |
        set(
            breed_conflict_counts.keys()
        )
    )


    for breed in all_breeds:

        unique_count = (
            breed_unique_counts[
                breed
            ]
        )


        if unique_count >= 500:

            strength = "strong"

        elif unique_count >= 200:

            strength = "usable"

        elif unique_count >= 100:

            strength = "weak"

        else:

            strength = "insufficient"


        breed_summary[
            breed
        ] = {

            "usable_before_exact_dedup":
                breed_raw_counts[
                    breed
                ],

            "unique_after_exact_dedup":
                unique_count,

            "cross_class_conflict_images":
                breed_conflict_counts[
                    breed
                ],

            "post_dedup_strength":
                strength,
        }


    # =====================================================
    # SUMMARY JSON
    # =====================================================


    summary = {

        "phase":
            "Phase 6.2 - Buffalo Exact Duplicate Audit",

        "usable_images_before_exact_dedup":
            len(
                hash_groups
            )
            +
            same_class_removed_images
            +
            (
                cross_class_conflict_images
                -
                cross_class_conflict_groups
            ),

        "hashed_files":
            sum(
                len(
                    group
                )
                for group in hash_groups.values()
            ),

        "missing_files":
            len(
                missing_files
            ),

        "exact_duplicate_groups":
            exact_duplicate_groups,

        "same_class_duplicate_groups":
            same_class_duplicate_groups,

        "same_class_duplicate_images_removed":
            same_class_removed_images,

        "cross_class_conflict_groups":
            cross_class_conflict_groups,

        "cross_class_conflict_images_excluded":
            cross_class_conflict_images,

        "unique_training_candidates":
            len(
                unique_rows
            ),

        "breed_summary":
            breed_summary,

        "source_distribution_after_dedup": {

            source:
                dict(
                    counts
                )

            for source, counts
            in source_unique_counts.items()
        },

        "policy": {

            "same_class_exact_duplicates":
                (
                    "Keep one deterministic copy."
                ),

            "cross_class_exact_duplicates":
                (
                    "Exclude entire hash group "
                    "pending manual review."
                ),

            "raw_data_modified":
                False,
        },
    }


    with OUTPUT_SUMMARY_JSON.open(
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
    print("-" * 88)
    print("DUPLICATE AUDIT RESULTS")
    print("-" * 88)


    print(
        "Hashed files                    :",
        summary[
            "hashed_files"
        ]
    )

    print(
        "Missing files                   :",
        len(
            missing_files
        )
    )

    print(
        "Exact duplicate groups          :",
        exact_duplicate_groups
    )

    print(
        "Same-class duplicate groups     :",
        same_class_duplicate_groups
    )

    print(
        "Duplicate copies removed        :",
        same_class_removed_images
    )

    print(
        "Cross-class conflict groups     :",
        cross_class_conflict_groups
    )

    print(
        "Cross-class images excluded     :",
        cross_class_conflict_images
    )

    print(
        "Unique training candidates      :",
        len(
            unique_rows
        )
    )


    print()
    print("-" * 88)
    print("POST-DEDUP BREED COUNTS")
    print("-" * 88)


    print(
        f"{'Breed':<20}"
        f"{'Before':>12}"
        f"{'Unique':>12}"
        f"{'Conflicts':>12}"
        f"{'Strength':>16}"
    )


    for breed, info in (
        breed_summary.items()
    ):

        print(
            f"{breed:<20}"
            f"{info['usable_before_exact_dedup']:>12}"
            f"{info['unique_after_exact_dedup']:>12}"
            f"{info['cross_class_conflict_images']:>12}"
            f"{info['post_dedup_strength']:>16}"
        )


    print()
    print("=" * 88)
    print(
        "PHASE 6.2 DUPLICATE AUDIT: COMPLETE"
    )
    print("=" * 88)


    print()
    print(
        "Summary:"
    )

    print(
        OUTPUT_SUMMARY_JSON
    )


if __name__ == "__main__":

    main()