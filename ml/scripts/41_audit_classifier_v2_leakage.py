from pathlib import Path
import csv
import json
from collections import defaultdict, Counter


# =========================================================
# BREEDVISION AI
# PHASE 6.7B
# INDEPENDENT CLASSIFIER V2 LEAKAGE AUDIT
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


MANIFEST_PATH = (
    REPORTS_DIR
    / "classifier_v2_final_manifest.csv"
)

CONFIG_PATH = (
    CONFIGS_DIR
    / "classifier_v2_dataset_config.json"
)

OUTPUT_JSON = (
    REPORTS_DIR
    / "classifier_v2_leakage_audit.json"
)


VALID_SPLITS = {
    "train",
    "validation",
    "test",
}


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


def main():

    print("=" * 90)
    print(
        "BREEDVISION AI - CLASSIFIER V2 LEAKAGE AUDIT"
    )
    print("=" * 90)


    if not MANIFEST_PATH.exists():

        raise FileNotFoundError(
            MANIFEST_PATH
        )


    rows = load_csv(
        MANIFEST_PATH
    )


    config = load_json(
        CONFIG_PATH
    )


    expected_classes = set(
        config[
            "classes"
        ]
    )


    errors = []
    warnings = []


    # =====================================================
    # VALID SPLITS
    # =====================================================


    invalid_split_rows = [

        row

        for row in rows

        if (
            row[
                "split"
            ]
            not in
            VALID_SPLITS
        )
    ]


    if invalid_split_rows:

        errors.append(
            f"{len(invalid_split_rows)} rows "
            f"have invalid splits."
        )


    # =====================================================
    # DUPLICATE IMAGE PATH
    # =====================================================


    path_splits = defaultdict(
        set
    )


    for row in rows:

        path_splits[
            row[
                "image_path"
            ]
        ].add(
            row[
                "split"
            ]
        )


    duplicate_paths = [

        path

        for path, splits
        in path_splits.items()

        if len(
            splits
        ) > 1
    ]


    if duplicate_paths:

        errors.append(
            f"{len(duplicate_paths)} image paths "
            f"appear across multiple splits."
        )


    # =====================================================
    # GROUP LEAKAGE
    # =====================================================


    group_splits = defaultdict(
        set
    )


    for row in rows:

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

        errors.append(
            f"{len(leaking_groups)} group IDs "
            f"cross dataset splits."
        )


    # =====================================================
    # SHA256 LEAKAGE
    # =====================================================


    hash_splits = defaultdict(
        set
    )


    for row in rows:

        sha256 = (
            row[
                "sha256"
            ].strip()
        )


        if not sha256:

            continue


        hash_splits[
            sha256
        ].add(
            row[
                "split"
            ]
        )


    leaking_hashes = {

        sha256:
            sorted(
                splits
            )

        for sha256, splits
        in hash_splits.items()

        if len(
            splits
        ) > 1
    }


    if leaking_hashes:

        errors.append(
            f"{len(leaking_hashes)} SHA256 hashes "
            f"cross dataset splits."
        )


    # =====================================================
    # CLASS PRESENCE
    # =====================================================


    class_split_counts = defaultdict(
        Counter
    )


    for row in rows:

        class_split_counts[
            row[
                "breed"
            ]
        ][
            row[
                "split"
            ]
        ] += 1


    missing_class_splits = {}


    for breed in sorted(
        expected_classes
    ):

        missing = [

            split

            for split
            in VALID_SPLITS

            if (
                class_split_counts[
                    breed
                ][
                    split
                ]
                ==
                0
            )
        ]


        if missing:

            missing_class_splits[
                breed
            ] = (
                sorted(
                    missing
                )
            )


    if missing_class_splits:

        errors.append(
            f"{len(missing_class_splits)} classes "
            f"are missing from one or more splits."
        )


    # =====================================================
    # CLASS INDEX CONSISTENCY
    # =====================================================


    class_to_index = (
        config[
            "class_to_index"
        ]
    )


    wrong_class_indices = []


    for row in rows:

        breed = (
            row[
                "breed"
            ]
        )


        expected_index = str(
            class_to_index[
                breed
            ]
        )


        if (
            row[
                "class_index"
            ]
            !=
            expected_index
        ):

            wrong_class_indices.append(
                row[
                    "record_id"
                ]
            )


    if wrong_class_indices:

        errors.append(
            f"{len(wrong_class_indices)} rows "
            f"have inconsistent class indices."
        )


    # =====================================================
    # COUNTS
    # =====================================================


    split_counts = Counter(
        row[
            "split"
        ]
        for row in rows
    )


    species_counts = Counter(
        row[
            "species"
        ]
        for row in rows
    )


    # =====================================================
    # STATUS
    # =====================================================


    status = (
        "PASS"
        if not errors
        else
        "FAIL"
    )


    result = {

        "phase":
            "Phase 6.7B - Classifier V2 Leakage Audit",

        "status":
            status,

        "total_images":
            len(
                rows
            ),

        "split_counts":
            dict(
                split_counts
            ),

        "species_counts":
            dict(
                species_counts
            ),

        "num_classes":
            len(
                expected_classes
            ),

        "group_leakage_count":
            len(
                leaking_groups
            ),

        "sha256_leakage_count":
            len(
                leaking_hashes
            ),

        "duplicate_path_cross_split_count":
            len(
                duplicate_paths
            ),

        "missing_class_split_count":
            len(
                missing_class_splits
            ),

        "wrong_class_index_count":
            len(
                wrong_class_indices
            ),

        "leaking_groups":
            leaking_groups,

        "missing_class_splits":
            missing_class_splits,

        "errors":
            errors,

        "warnings":
            warnings,
    }


    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
        )


    print()
    print(
        "Total images               :",
        len(
            rows
        )
    )

    print(
        "Split counts               :",
        dict(
            split_counts
        )
    )

    print(
        "Group leakage              :",
        len(
            leaking_groups
        )
    )

    print(
        "SHA256 leakage             :",
        len(
            leaking_hashes
        )
    )

    print(
        "Path cross-split duplicates:",
        len(
            duplicate_paths
        )
    )

    print(
        "Missing class/splits       :",
        len(
            missing_class_splits
        )
    )

    print(
        "Wrong class indices        :",
        len(
            wrong_class_indices
        )
    )


    print()
    print("=" * 90)
    print(
        "CLASSIFIER V2 LEAKAGE STATUS:",
        status
    )
    print("=" * 90)


    if errors:

        print()

        for error in errors:

            print(
                "[ERROR]",
                error
            )


if __name__ == "__main__":

    main()