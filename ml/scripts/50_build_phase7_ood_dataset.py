import csv
import json
import random
from collections import defaultdict
from pathlib import Path

import imagehash
from PIL import Image


# =========================================================
# BREEDVISION AI
# PHASE 7
# BUILD REAL OUT-OF-DISTRIBUTION DATASET
#
# OOD breeds:
# - Buffalo breeds held from classifier-v2
# - Exact-conflict-cleaned source images
# - Near duplicates grouped before splitting
#
# OOD split:
# - threshold_tuning
# - evaluation
# =========================================================


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


INPUT_CSV = (
    PROJECT_ROOT
    / "reports"
    / "phase6_buffalo_unique_candidates.csv"
)


FINAL_CLASS_CONFIG = (
    PROJECT_ROOT
    / "configs"
    / "phase6_buffalo_final_classes.json"
)


OUTPUT_MANIFEST = (
    PROJECT_ROOT
    / "reports"
    / "phase7_ood_manifest.csv"
)


OUTPUT_SUMMARY = (
    PROJECT_ROOT
    / "reports"
    / "phase7_ood_summary.json"
)


PHASH_THRESHOLD = 4

TUNING_RATIO = 0.60

RANDOM_SEED = 42


# =========================================================
# HELPERS
# =========================================================


def load_json(path):

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def load_csv(path):

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        return list(
            csv.DictReader(file)
        )


class UnionFind:

    def __init__(
        self,
        size,
    ):

        self.parent = list(
            range(size)
        )

        self.rank = [
            0
            for _ in range(size)
        ]


    def find(
        self,
        value,
    ):

        while (
            self.parent[
                value
            ]
            !=
            value
        ):

            self.parent[
                value
            ] = (
                self.parent[
                    self.parent[
                        value
                    ]
                ]
            )

            value = (
                self.parent[
                    value
                ]
            )

        return value


    def union(
        self,
        left,
        right,
    ):

        root_left = self.find(
            left
        )

        root_right = self.find(
            right
        )


        if (
            root_left
            ==
            root_right
        ):

            return


        if (
            self.rank[
                root_left
            ]
            <
            self.rank[
                root_right
            ]
        ):

            self.parent[
                root_left
            ] = (
                root_right
            )

        elif (
            self.rank[
                root_left
            ]
            >
            self.rank[
                root_right
            ]
        ):

            self.parent[
                root_right
            ] = (
                root_left
            )

        else:

            self.parent[
                root_right
            ] = (
                root_left
            )

            self.rank[
                root_left
            ] += 1


