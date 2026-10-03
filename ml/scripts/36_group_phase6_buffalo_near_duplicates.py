from pathlib import Path
import csv
import json
from collections import defaultdict, Counter


# =========================================================
# BREEDVISION AI
# PHASE 6.4B
# BUFFALO NEAR-DUPLICATE GROUPING
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

CONFIGS_DIR = (
    PROJECT_ROOT
    / "configs"
)


UNIQUE_CSV = (
    REPORTS_DIR
    / "phase6_buffalo_unique_candidates.csv"
)

PAIRS_CSV = (
    REPORTS_DIR
    / "phase6_buffalo_near_duplicate_pairs.csv"
)

CANDIDATE_CONFIG = (
    CONFIGS_DIR
    / "phase6_buffalo_candidates.json"
)


OUTPUT_GROUPS = (
    REPORTS_DIR
    / "phase6_buffalo_near_duplicate_groups.csv"
)

OUTPUT_SUMMARY = (
    REPORTS_DIR
    / "phase6_buffalo_near_duplicate_groups_summary.json"
)


# =========================================================
# UNION FIND
# =========================================================


class UnionFind:

    def __init__(
        self,
        values,
    ):

        self.parent = {
            value: value
            for value in values
        }

        self.rank = {
            value: 0
            for value in values
        }


    def find(
        self,
        value,
    ):

        if (
            self.parent[
                value
            ]
            !=
            value
        ):

            self.parent[
                value
            ] = self.find(
                self.parent[
                    value
                ]
            )


        return self.parent[
            value
        ]


    def union(
        self,
        a,
        b,
    ):

        root_a = self.find(
            a
        )

        root_b = self.find(
            b
        )


        if root_a == root_b:

            return


        if (
            self.rank[
                root_a
            ]
            <
            self.rank[
                root_b
            ]
        ):

            self.parent[
                root_a
            ] = root_b


        elif (
            self.rank[
                root_a
            ]
            >
            self.rank[
                root_b
            ]
        ):

            self.parent[
                root_b
            ] = root_a


        else:

            self.parent[
                root_b
            ] = root_a

            self.rank[
                root_a
            ] += 1


# =========================================================
# HELPERS
# =========================================================


def load_csv(path):

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        return list(
            csv.DictReader(file)
        )


