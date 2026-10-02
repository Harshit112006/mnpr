from pathlib import Path
import csv
import json
from collections import defaultdict

from PIL import Image
import imagehash
from tqdm import tqdm


# =========================================================
# BREEDVISION AI
# PHASE 4 - NEAR DUPLICATE AUDIT
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


OUTPUT_CSV = (
    REPORTS_DIR
    / "near_duplicate_pairs.csv"
)

OUTPUT_JSON = (
    REPORTS_DIR
    / "near_duplicate_summary.json"
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
# PHASH SETTINGS
# =========================================================

# pHash produces a 64-bit perceptual fingerprint.
#
# Distance:
# 0 = extremely visually similar hash
# Small values = likely near duplicate
#
# We use a conservative threshold of 4 for the first audit.
HAMMING_THRESHOLD = 4


def hamming_distance(value_a, value_b):
    return (
        value_a ^ value_b
    ).bit_count()


# =========================================================
# BK-TREE
#
# Allows efficient Hamming-distance searching without
# comparing every image against every other image.
# =========================================================


class BKNode:

    def __init__(self, hash_value):
        self.hash_value = hash_value

        self.children = {}

        self.image_indexes = []


class BKTree:

    def __init__(self):
        self.root = None


    def insert(
        self,
        hash_value,
        image_index,
    ):

        if self.root is None:

            self.root = BKNode(
                hash_value
            )

            self.root.image_indexes.append(
                image_index
            )

            return


        node = self.root


        while True:

            distance = hamming_distance(
                hash_value,
                node.hash_value,
            )


            if distance == 0:

                node.image_indexes.append(
                    image_index
                )

                return


            if distance in node.children:

                node = node.children[
                    distance
                ]

            else:

                new_node = BKNode(
                    hash_value
                )

                new_node.image_indexes.append(
                    image_index
                )

                node.children[
                    distance
                ] = new_node

                return


    def search(
        self,
        query_hash,
        max_distance,
    ):

        results = []


        if self.root is None:
            return results


        stack = [
            self.root
        ]


        while stack:

            node = stack.pop()


            distance = hamming_distance(
                query_hash,
                node.hash_value,
            )


            if distance <= max_distance:

                results.append(
                    (
                        distance,
                        node.image_indexes,
                    )
                )


            lower = (
                distance
                -
                max_distance
            )

            upper = (
                distance
                +
                max_distance
            )


            for (
                edge_distance,
                child,
            ) in node.children.items():

                if (
                    lower
                    <=
                    edge_distance
                    <=
                    upper
                ):

                    stack.append(
                        child
                    )


        return results


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 80)
    print("BREEDVISION AI - NEAR DUPLICATE AUDIT")
    print("=" * 80)


    if not MASTER_ROOT.exists():

        raise FileNotFoundError(
            "\nProcessed master dataset not found:\n"
            f"{MASTER_ROOT}\n\n"
            "Run 13_build_processed_master.py first."
        )


    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    # =====================================================
    # DISCOVER IMAGES
    # =====================================================

    image_files = sorted(
        [
            path

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
        "Processed images found:",
        len(image_files),
    )

    print(
        "pHash Hamming threshold:",
        HAMMING_THRESHOLD,
    )


    # =====================================================
    # COMPUTE PHASH
    # =====================================================

    records = []

    failed_images = 0


    for image_path in tqdm(
        image_files,
        desc="Computing perceptual hashes",
    ):

        try:

            with Image.open(
                image_path
            ) as image:

                image = image.convert(
                    "RGB"
                )


                phash = imagehash.phash(
                    image
                )


                phash_int = int(
                    str(phash),
                    16,
                )


                records.append(
                    {
                        "path":
                            image_path,

                        "breed":
                            image_path.parent.name,

                        "phash":
                            str(phash),

                        "phash_int":
                            phash_int,
                    }
                )


        except Exception as error:

            failed_images += 1

            print(
                f"\nFailed to hash: "
                f"{image_path}\n"
                f"{error}"
            )


    # =====================================================
    # FIND NEAR DUPLICATES
    # =====================================================

    tree = BKTree()

    pairs = []


    same_class_pairs = 0

    cross_class_pairs = 0


    print()

    for current_index, current in enumerate(
        tqdm(
            records,
            desc="Searching near duplicates",
        )
    ):

        matches = tree.search(
            current[
                "phash_int"
            ],
            HAMMING_THRESHOLD,
        )


        for (
            distance,
            matching_indexes,
        ) in matches:

            for previous_index in matching_indexes:

                previous = records[
                    previous_index
                ]


                same_class = (
                    previous[
                        "breed"
                    ]
                    ==
                    current[
                        "breed"
                    ]
                )


                if same_class:

                    status = (
                        "same_class_near_duplicate"
                    )

                    same_class_pairs += 1

                else:

                    status = (
                        "cross_class_near_duplicate"
                    )

                    cross_class_pairs += 1


                pairs.append(
                    {
                        "image_a":
                            str(
                                previous[
                                    "path"
                                ].resolve()
                            ),

                        "breed_a":
                            previous[
                                "breed"
                            ],

                        "image_b":
                            str(
                                current[
                                    "path"
                                ].resolve()
                            ),

                        "breed_b":
                            current[
                                "breed"
                            ],

                        "phash_a":
                            previous[
                                "phash"
                            ],

                        "phash_b":
                            current[
                                "phash"
                            ],

                        "hamming_distance":
                            distance,

                        "status":
                            status,
                    }
                )


        tree.insert(
            current[
                "phash_int"
            ],
            current_index,
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
            "image_a",
            "breed_a",
            "image_b",
            "breed_b",
            "phash_a",
            "phash_b",
            "hamming_distance",
            "status",
        ]


        writer = csv.DictWriter(
            file,
            fieldnames=
                fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            pairs
        )


    # =====================================================
    # PAIRS BY DISTANCE
    # =====================================================

    distance_counts = defaultdict(
        int
    )


    cross_class_combinations = defaultdict(
        int
    )


    for row in pairs:

        distance_counts[
            str(
                row[
                    "hamming_distance"
                ]
            )
        ] += 1


        if (
            row[
                "status"
            ]
            ==
            "cross_class_near_duplicate"
        ):

            breeds = sorted(
                [
                    row[
                        "breed_a"
                    ],
                    row[
                        "breed_b"
                    ],
                ]
            )


            key = (
                breeds[0]
                +
                " <-> "
                +
                breeds[1]
            )


            cross_class_combinations[
                key
            ] += 1


    # =====================================================
    # SUMMARY
    # =====================================================

    summary = {
        "processed_images_checked":
            len(records),

        "failed_images":
            failed_images,

        "phash_hamming_threshold":
            HAMMING_THRESHOLD,

        "total_near_duplicate_pairs":
            len(pairs),

        "same_class_near_duplicate_pairs":
            same_class_pairs,

        "cross_class_near_duplicate_pairs":
            cross_class_pairs,

        "pairs_by_hamming_distance":
            dict(
                sorted(
                    distance_counts.items(),
                    key=lambda item:
                    int(item[0]),
                )
            ),

        "cross_class_breed_combinations":
            dict(
                sorted(
                    cross_class_combinations.items(),
                    key=lambda item:
                    -item[1],
                )
            ),

        "policy": {
            "current_action":
                "Audit only. No files removed.",

            "cross_class_near_duplicates":
                "Require review before train/validation/test split.",

            "same_class_near_duplicates":
                (
                    "Must be grouped before splitting so visually "
                    "similar images cannot leak across dataset splits."
                ),
        },
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
    print("=" * 80)
    print("NEAR DUPLICATE RESULT")
    print("=" * 80)


    print(
        "Images checked                   :",
        len(records),
    )

    print(
        "Failed images                    :",
        failed_images,
    )

    print(
        "Near-duplicate pairs             :",
        len(pairs),
    )

    print(
        "Same-class pairs                 :",
        same_class_pairs,
    )

    print(
        "Cross-class pairs                :",
        cross_class_pairs,
    )


    print()
    print("-" * 80)
    print("PAIRS BY HAMMING DISTANCE")
    print("-" * 80)


    for distance, count in sorted(
        distance_counts.items(),
        key=lambda item:
        int(item[0]),
    ):

        print(
            f"Distance {distance:<3} : {count}"
        )


    if cross_class_combinations:

        print()
        print("-" * 80)
        print("CROSS-CLASS NEAR-DUPLICATE COMBINATIONS")
        print("-" * 80)


        for (
            combination,
            count,
        ) in sorted(
            cross_class_combinations.items(),
            key=lambda item:
            -item[1],
        )[:20]:

            print(
                f"{combination:<50} : {count}"
            )


    print()

    print(
        "Pair report :",
        OUTPUT_CSV
    )

    print(
        "Summary     :",
        OUTPUT_JSON
    )


    print()
    print(
        "No images were modified or deleted."
    )


if __name__ == "__main__":
    main()