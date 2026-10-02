from pathlib import Path
import csv
import json
from collections import defaultdict


# =========================================================
# BREEDVISION AI
# PHASE 4 - INDEPENDENT SPLIT LEAKAGE VALIDATION
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORTS_DIR = PROJECT_ROOT / "reports"
CONFIGS_DIR = PROJECT_ROOT / "configs"


SPLIT_MANIFEST = (
    REPORTS_DIR
    / "dataset_split_manifest.csv"
)

MASTER_MANIFEST = (
    REPORTS_DIR
    / "processed_master_manifest.csv"
)

NEAR_DUPLICATES = (
    REPORTS_DIR
    / "near_duplicate_pairs.csv"
)

DATASET_CONFIG = (
    CONFIGS_DIR
    / "dataset_config.json"
)


OUTPUT_JSON = (
    REPORTS_DIR
    / "split_leakage_audit.json"
)

OUTPUT_CSV = (
    REPORTS_DIR
    / "split_leakage_issues.csv"
)


def normalize_path(value):
    return str(
        Path(value).resolve()
    )


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


def main():

    print("=" * 82)
    print("BREEDVISION AI - SPLIT LEAKAGE AUDIT")
    print("=" * 82)


    split_rows = load_csv(
        SPLIT_MANIFEST
    )

    master_rows = load_csv(
        MASTER_MANIFEST
    )

    near_rows = load_csv(
        NEAR_DUPLICATES
    )

    config = load_json(
        DATASET_CONFIG
    )


    issues = []


    # =====================================================
    # BUILD SPLIT LOOKUP
    # =====================================================

    path_to_split = {}

    duplicate_manifest_paths = []


    for row in split_rows:

        path = normalize_path(
            row["image_path"]
        )

        split = (
            row["split"]
            .strip()
        )


        if path in path_to_split:

            duplicate_manifest_paths.append(
                path
            )

        else:

            path_to_split[path] = split


    # =====================================================
    # CHECK GROUP LEAKAGE
    # =====================================================

    group_splits = defaultdict(
        set
    )


    for row in split_rows:

        group_id = (
            row["group_id"]
            .strip()
        )

        split = (
            row["split"]
            .strip()
        )


        group_splits[
            group_id
        ].add(
            split
        )


    leaking_groups = {
        group_id: sorted(splits)

        for group_id, splits
        in group_splits.items()

        if len(splits) > 1
    }


    for group_id, splits in leaking_groups.items():

        issues.append(
            {
                "issue_type":
                    "near_duplicate_group_leakage",

                "identifier":
                    group_id,

                "details":
                    " | ".join(splits),
            }
        )


    # =====================================================
    # BUILD MASTER HASH LOOKUP
    # =====================================================

    path_to_hash = {}

    hash_paths = defaultdict(
        list
    )


    for row in master_rows:

        processed_path = normalize_path(
            row[
                "processed_path"
            ]
        )

        sha256 = (
            row["sha256"]
            .strip()
        )


        path_to_hash[
            processed_path
        ] = sha256


        hash_paths[
            sha256
        ].append(
            processed_path
        )


    # =====================================================
    # CHECK EXACT HASH ACROSS SPLITS
    # =====================================================

    hash_splits = defaultdict(
        set
    )


    for path, split in path_to_split.items():

        sha256 = path_to_hash.get(
            path
        )


        if sha256:

            hash_splits[
                sha256
            ].add(
                split
            )


    leaking_hashes = {
        sha256: sorted(splits)

        for sha256, splits
        in hash_splits.items()

        if len(splits) > 1
    }


    for sha256, splits in leaking_hashes.items():

        issues.append(
            {
                "issue_type":
                    "exact_hash_cross_split",

                "identifier":
                    sha256,

                "details":
                    " | ".join(splits),
            }
        )


    # =====================================================
    # CHECK NEAR-DUPLICATE PAIRS ACROSS SPLITS
    # =====================================================

    leaking_near_pairs = []


    for row in near_rows:

        image_a = normalize_path(
            row["image_a"]
        )

        image_b = normalize_path(
            row["image_b"]
        )


        split_a = path_to_split.get(
            image_a
        )

        split_b = path_to_split.get(
            image_b
        )


        if (
            split_a
            and split_b
            and split_a != split_b
        ):

            leaking_near_pairs.append(
                {
                    "image_a":
                        image_a,

                    "image_b":
                        image_b,

                    "split_a":
                        split_a,

                    "split_b":
                        split_b,

                    "distance":
                        row[
                            "hamming_distance"
                        ],
                }
            )


            issues.append(
                {
                    "issue_type":
                        "near_duplicate_pair_cross_split",

                    "identifier":
                        f"{image_a} <-> {image_b}",

                    "details":
                        f"{split_a} <-> {split_b}",
                }
            )


    # =====================================================
    # DUPLICATE MANIFEST PATHS
    # =====================================================

    for path in duplicate_manifest_paths:

        issues.append(
            {
                "issue_type":
                    "duplicate_manifest_path",

                "identifier":
                    path,

                "details":
                    "Same image appears more than once in split manifest.",
            }
        )


    # =====================================================
    # CHECK EVERY IMAGE EXISTS
    # =====================================================

    missing_files = []


    for path in path_to_split:

        if not Path(path).exists():

            missing_files.append(
                path
            )


            issues.append(
                {
                    "issue_type":
                        "missing_processed_file",

                    "identifier":
                        path,

                    "details":
                        "File referenced by split manifest does not exist.",
                }
            )


    # =====================================================
    # CLASS COVERAGE
    # =====================================================

    classes = config[
        "classes"
    ]


    class_split_counts = {
        breed: {
            "train": 0,
            "validation": 0,
            "test": 0,
        }

        for breed in classes
    }


    for row in split_rows:

        breed = (
            row["breed"]
            .strip()
        )

        split = (
            row["split"]
            .strip()
        )


        if (
            breed in class_split_counts
            and
            split in class_split_counts[
                breed
            ]
        ):

            class_split_counts[
                breed
            ][
                split
            ] += 1


    missing_class_splits = []


    for breed, counts in class_split_counts.items():

        for split, count in counts.items():

            if count == 0:

                missing_class_splits.append(
                    {
                        "breed":
                            breed,

                        "split":
                            split,
                    }
                )


                issues.append(
                    {
                        "issue_type":
                            "class_missing_from_split",

                        "identifier":
                            breed,

                        "details":
                            f"No images in {split}.",
                    }
                )


    # =====================================================
    # WRITE ISSUE CSV
    # =====================================================

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "issue_type",
                "identifier",
                "details",
            ],
        )

        writer.writeheader()

        writer.writerows(
            issues
        )


    # =====================================================
    # SUMMARY
    # =====================================================

    critical_issue_count = (
        len(leaking_groups)
        +
        len(leaking_hashes)
        +
        len(leaking_near_pairs)
        +
        len(duplicate_manifest_paths)
        +
        len(missing_files)
        +
        len(missing_class_splits)
    )


    status = (
        "PASS"
        if critical_issue_count == 0
        else
        "FAIL"
    )


    summary = {
        "status":
            status,

        "split_manifest_images":
            len(split_rows),

        "processed_master_images":
            len(master_rows),

        "duplicate_manifest_paths":
            len(
                duplicate_manifest_paths
            ),

        "group_leakage_count":
            len(
                leaking_groups
            ),

        "exact_hash_cross_split_count":
            len(
                leaking_hashes
            ),

        "near_duplicate_pair_cross_split_count":
            len(
                leaking_near_pairs
            ),

        "missing_processed_files":
            len(
                missing_files
            ),

        "missing_class_split_combinations":
            missing_class_splits,

        "class_split_counts":
            class_split_counts,

        "total_critical_issues":
            critical_issue_count,
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
    # TERMINAL
    # =====================================================

    print()

    print(
        "Split images                     :",
        len(split_rows),
    )

    print(
        "Duplicate manifest paths         :",
        len(
            duplicate_manifest_paths
        ),
    )

    print(
        "Near-duplicate group leakage     :",
        len(
            leaking_groups
        ),
    )

    print(
        "Exact hash cross-split leakage   :",
        len(
            leaking_hashes
        ),
    )

    print(
        "Near-duplicate pair leakage      :",
        len(
            leaking_near_pairs
        ),
    )

    print(
        "Missing files                    :",
        len(
            missing_files
        ),
    )

    print(
        "Missing class/split combinations :",
        len(
            missing_class_splits
        ),
    )


    print()
    print("=" * 82)
    print("LEAKAGE AUDIT STATUS:", status)
    print("=" * 82)


    print()
    print(
        "Summary:",
        OUTPUT_JSON
    )

    print(
        "Issues :",
        OUTPUT_CSV
    )


if __name__ == "__main__":
    main()