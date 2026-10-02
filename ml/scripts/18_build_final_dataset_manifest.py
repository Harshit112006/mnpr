from pathlib import Path
import csv
import json
from collections import defaultdict


# =========================================================
# BREEDVISION AI
# PHASE 4 - FINAL DATASET MANIFEST
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORTS_DIR = PROJECT_ROOT / "reports"
CONFIGS_DIR = PROJECT_ROOT / "configs"


MASTER_MANIFEST = (
    REPORTS_DIR
    / "processed_master_manifest.csv"
)

SPLIT_MANIFEST = (
    REPORTS_DIR
    / "dataset_split_manifest.csv"
)

CLASS_TO_INDEX_FILE = (
    CONFIGS_DIR
    / "class_to_index.json"
)

SPECIES_MAPPING_FILE = (
    CONFIGS_DIR
    / "species_mapping.json"
)


OUTPUT_CSV = (
    REPORTS_DIR
    / "final_dataset_manifest.csv"
)

OUTPUT_JSON = (
    REPORTS_DIR
    / "final_dataset_summary.json"
)


def normalize_path(value):
    return str(
        Path(value).resolve()
    )


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

    print("=" * 82)
    print("BREEDVISION AI - FINAL DATASET MANIFEST")
    print("=" * 82)


    master_rows = load_csv(
        MASTER_MANIFEST
    )

    split_rows = load_csv(
        SPLIT_MANIFEST
    )

    class_to_index = load_json(
        CLASS_TO_INDEX_FILE
    )

    species_mapping = load_json(
        SPECIES_MAPPING_FILE
    )


    # =====================================================
    # SPLIT LOOKUP
    # =====================================================

    split_lookup = {}


    for row in split_rows:

        path = normalize_path(
            row[
                "image_path"
            ]
        )


        split_lookup[
            path
        ] = {
            "split":
                row[
                    "split"
                ],

            "group_id":
                row[
                    "group_id"
                ],

            "group_size":
                row[
                    "group_size"
                ],

            "group_type":
                row[
                    "group_type"
                ],
        }


    # =====================================================
    # FINAL ROWS
    # =====================================================

    final_rows = []

    missing_split_rows = 0


    for row in master_rows:

        processed_path = normalize_path(
            row[
                "processed_path"
            ]
        )


        split_info = split_lookup.get(
            processed_path
        )


        if split_info is None:

            missing_split_rows += 1

            continue


        breed = (
            row[
                "normalized_breed"
            ]
        )


        final_rows.append(
            {
                "image_path":
                    processed_path,

                "breed":
                    breed,

                "class_index":
                    class_to_index[
                        breed
                    ],

                "species":
                    species_mapping[
                        breed
                    ],

                "split":
                    split_info[
                        "split"
                    ],

                "group_id":
                    split_info[
                        "group_id"
                    ],

                "group_size":
                    split_info[
                        "group_size"
                    ],

                "group_type":
                    split_info[
                        "group_type"
                    ],

                "source_dataset":
                    row[
                        "source_dataset"
                    ],

                "source_path":
                    row[
                        "source_path"
                    ],

                "original_label":
                    row[
                        "original_label"
                    ],

                "sha256":
                    row[
                        "sha256"
                    ],

                "width":
                    row[
                        "width"
                    ],

                "height":
                    row[
                        "height"
                    ],

                "file_size_bytes":
                    row[
                        "file_size_bytes"
                    ],
            }
        )


    # =====================================================
    # SORT
    # =====================================================

    split_order = {
        "train": 0,
        "validation": 1,
        "test": 2,
    }


    final_rows.sort(
        key=lambda row: (
            split_order[
                row[
                    "split"
                ]
            ],
            int(
                row[
                    "class_index"
                ]
            ),
            row[
                "image_path"
            ],
        )
    )


    # =====================================================
    # SAVE CSV
    # =====================================================

    fieldnames = [
        "image_path",
        "breed",
        "class_index",
        "species",
        "split",
        "group_id",
        "group_size",
        "group_type",
        "source_dataset",
        "source_path",
        "original_label",
        "sha256",
        "width",
        "height",
        "file_size_bytes",
    ]


    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            final_rows
        )


    # =====================================================
    # SUMMARY
    # =====================================================

    split_counts = defaultdict(
        int
    )

    class_counts = defaultdict(
        int
    )

    species_counts = defaultdict(
        int
    )


    for row in final_rows:

        split_counts[
            row[
                "split"
            ]
        ] += 1

        class_counts[
            row[
                "breed"
            ]
        ] += 1

        species_counts[
            row[
                "species"
            ]
        ] += 1


    summary = {
        "total_images":
            len(
                final_rows
            ),

        "missing_split_rows":
            missing_split_rows,

        "num_classes":
            len(
                class_to_index
            ),

        "split_counts":
            dict(
                split_counts
            ),

        "class_counts":
            dict(
                sorted(
                    class_counts.items()
                )
            ),

        "species_counts":
            dict(
                species_counts
            ),

        "class_to_index":
            class_to_index,

        "manifest":
            str(
                OUTPUT_CSV
            ),
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


    print()

    print(
        "Final manifest images :",
        len(
            final_rows
        ),
    )

    print(
        "Missing split rows     :",
        missing_split_rows,
    )

    print(
        "Number of classes      :",
        len(
            class_to_index
        ),
    )


    print()
    print("Split counts:")


    for split in [
        "train",
        "validation",
        "test",
    ]:

        print(
            f"  {split:<12}: "
            f"{split_counts[split]}"
        )


    print()
    print(
        "Manifest:",
        OUTPUT_CSV
    )

    print(
        "Summary :",
        OUTPUT_JSON
    )


if __name__ == "__main__":
    main()