def compute_phash(
    image_path,
):

    with Image.open(
        image_path
    ) as image:

        image = image.convert(
            "RGB"
        )

        return imagehash.phash(
            image
        )


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 92)
    print(
        "BREEDVISION AI - PHASE 7 REAL OOD DATASET"
    )
    print("=" * 92)


    if not INPUT_CSV.exists():

        raise FileNotFoundError(
            f"Missing input:\n{INPUT_CSV}"
        )


    config = load_json(
        FINAL_CLASS_CONFIG
    )


    held_classes = sorted(
        config[
            "held_buffalo_classes"
        ]
    )


    if not held_classes:

        raise RuntimeError(
            "No held buffalo classes available "
            "for OOD evaluation."
        )


    print()
    print(
        "OOD breeds:",
        held_classes
    )


    all_rows = load_csv(
        INPUT_CSV
    )


    rows = [

        row

        for row in all_rows

        if (
            row[
                "candidate_breed"
            ]
            in
            held_classes
        )
    ]


    if not rows:

        raise RuntimeError(
            "No OOD images found."
        )


    print(
        "OOD images before pHash:",
        len(
            rows
        )
    )


    # =====================================================
    # COMPUTE PHASH
    # =====================================================


    valid_rows = []

    failed_rows = []


    for index, row in enumerate(
        rows,
        start=1,
    ):

        path = Path(
            row[
                "image_path"
            ]
        )


        try:

            phash = compute_phash(
                path
            )


            new_row = dict(
                row
            )


            new_row[
                "phash"
            ] = str(
                phash
            )


            valid_rows.append(
                new_row
            )


        except Exception as error:

            failed_rows.append(
                {
                    "image_path":
                        str(
                            path
                        ),

                    "error":
                        str(
                            error
                        ),
                }
            )


        if (
            index % 25 == 0
            or
            index
            ==
            len(
                rows
            )
        ):

            print(
                f"Hashed "
                f"{index}/"
                f"{len(rows)}"
            )


    if not valid_rows:

        raise RuntimeError(
            "No valid OOD images after hashing."
        )


    # =====================================================
    # NEAR-DUPLICATE GROUPING
    #
    # Small dataset, so O(n^2) is acceptable here.
    # =====================================================


    union_find = UnionFind(
        len(
            valid_rows
        )
    )


    hashes = [

        imagehash.hex_to_hash(
            row[
                "phash"
            ]
        )

        for row in valid_rows
    ]


    near_duplicate_pairs = 0


    for left in range(
        len(
            valid_rows
        )
    ):

        for right in range(
            left + 1,
            len(
                valid_rows
            )
        ):

            distance = (
                hashes[
                    left
                ]
                -
                hashes[
                    right
                ]
            )


            if (
                distance
                <=
                PHASH_THRESHOLD
            ):

                union_find.union(
                    left,
                    right,
                )

                near_duplicate_pairs += 1


    components = defaultdict(
        list
    )


    for index in range(
        len(
            valid_rows
        )
    ):

        root = union_find.find(
            index
        )

        components[
            root
        ].append(
            index
        )


    # =====================================================
    # GROUP IDs
    # =====================================================


    groups = []


    for group_number, indices in enumerate(
        sorted(
            components.values(),
            key=lambda values:
                min(values),
        ),
        start=1,
    ):

        group_id = (
            f"OOD_NDG_"
            f"{group_number:05d}"
        )


        breeds = sorted(
            {
                valid_rows[
                    index
                ][
                    "candidate_breed"
                ]

                for index in indices
            }
        )


        groups.append(
            {
                "group_id":
                    group_id,

                "indices":
                    indices,

                "size":
                    len(
                        indices
                    ),

                "breeds":
                    breeds,
            }
        )


        for index in indices:

            valid_rows[
                index
            ][
                "ood_group_id"
            ] = (
                group_id
            )


    # =====================================================
    # SPLIT GROUPS PER BREED
    # =====================================================


    rng = random.Random(
        RANDOM_SEED
    )


    group_lookup = {

        group[
            "group_id"
        ]:
            group

        for group in groups
    }


    groups_by_breed = defaultdict(
        list
    )


    for group in groups:

        for breed in group[
            "breeds"
        ]:

            groups_by_breed[
                breed
            ].append(
                group[
                    "group_id"
                ]
            )


    assignment = {}


    for breed in held_classes:

        breed_groups = list(
            dict.fromkeys(
                groups_by_breed[
                    breed
                ]
            )
        )


        rng.shuffle(
            breed_groups
        )


        if len(
            breed_groups
        ) < 2:

            raise RuntimeError(
                f"OOD breed '{breed}' has "
                f"fewer than 2 near-duplicate groups."
            )


        total_images = sum(

            sum(

                1

                for index in group_lookup[
                    group_id
                ][
                    "indices"
                ]

                if (
                    valid_rows[
                        index
                    ][
                        "candidate_breed"
                    ]
                    ==
                    breed
                )
            )

            for group_id in breed_groups
        )


        target_tuning = (
            total_images
            *
            TUNING_RATIO
        )


        current_tuning = 0


        breed_groups.sort(
            key=lambda group_id:
                group_lookup[
                    group_id
                ][
                    "size"
                ],
            reverse=True,
        )


        for group_id in breed_groups:

            if group_id in assignment:
                continue


            group = (
                group_lookup[
                    group_id
                ]
            )


            breed_count = sum(

                1

                for index in group[
                    "indices"
                ]

                if (
                    valid_rows[
                        index
                    ][
                        "candidate_breed"
                    ]
                    ==
                    breed
                )
            )


            if (
                current_tuning
                <
                target_tuning
            ):

                assignment[
                    group_id
                ] = (
                    "threshold_tuning"
                )

                current_tuning += (
                    breed_count
                )

            else:

                assignment[
                    group_id
                ] = (
                    "evaluation"
                )


    # Anything not assigned due to cross-breed groups
    # gets evaluation conservatively.

    for group in groups:

        if (
            group[
                "group_id"
            ]
            not in
            assignment
        ):

            assignment[
                group[
                    "group_id"
                ]
            ] = (
                "evaluation"
            )


    # =====================================================
    # APPLY SPLITS
    # =====================================================


    output_rows = []


    for row in valid_rows:

        group_id = (
            row[
                "ood_group_id"
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
                        "candidate_breed"
                    ],

                "species":
                    "buffalo",

                "ood_status":
                    "unknown_to_classifier_v2",

                "ood_group_id":
                    group_id,

                "ood_split":
                    assignment[
                        group_id
                    ],

                "sha256":
                    row[
                        "sha256"
                    ],

                "phash":
                    row[
                        "phash"
                    ],

                "source_dataset":
                    row[
                        "source_dataset"
                    ],
            }
        )


    # =====================================================
    # VALIDATION
    # =====================================================


    group_splits = defaultdict(
        set
    )


    for row in output_rows:

        group_splits[
            row[
                "ood_group_id"
            ]
        ].add(
            row[
                "ood_split"
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
            "OOD group leakage detected."
        )


    breed_split_counts = defaultdict(
        lambda: defaultdict(int)
    )


    for row in output_rows:

        breed_split_counts[
            row[
                "breed"
            ]
        ][
            row[
                "ood_split"
            ]
        ] += 1


    for breed in held_classes:

        if (
            breed_split_counts[
                breed
            ][
                "threshold_tuning"
            ]
            ==
            0
        ):

            raise RuntimeError(
                f"{breed} missing threshold_tuning data."
            )


        if (
            breed_split_counts[
                breed
            ][
                "evaluation"
            ]
            ==
            0
        ):

            raise RuntimeError(
                f"{breed} missing evaluation data."
            )


    # =====================================================
    # SAVE
    # =====================================================


    fieldnames = [
        "image_path",
        "breed",
        "species",
        "ood_status",
        "ood_group_id",
        "ood_split",
        "sha256",
        "phash",
        "source_dataset",
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
            output_rows
        )


    tuning_count = sum(

        1

        for row in output_rows

        if (
            row[
                "ood_split"
            ]
            ==
            "threshold_tuning"
        )
    )


    evaluation_count = sum(

        1

        for row in output_rows

        if (
            row[
                "ood_split"
            ]
            ==
            "evaluation"
        )
    )


    summary = {

        "phase":
            "Phase 7 - Real OOD Dataset",

        "ood_breeds":
            held_classes,

        "total_ood_images":
            len(
                output_rows
            ),

        "threshold_tuning_images":
            tuning_count,

        "evaluation_images":
            evaluation_count,

        "near_duplicate_threshold":
            PHASH_THRESHOLD,

        "near_duplicate_pairs":
            near_duplicate_pairs,

        "near_duplicate_groups":
            len(
                groups
            ),

        "group_leakage_count":
            len(
                leaking_groups
            ),

        "failed_images":
            failed_rows,

        "breed_split_counts": {

            breed:
                dict(
                    counts
                )

            for breed, counts
            in breed_split_counts.items()
        },

        "policy":
            (
                "Held buffalo breeds are treated as "
                "real unknown/OOD classes. Near-duplicate "
                "groups remain entirely within one OOD split."
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


    print()
    print("-" * 92)

    print(
        "Total OOD images      :",
        len(
            output_rows
        )
    )

    print(
        "Threshold tuning      :",
        tuning_count
    )

    print(
        "Final OOD evaluation  :",
        evaluation_count
    )

    print(
        "Near-duplicate groups :",
        len(
            groups
        )
    )

    print(
        "Group leakage         :",
        len(
            leaking_groups
        )
    )


    print()
    print("Per-breed OOD split:")


    for breed in held_classes:

        print(
            breed,
            "=>",
            dict(
                breed_split_counts[
                    breed
                ]
            ),
        )


    print()
    print("=" * 92)
    print(
        "PHASE 7 OOD DATASET: PASS"
    )
    print("=" * 92)


if __name__ == "__main__":

    main()