def load_json(path):

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 88)
    print(
        "BREEDVISION AI - PHASE 6 BUFFALO NEAR-DUPLICATE GROUPING"
    )
    print("=" * 88)


    rows = load_csv(
        UNIQUE_CSV
    )


    pairs = load_csv(
        PAIRS_CSV
    )


    config = load_json(
        CANDIDATE_CONFIG
    )


    candidate_classes = set(
        config[
            "candidate_classes"
        ]
    )


    rows = [

        row

        for row in rows

        if (
            row[
                "candidate_breed"
            ]
            in
            candidate_classes
        )
    ]


    row_lookup = {

        row[
            "image_path"
        ]:
            row

        for row in rows
    }


    image_paths = sorted(
        row_lookup.keys()
    )


    union_find = UnionFind(
        image_paths
    )


    # =====================================================
    # UNION PAIRS
    # =====================================================


    valid_pairs = 0


    for pair in pairs:

        image_a = (
            pair[
                "image_a"
            ]
        )

        image_b = (
            pair[
                "image_b"
            ]
        )


        if (
            image_a
            in
            row_lookup
            and
            image_b
            in
            row_lookup
        ):

            union_find.union(
                image_a,
                image_b,
            )

            valid_pairs += 1


    # =====================================================
    # BUILD CONNECTED COMPONENTS
    # =====================================================


    components = defaultdict(
        list
    )


    for image_path in image_paths:

        root = union_find.find(
            image_path
        )

        components[
            root
        ].append(
            image_path
        )


    ordered_components = sorted(
        components.values(),
        key=lambda group:
            min(
                group
            ),
    )


    output_rows = []


    singleton_groups = 0

    same_class_groups = 0

    cross_class_groups = 0


    breed_group_ids = defaultdict(
        set
    )


    largest_group_per_breed = Counter()


    # =====================================================
    # ASSIGN IDs
    # =====================================================


    for index, group in enumerate(
        ordered_components,
        start=1,
    ):

        group_id = (
            f"BUF_NDG_"
            f"{index:06d}"
        )


        breeds = sorted(
            {
                row_lookup[
                    path
                ][
                    "candidate_breed"
                ]

                for path in group
            }
        )


        if len(
            group
        ) == 1:

            group_type = (
                "singleton"
            )

            singleton_groups += 1


        elif len(
            breeds
        ) == 1:

            group_type = (
                "same_class_near_duplicate"
            )

            same_class_groups += 1


        else:

            group_type = (
                "cross_class_near_duplicate"
            )

            cross_class_groups += 1


        for image_path in sorted(
            group
        ):

            row = (
                row_lookup[
                    image_path
                ]
            )


            breed = (
                row[
                    "candidate_breed"
                ]
            )


            breed_group_ids[
                breed
            ].add(
                group_id
            )


            largest_group_per_breed[
                breed
            ] = max(
                largest_group_per_breed[
                    breed
                ],
                len(
                    group
                ),
            )


            output_rows.append(
                {
                    "image_path":
                        image_path,

                    "candidate_breed":
                        breed,

                    "source_dataset":
                        row[
                            "source_dataset"
                        ],

                    "sha256":
                        row[
                            "sha256"
                        ],

                    "group_id":
                        group_id,

                    "group_size":
                        len(
                            group
                        ),

                    "group_type":
                        group_type,

                    "breeds_in_group":
                        " | ".join(
                            breeds
                        ),
                }
            )


    # =====================================================
    # WRITE CSV
    # =====================================================


    with OUTPUT_GROUPS.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        fieldnames = [
            "image_path",
            "candidate_breed",
            "source_dataset",
            "sha256",
            "group_id",
            "group_size",
            "group_type",
            "breeds_in_group",
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
    # SUMMARY
    # =====================================================


    breed_group_summary = {}


    for breed in sorted(
        candidate_classes
    ):

        breed_images = sum(

            1

            for row in output_rows

            if (
                row[
                    "candidate_breed"
                ]
                ==
                breed
            )
        )


        breed_group_summary[
            breed
        ] = {

            "images":
                breed_images,

            "distinct_near_duplicate_groups":
                len(
                    breed_group_ids[
                        breed
                    ]
                ),

            "largest_group_size":
                largest_group_per_breed[
                    breed
                ],
        }


    summary = {

        "phase":
            "Phase 6.4B - Buffalo Near Duplicate Grouping",

        "images":
            len(
                output_rows
            ),

        "input_near_duplicate_pairs":
            len(
                pairs
            ),

        "valid_pairs_used":
            valid_pairs,

        "total_groups":
            len(
                ordered_components
            ),

        "singleton_groups":
            singleton_groups,

        "same_class_near_duplicate_groups":
            same_class_groups,

        "cross_class_near_duplicate_groups":
            cross_class_groups,

        "breed_group_summary":
            breed_group_summary,

        "split_policy":
            (
                "All images sharing a near-duplicate "
                "group ID must remain in the same split."
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
    print(
        "Images                         :",
        len(
            output_rows
        )
    )

    print(
        "Total groups                   :",
        len(
            ordered_components
        )
    )

    print(
        "Singleton groups               :",
        singleton_groups
    )

    print(
        "Same-class near-dup groups     :",
        same_class_groups
    )

    print(
        "Cross-class near-dup groups    :",
        cross_class_groups
    )


    print()
    print("-" * 88)
    print("BREED GROUP COUNTS")
    print("-" * 88)


    for breed, info in (
        breed_group_summary.items()
    ):

        print(
            f"{breed:<20}"
            f" images={info['images']:<8}"
            f" groups={info['distinct_near_duplicate_groups']:<8}"
            f" largest={info['largest_group_size']}"
        )


    print()
    print("=" * 88)
    print(
        "PHASE 6.4 GROUPING: COMPLETE"
    )
    print("=" * 88)


if __name__ == "__main__":

    main()