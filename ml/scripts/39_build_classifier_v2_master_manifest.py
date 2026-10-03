from pathlib import Path
import csv
import json
from collections import Counter


# =========================================================
# BREEDVISION AI
# PHASE 6.6A
# BUILD CLASSIFIER V2 MASTER MANIFEST
#
# Cattle:
#   - preserve existing v1 train/validation/test split
#   - preserve leakage grouping if available
#
# Buffalo:
#   - include only final frozen buffalo classes
#   - preserve near-duplicate group IDs
#   - split remains "pending"
#
# No source images are modified.
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


CATTLE_MANIFEST = (
    REPORTS_DIR
    / "final_dataset_manifest.csv"
)

BUFFALO_GROUPS = (
    REPORTS_DIR
    / "phase6_buffalo_near_duplicate_groups.csv"
)

V2_CONFIG = (
    CONFIGS_DIR
    / "classifier_v2_dataset_config.json"
)

FINAL_BUFFALO_CONFIG = (
    CONFIGS_DIR
    / "phase6_buffalo_final_classes.json"
)


OUTPUT_MANIFEST = (
    REPORTS_DIR
    / "classifier_v2_master_manifest.csv"
)

OUTPUT_SUMMARY = (
    REPORTS_DIR
    / "classifier_v2_master_summary.json"
)


# =========================================================
# HELPERS
# =========================================================


