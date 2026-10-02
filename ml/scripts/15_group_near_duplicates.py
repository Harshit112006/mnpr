from pathlib import Path
import csv
import json
from collections import defaultdict


# =========================================================
# BREEDVISION AI
# PHASE 4 - NEAR DUPLICATE GROUPING
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MASTER_ROOT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "master"
)

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)


PAIR_CSV = (
    REPORTS_DIR
    / "near_duplicate_pairs.csv"
)

OUTPUT_CSV = (
    REPORTS_DIR
    / "near_duplicate_groups.csv"
)

SUMMARY_JSON = (
    REPORTS_DIR
    / "near_duplicate_groups_summary.json"
)


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
}


# =========================================================
# UNION FIND
# =========================================================


class UnionFind:

    def __init__(self):
        self.parent = {}
        self.rank = {}


    def add(self, item):

        if item not in self.parent:
            self.parent[item] = item
            self.rank[item] = 0


    def find(self, item):

        if self.parent[item] != item:

            self.parent[item] = self.find(
                self.parent[item]
            )

        return self.parent[item]


    def union(self, item_a, item_b):

        self.add(item_a)
        self.add(item_b)

        root_a = self.find(item_a)
        root_b = self.find(item_b)

        if root_a == root_b:
            return


        rank_a = self.rank[root_a]
        rank_b = self.rank[root_b]


        if rank_a < rank_b:

            self.parent[root_a] = root_b


        elif rank_a > rank_b:

            self.parent[root_b] = root_a


        else:

            self.parent[root_b] = root_a
            self.rank[root_a] += 1


def normalize_path(value):
    return str(
        Path(value).resolve()
    )


def main():

    print("=" * 80)
    print("BREEDVISION AI - NEAR DUPLICATE GROUPING")
    print("=" * 80)


    if not MASTER_ROOT.exists():

        raise FileNotFoundError(
            f"\nProcessed master dataset not found:\n"
            f"{MASTER_ROOT}"
        )


    if not PAIR_CSV.exists():

        raise FileNotFoundError(
            f"\nNear-duplicate pair report not found:\n"
            f"{PAIR_CSV}\n\n"
            "Run 14_audit_near_duplicates.py first."
        )


    # =====================================================
    # ALL PROCESSED IMAGES
    # =====================================================

    images = sorted(
        [
            path.resolve()

            for path in MASTER_ROOT.rglob("*")

            if (
                path.is_file()
                and path.suffix.lower()
                in IMAGE_EXTENSIONS
            )
        ]
    )


    print()
    print(
        "Processed images discovered:",
        len(images),
    )


    union_find = UnionFind()


    for image_path in images:

        union_find.add(
            str(image_path)
        )


    # =====================================================
    # READ NEAR-DUPLICATE PAIRS
    # =====================================================

    pair_count = 0


    with PAIR_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)


        for row in reader:

            image_a = normalize_path(
                row["image_a"]
            )

            image_b = normalize_path(
                row["image_b"]
            )


            union_find.union(
                image_a,
                image_b,
            )

            pair_count += 1


    # =====================================================
    # BUILD GROUPS
    # =====================================================

    groups = defaultdict(list)


    for image_path in images:

        path_string = str(
            image_path
        )

        root = union_find.find(
            path_string
        )

        groups[root].append(
            image_path
        )


    # =====================================================
    # CREATE DETERMINISTIC GROUP IDs
    # =====================================================

    sorted_groups = sorted(
        groups.values(),
        key=lambda group:
        str(
            sorted(group)[0]
        ),
    )


    rows = []

    grouped_images = 0
    singleton_images = 0
    cross_class_groups = 0
    same_class_groups = 0


    for group_index, group in enumerate(
        sorted_groups,
        start=1,
    ):

        group_id = (
            f"NDG_{group_index:06d}"
        )


        group = sorted(group)


        breeds = sorted(
            {
                path.parent.name
                for path in group
            }
        )


        group_size = len(group)


        if group_size == 1:

            group_type = "singleton"

            singleton_images += 1


        elif len(breeds) == 1:

            group_type = (
                "same_class_near_duplicate_group"
            )

            same_class_groups += 1

            grouped_images += group_size


        else:

            group_type = (
                "cross_class_near_duplicate_group"
            )

            cross_class_groups += 1

            grouped_images += group_size


        for image_path in group:

            rows.append(
                {
                    "group_id":
                        group_id,

                    "image_path":
                        str(
                            image_path.resolve()
                        ),

                    "breed":
                        image_path.parent.name,

                    "group_size":
                        group_size,

                    "group_breeds":
                        " | ".join(
                            breeds
                        ),

                    "group_type":
                        group_type,

                    "must_stay_together":
                        True,
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
            "group_id",
            "image_path",
            "breed",
            "group_size",
            "group_breeds",
            "group_type",
            "must_stay_together",
        ]


        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


    # =====================================================
    # SUMMARY
    # =====================================================

    multi_image_groups = [
        group

        for group in sorted_groups

        if len(group) > 1
    ]


    largest_group = max(
        (
            len(group)
            for group in sorted_groups
        ),
        default=0,
    )


    summary = {
        "processed_images":
            len(images),

        "near_duplicate_pairs_loaded":
            pair_count,

        "total_groups":
            len(sorted_groups),

        "multi_image_groups":
            len(
                multi_image_groups
            ),

        "same_class_near_duplicate_groups":
            same_class_groups,

        "cross_class_near_duplicate_groups":
            cross_class_groups,

        "singleton_images":
            singleton_images,

        "images_inside_multi_image_groups":
            grouped_images,

        "largest_group_size":
            largest_group,

        "split_policy":
            (
                "All images sharing a group_id must remain "
                "inside the same train, validation or test split."
            ),
    }


    with SUMMARY_JSON.open(
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
    print("=" * 80)
    print("GROUPING RESULT")
    print("=" * 80)


    print(
        "Processed images                 :",
        len(images),
    )

    print(
        "Near-duplicate pairs loaded      :",
        pair_count,
    )

    print(
        "Total groups                     :",
        len(sorted_groups),
    )

    print(
        "Multi-image groups               :",
        len(
            multi_image_groups
        ),
    )

    print(
        "Same-class near-duplicate groups :",
        same_class_groups,
    )

    print(
        "Cross-class near-duplicate groups:",
        cross_class_groups,
    )

    print(
        "Singleton images                 :",
        singleton_images,
    )

    print(
        "Largest group size               :",
        largest_group,
    )


    print()
    print(
        "CSV:",
        OUTPUT_CSV
    )

    print(
        "Summary:",
        SUMMARY_JSON
    )


    print()
    print(
        "No images were modified or deleted."
    )


if __name__ == "__main__":
    main()