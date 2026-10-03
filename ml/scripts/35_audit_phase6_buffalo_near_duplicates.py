from pathlib import Path
import csv
import json

from PIL import Image
import imagehash


# =========================================================
# BREEDVISION AI
# PHASE 6.4
# BUFFALO PERCEPTUAL NEAR-DUPLICATE AUDIT
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


INPUT_CSV = (
    REPORTS_DIR
    / "phase6_buffalo_unique_candidates.csv"
)

CANDIDATE_CONFIG = (
    CONFIGS_DIR
    / "phase6_buffalo_candidates.json"
)


OUTPUT_PAIRS = (
    REPORTS_DIR
    / "phase6_buffalo_near_duplicate_pairs.csv"
)

OUTPUT_SUMMARY = (
    REPORTS_DIR
    / "phase6_buffalo_near_duplicate_summary.json"
)


PHASH_THRESHOLD = 4


# =========================================================
# HELPERS
# =========================================================


def load_json(path):

    if not path.exists():
        raise FileNotFoundError(
            f"Required file missing:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def load_csv(path):

    if not path.exists():
        raise FileNotFoundError(
            f"Required file missing:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        return list(
            csv.DictReader(file)
        )


def phash_to_int(hash_object):

    return int(
        str(hash_object),
        16,
    )


def hamming_distance(
    value_a,
    value_b,
):

    return (
        value_a
        ^
        value_b
    ).bit_count()


# =========================================================
# BK-TREE
# =========================================================


class BKNode:

    def __init__(
        self,
        hash_value,
        row_index,
    ):

        self.hash_value = hash_value
        self.row_index = row_index

        self.children = {}


class BKTree:

    def __init__(self):

        self.root = None


    def add(
        self,
        hash_value,
        row_index,
    ):

        if self.root is None:

            self.root = BKNode(
                hash_value,
                row_index,
            )

            return


        node = self.root


        while True:

            distance = hamming_distance(
                hash_value,
                node.hash_value,
            )


            if distance in node.children:

                node = (
                    node.children[
                        distance
                    ]
                )

            else:

                node.children[
                    distance
                ] = BKNode(
                    hash_value,
                    row_index,
                )

                break


    def query(
        self,
        hash_value,
        threshold,
    ):

        matches = []


        if self.root is None:

            return matches


        stack = [
            self.root
        ]


        while stack:

            node = stack.pop()


            distance = hamming_distance(
                hash_value,
                node.hash_value,
            )


            if distance <= threshold:

                matches.append(
                    (
                        node.row_index,
                        distance,
                    )
                )


            lower = (
                distance
                -
                threshold
            )

            upper = (
                distance
                +
                threshold
            )


            for child_distance, child in (
                node.children.items()
            ):

                if (
                    lower
                    <=
                    child_distance
                    <=
                    upper
                ):

                    stack.append(
                        child
                    )


        return matches


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 88)
    print(
        "BREEDVISION AI - PHASE 6 BUFFALO NEAR-DUPLICATE AUDIT"
    )
    print("=" * 88)


    rows = load_csv(
        INPUT_CSV
    )


    config = load_json(
        CANDIDATE_CONFIG
    )


    candidate_classes = set(
        config[
            "candidate_classes"
        ]
    )


    filtered_rows = [

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


    print()
    print(
        "Provisional buffalo classes:",
        sorted(
            candidate_classes
        )
    )

    print(
        "Candidate images:",
        len(
            filtered_rows
        )
    )


    tree = BKTree()

    processed_rows = []

    pairs = []

    failed_images = []


    # =====================================================
    # HASH + SEARCH
    # =====================================================


    total = len(
        filtered_rows
    )


    for index, row in enumerate(
        filtered_rows
    ):

        image_path = Path(
            row[
                "image_path"
            ]
        )


        try:

            with Image.open(
                image_path
            ) as image:

                image = image.convert(
                    "RGB"
                )

                perceptual_hash = (
                    imagehash.phash(
                        image
                    )
                )


        except Exception as exc:

            failed_images.append(
                {
                    "image_path":
                        str(
                            image_path
                        ),

                    "error":
                        str(
                            exc
                        ),
                }
            )

            continue


        hash_int = phash_to_int(
            perceptual_hash
        )


        matches = tree.query(
            hash_value=
                hash_int,

            threshold=
                PHASH_THRESHOLD,
        )


        for (
            previous_index,
            distance,
        ) in matches:

            previous = (
                processed_rows[
                    previous_index
                ]
            )


            pairs.append(
                {
                    "image_a":
                        previous[
                            "image_path"
                        ],

                    "breed_a":
                        previous[
                            "candidate_breed"
                        ],

                    "image_b":
                        row[
                            "image_path"
                        ],

                    "breed_b":
                        row[
                            "candidate_breed"
                        ],

                    "hamming_distance":
                        distance,

                    "cross_class":
                        (
                            previous[
                                "candidate_breed"
                            ]
                            !=
                            row[
                                "candidate_breed"
                            ]
                        ),
                }
            )


        processed_rows.append(
            row
        )


        tree.add(
            hash_value=
                hash_int,

            row_index=
                len(
                    processed_rows
                )
                -
                1,
        )


        completed = (
            index
            +
            1
        )


        if (
            completed % 250 == 0
            or
            completed == total
        ):

            print(
                f"  Processed "
                f"{completed}/{total}"
            )


    # =====================================================
    # SAVE PAIRS
    # =====================================================


    with OUTPUT_PAIRS.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        fieldnames = [
            "image_a",
            "breed_a",
            "image_b",
            "breed_b",
            "hamming_distance",
            "cross_class",
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
    # SUMMARY
    # =====================================================


    same_class_pairs = sum(

        1

        for pair in pairs

        if not pair[
            "cross_class"
        ]
    )


    cross_class_pairs = sum(

        1

        for pair in pairs

        if pair[
            "cross_class"
        ]
    )


    summary = {

        "phase":
            "Phase 6.4 - Buffalo Near Duplicate Audit",

        "phash_threshold":
            PHASH_THRESHOLD,

        "candidate_classes":
            sorted(
                candidate_classes
            ),

        "images_considered":
            len(
                filtered_rows
            ),

        "images_successfully_hashed":
            len(
                processed_rows
            ),

        "failed_images":
            len(
                failed_images
            ),

        "near_duplicate_pairs":
            len(
                pairs
            ),

        "same_class_near_duplicate_pairs":
            same_class_pairs,

        "cross_class_near_duplicate_pairs":
            cross_class_pairs,

        "policy": (
            "pHash distance <= 4 is treated as "
            "a near-duplicate candidate. "
            "Pairs are grouped for leakage prevention, "
            "not automatically deleted."
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
    print("-" * 88)

    print(
        "Hashed images            :",
        len(
            processed_rows
        )
    )

    print(
        "Near-duplicate pairs     :",
        len(
            pairs
        )
    )

    print(
        "Same-class pairs         :",
        same_class_pairs
    )

    print(
        "Cross-class pairs        :",
        cross_class_pairs
    )

    print(
        "Failed images            :",
        len(
            failed_images
        )
    )


    print()
    print("=" * 88)
    print(
        "PHASE 6.4 NEAR-DUPLICATE AUDIT: COMPLETE"
    )
    print("=" * 88)


if __name__ == "__main__":

    main()