def load_json(path):

    if not path.exists():

        raise FileNotFoundError(
            f"Required JSON missing:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def load_csv(path):

    if not path.exists():

        raise FileNotFoundError(
            f"Required CSV missing:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        return list(
            csv.DictReader(file)
        )


def first_existing_key(
    row,
    candidates,
):

    for key in candidates:

        if key in row:

            return key

    return None


def get_required_column(
    sample_row,
    candidates,
    description,
):

    key = first_existing_key(
        sample_row,
        candidates,
    )

    if key is None:

        raise RuntimeError(
            f"Could not detect {description} column.\n"
            f"Expected one of: {candidates}\n"
            f"Available columns: {list(sample_row.keys())}"
        )

    return key


def get_optional_column(
    sample_row,
    candidates,
):

    return first_existing_key(
        sample_row,
        candidates,
    )


def normalize_split(value):

    value = (
        str(value)
        .strip()
        .lower()
    )

    mapping = {
        "train": "train",
        "training": "train",

        "val": "validation",
        "valid": "validation",
        "validation": "validation",

        "test": "test",
        "testing": "test",
    }

    return mapping.get(
        value,
        value,
    )


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 90)
    print(
        "BREEDVISION AI - CLASSIFIER V2 MASTER MANIFEST"
    )
    print("=" * 90)


    v2_config = load_json(
        V2_CONFIG
    )

    buffalo_config = load_json(
        FINAL_BUFFALO_CONFIG
    )


    cattle_rows = load_csv(
        CATTLE_MANIFEST
    )

    buffalo_rows = load_csv(
        BUFFALO_GROUPS
    )


    if not cattle_rows:

        raise RuntimeError(
            "Cattle manifest is empty."
        )


    if not buffalo_rows:

        raise RuntimeError(
            "Buffalo group manifest is empty."
        )


    class_to_index = (
        v2_config[
            "class_to_index"
        ]
    )


    final_buffalo_classes = set(
        buffalo_config[
            "final_buffalo_classes"
        ]
    )


    cattle_classes = set(
        v2_config[
            "cattle_classes"
        ]
    )


    # =====================================================
    # DETECT CATTLE MANIFEST COLUMNS
    # =====================================================


    cattle_sample = (
        cattle_rows[0]
    )


    cattle_path_key = get_required_column(
        cattle_sample,
        [
            "image_path",
            "path",
            "filepath",
            "file_path",
        ],
        "cattle image path",
    )


    cattle_breed_key = get_required_column(
        cattle_sample,
        [
            "breed",
            "class_name",
            "label",
            "normalized_label",
            "candidate_breed",
        ],
        "cattle breed",
    )


    cattle_split_key = get_required_column(
        cattle_sample,
        [
            "split",
            "dataset_split",
            "final_split",
        ],
        "cattle split",
    )


    cattle_group_key = get_optional_column(
        cattle_sample,
        [
            "group_id",
            "near_duplicate_group",
            "duplicate_group_id",
            "leakage_group_id",
        ],
    )


    cattle_source_key = get_optional_column(
        cattle_sample,
        [
            "source_dataset",
            "source",
            "dataset_source",
        ],
    )


    cattle_sha_key = get_optional_column(
        cattle_sample,
        [
            "sha256",
            "hash",
            "file_hash",
        ],
    )


    print()
    print("Detected cattle columns:")
    print(
        " image path :",
        cattle_path_key
    )
    print(
        " breed      :",
        cattle_breed_key
    )
    print(
        " split      :",
        cattle_split_key
    )
    print(
        " group      :",
        cattle_group_key
    )
    print(
        " source     :",
        cattle_source_key
    )
    print(
        " sha256     :",
        cattle_sha_key
    )


    # =====================================================
    # NORMALIZE CATTLE ROWS
    # =====================================================


    master_rows = []

    skipped_cattle = []

    cattle_split_counts = Counter()

    cattle_class_counts = Counter()


    for index, row in enumerate(
        cattle_rows,
        start=1,
    ):

        breed = (
            row[
                cattle_breed_key
            ]
            .strip()
        )


        if breed not in cattle_classes:

            skipped_cattle.append(
                {
                    "reason":
                        "breed_not_in_v2_cattle_config",

                    "breed":
                        breed,

                    "image_path":
                        row[
                            cattle_path_key
                        ],
                }
            )

            continue


        image_path = (
            row[
                cattle_path_key
            ]
            .strip()
        )


        split = normalize_split(
            row[
                cattle_split_key
            ]
        )


        if split not in {
            "train",
            "validation",
            "test",
        }:

            raise RuntimeError(
                f"Invalid cattle split '{split}' "
                f"for image:\n{image_path}"
            )


        if cattle_group_key:

            original_group = (
                row[
                    cattle_group_key
                ]
                .strip()
            )

        else:

            original_group = ""


        if not original_group:

            original_group = (
                f"UNIQUE_{index:08d}"
            )


        group_id = (
            "CATTLE_"
            +
            original_group
        )


        source = (
            row[
                cattle_source_key
            ].strip()

            if cattle_source_key
            else
            "phase4_cattle_master"
        )


        sha256 = (
            row[
                cattle_sha_key
            ].strip()

            if cattle_sha_key
            else
            ""
        )


        master_rows.append(
            {
                "record_id":
                    "",

                "image_path":
                    image_path,

                "breed":
                    breed,

                "species":
                    "cattle",

                "class_index":
                    class_to_index[
                        breed
                    ],

                "source_dataset":
                    source,

                "sha256":
                    sha256,

                "group_id":
                    group_id,

                "group_origin":
                    "phase4_cattle",

                "split":
                    split,

                "split_status":
                    "preserved_from_v1",
            }
        )


        cattle_split_counts[
            split
        ] += 1


        cattle_class_counts[
            breed
        ] += 1


    # =====================================================
    # NORMALIZE BUFFALO ROWS
    # =====================================================


    buffalo_class_counts = Counter()

    buffalo_group_counts = Counter()

    skipped_buffalo = []


    for row in buffalo_rows:

        breed = (
            row[
                "candidate_breed"
            ]
            .strip()
        )


        if breed not in final_buffalo_classes:

            continue


        if breed not in class_to_index:

            skipped_buffalo.append(
                {
                    "reason":
                        "breed_missing_from_v2_class_map",

                    "breed":
                        breed,

                    "image_path":
                        row[
                            "image_path"
                        ],
                }
            )

            continue


        original_group = (
            row[
                "group_id"
            ]
            .strip()
        )


        if not original_group:

            raise RuntimeError(
                "Buffalo row has empty group_id:\n"
                f"{row['image_path']}"
            )


        group_id = (
            "BUFFALO_"
            +
            original_group
        )


        master_rows.append(
            {
                "record_id":
                    "",

                "image_path":
                    row[
                        "image_path"
                    ].strip(),

                "breed":
                    breed,

                "species":
                    "buffalo",

                "class_index":
                    class_to_index[
                        breed
                    ],

                "source_dataset":
                    row[
                        "source_dataset"
                    ].strip(),

                "sha256":
                    row[
                        "sha256"
                    ].strip(),

                "group_id":
                    group_id,

                "group_origin":
                    "phase6_buffalo",

                "split":
                    "pending",

                "split_status":
                    "awaiting_group_split",
            }
        )


        buffalo_class_counts[
            breed
        ] += 1


        buffalo_group_counts[
            breed
        ] += 0


    # =====================================================
    # SORT + RECORD IDS
    # =====================================================


    master_rows.sort(
        key=lambda row: (
            row[
                "species"
            ],
            row[
                "breed"
            ],
            row[
                "image_path"
            ],
        )
    )


    for index, row in enumerate(
        master_rows,
        start=1,
    ):

        row[
            "record_id"
        ] = (
            f"BV2_{index:07d}"
        )


    # =====================================================
    # VALIDATION
    # =====================================================


    duplicate_paths = []

    seen_paths = set()


    for row in master_rows:

        image_path = (
            row[
                "image_path"
            ]
        )


        if image_path in seen_paths:

            duplicate_paths.append(
                image_path
            )

        seen_paths.add(
            image_path
        )


    if duplicate_paths:

        raise RuntimeError(
            "Duplicate image paths detected "
            "in v2 master manifest.\n"
            f"Count: {len(duplicate_paths)}"
        )


    invalid_classes = [

        row[
            "breed"
        ]

        for row in master_rows

        if (
            row[
                "breed"
            ]
            not in
            class_to_index
        )
    ]


    if invalid_classes:

        raise RuntimeError(
            "Unknown classes found in master manifest."
        )


    # =====================================================
    # WRITE MASTER CSV
    # =====================================================


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
            master_rows
        )


    # =====================================================
    # SUMMARY
    # =====================================================


    species_counts = Counter(
        row[
            "species"
        ]
        for row in master_rows
    )


    total_class_counts = Counter(
        row[
            "breed"
        ]
        for row in master_rows
    )


    pending_rows = sum(
        1
        for row in master_rows
        if (
            row[
                "split"
            ]
            ==
            "pending"
        )
    )


    summary = {

        "phase":
            "Phase 6.6A - Classifier V2 Master Manifest",

        "classifier_version":
            "v2",

        "total_images":
            len(
                master_rows
            ),

        "species_counts":
            dict(
                species_counts
            ),

        "class_counts":
            dict(
                sorted(
                    total_class_counts.items()
                )
            ),

        "num_classes":
            len(
                class_to_index
            ),

        "cattle_classes":
            sorted(
                cattle_classes
            ),

        "buffalo_classes":
            sorted(
                final_buffalo_classes
            ),

        "cattle_split_counts_preserved":
            dict(
                cattle_split_counts
            ),

        "pending_buffalo_split_rows":
            pending_rows,

        "duplicate_image_paths":
            len(
                duplicate_paths
            ),

        "skipped_cattle_rows":
            len(
                skipped_cattle
            ),

        "skipped_buffalo_rows":
            len(
                skipped_buffalo
            ),

        "policy": {
            "cattle_split":
                (
                    "Preserved from Phase 4/5 "
                    "leakage-safe v1 dataset."
                ),

            "buffalo_split":
                (
                    "Pending. Will be assigned "
                    "group-wise in Phase 6.7."
                ),

            "source_images_modified":
                False,

            "phase5_dataset_modified":
                False,
        },
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
    print("-" * 90)

    print(
        "Total v2 images          :",
        len(
            master_rows
        )
    )

    print(
        "Cattle images            :",
        species_counts[
            "cattle"
        ]
    )

    print(
        "Buffalo images           :",
        species_counts[
            "buffalo"
        ]
    )

    print(
        "Total classes            :",
        len(
            class_to_index
        )
    )

    print(
        "Pending buffalo splits   :",
        pending_rows
    )

    print(
        "Duplicate image paths    :",
        len(
            duplicate_paths
        )
    )


    print()
    print("-" * 90)
    print("CATTLE SPLITS PRESERVED")
    print("-" * 90)


    for split in [
        "train",
        "validation",
        "test",
    ]:

        print(
            f"{split:<12}: "
            f"{cattle_split_counts[split]}"
        )


    print()
    print("-" * 90)
    print("CLASS COUNTS")
    print("-" * 90)


    for breed in sorted(
        total_class_counts.keys()
    ):

        species = (
            "buffalo"
            if breed in final_buffalo_classes
            else
            "cattle"
        )


        print(
            f"{breed:<20}"
            f"{total_class_counts[breed]:>8}"
            f"   {species}"
        )


    print()
    print("=" * 90)
    print(
        "CLASSIFIER V2 MASTER MANIFEST: PASS"
    )
    print("=" * 90)


    print()
    print(
        "Manifest:"
    )

    print(
        OUTPUT_MANIFEST
    )

    print()
    print(
        "Summary:"
    )

    print(
        OUTPUT_SUMMARY
    )


if __name__ == "__main__":

    main()