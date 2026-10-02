from pathlib import Path
import csv
import hashlib
import json
import shutil
from collections import defaultdict

from PIL import Image
from tqdm import tqdm


# =========================================================
# BREEDVISION AI
# PHASE 4 - BUILD PROCESSED MASTER DATASET
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_ROOT = PROJECT_ROOT / "data" / "raw"

PROCESSED_ROOT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "master"
)

REPORTS_DIR = PROJECT_ROOT / "reports"

CONFIGS_DIR = PROJECT_ROOT / "configs"


CLASS_CONFIG = (
    CONFIGS_DIR
    / "class_to_index.json"
)

LABEL_REVIEW_CSV = (
    REPORTS_DIR
    / "label_normalization_review.csv"
)

CORRUPT_CSV = (
    REPORTS_DIR
    / "corrupt_images.csv"
)

QUALITY_CSV = (
    REPORTS_DIR
    / "image_quality_audit.csv"
)

CONFLICT_CSV = (
    REPORTS_DIR
    / "duplicate_label_conflicts.csv"
)


MANIFEST_CSV = (
    REPORTS_DIR
    / "processed_master_manifest.csv"
)

SUMMARY_JSON = (
    REPORTS_DIR
    / "processed_master_summary.json"
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


IICBD_LABELS = {
    "bargur": "Bargur",
    "gir": "Gir",
    "hallikar": "Hallikar",
    "kankrej": "Kankrej",
    "ongole": "Ongole",
    "pulikulam": "Pulikulam",
    "rathi": "Rathi",
    "sahiwal": "Sahiwal",
    "tharparkar": "Tharparkar",
}


# =========================================================
# HELPERS
# =========================================================


def normalize_key(value):
    return (
        value.strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )


def normalized_path(path):
    return str(
        Path(path).resolve()
    ).lower()


def calculate_sha256(path):
    sha256 = hashlib.sha256()

    with path.open("rb") as file:
        while True:
            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


# =========================================================
# LOAD FINAL V1 CLASSES
# =========================================================


def load_final_classes():
    if not CLASS_CONFIG.exists():
        raise FileNotFoundError(
            "\nMissing class configuration:\n"
            f"{CLASS_CONFIG}\n\n"
            "Run 09_freeze_v1_classes.py first."
        )

    with CLASS_CONFIG.open(
        "r",
        encoding="utf-8",
    ) as file:
        mapping = json.load(file)

    return set(
        mapping.keys()
    )


# =========================================================
# SECONDARY LABEL MAPPING
# =========================================================


def load_secondary_label_map():

    mapping = {}

    if not LABEL_REVIEW_CSV.exists():
        return mapping

    with LABEL_REVIEW_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if (
                row["source"]
                !=
                "indian_bovine_secondary"
            ):
                continue

            original = normalize_key(
                row["original_label"]
            )

            normalized = (
                row["normalized_label"]
                .strip()
            )

            mapping[
                original
            ] = normalized

    return mapping


# =========================================================
# DETECT NORMALIZED BREED
# =========================================================


def detect_label(
    image_path,
    secondary_map,
):

    parts = list(
        image_path.parts
    )


    # -----------------------------------------------------
    # IICBD
    # -----------------------------------------------------

    if "iicbd_2026" in parts:

        for part in parts:

            key = normalize_key(
                part
            )

            if key in IICBD_LABELS:
                return (
                    IICBD_LABELS[key],
                    "iicbd_2026",
                )


    # -----------------------------------------------------
    # SECONDARY BOVINE DATASET
    # -----------------------------------------------------

    if "indian_bovine_kaggle" in parts:

        original_label = normalize_key(
            image_path.parent.name
        )

        normalized = secondary_map.get(
            original_label
        )

        if normalized:
            return (
                normalized,
                "indian_bovine_secondary",
            )

        return (
            None,
            "indian_bovine_secondary",
        )


    return (
        None,
        "unknown",
    )


# =========================================================
# EXCLUSION REPORTS
# =========================================================


def load_corrupt_paths():

    paths = set()

    if not CORRUPT_CSV.exists():
        return paths

    with CORRUPT_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            path = row.get(
                "path",
                ""
            )

            if path:
                paths.add(
                    normalized_path(
                        path
                    )
                )

    return paths


def load_small_image_paths():

    paths = set()

    if not QUALITY_CSV.exists():
        return paths

    with QUALITY_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            too_small = (
                row.get(
                    "too_small",
                    ""
                )
                .strip()
                .lower()
            )

            if too_small == "true":

                path = row.get(
                    "path",
                    ""
                )

                if path:
                    paths.add(
                        normalized_path(
                            path
                        )
                    )

    return paths


def load_conflict_hashes():

    hashes = set()

    if not CONFLICT_CSV.exists():
        return hashes

    with CONFLICT_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            status = (
                row.get(
                    "status",
                    ""
                )
                .strip()
            )

            if status in {
                "cross_class_conflict",
                "unknown_label",
            }:

                sha256 = (
                    row.get(
                        "sha256",
                        ""
                    )
                    .strip()
                )

                if sha256:
                    hashes.add(
                        sha256
                    )

    return hashes


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 80)
    print("BREEDVISION AI - BUILD PROCESSED MASTER DATASET")
    print("=" * 80)


    final_classes = (
        load_final_classes()
    )

    secondary_map = (
        load_secondary_label_map()
    )

    corrupt_paths = (
        load_corrupt_paths()
    )

    small_paths = (
        load_small_image_paths()
    )

    conflict_hashes = (
        load_conflict_hashes()
    )


    print()
    print(
        "Frozen v1 classes :",
        len(final_classes),
    )

    print(
        "Known corrupt files:",
        len(corrupt_paths),
    )

    print(
        "Small images       :",
        len(small_paths),
    )

    print(
        "Conflict hashes    :",
        len(conflict_hashes),
    )


    # =====================================================
    # REBUILD GENERATED PROCESSED DIRECTORY
    # =====================================================

    if PROCESSED_ROOT.exists():

        print()
        print(
            "Removing previous generated processed/master dataset..."
        )

        shutil.rmtree(
            PROCESSED_ROOT
        )


    PROCESSED_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )


    # Create final class directories.

    for breed in sorted(
        final_classes
    ):

        (
            PROCESSED_ROOT
            / breed
        ).mkdir(
            parents=True,
            exist_ok=True,
        )


    # =====================================================
    # DISCOVER RAW IMAGES
    # =====================================================

    raw_images = [
        path

        for path in RAW_ROOT.rglob("*")

        if (
            path.is_file()
            and
            path.suffix.lower()
            in IMAGE_EXTENSIONS
        )
    ]


    print()
    print(
        "Raw images discovered:",
        len(raw_images),
    )


    # =====================================================
    # FIRST PASS
    #
    # Validate label, corruption, dimensions and hash.
    # =====================================================

    eligible_by_hash = defaultdict(
        list
    )


    counters = {
        "raw_images":
            len(raw_images),

        "excluded_unknown_label":
            0,

        "excluded_not_v1_class":
            0,

        "excluded_corrupt":
            0,

        "excluded_small":
            0,

        "excluded_conflict_hash":
            0,

        "hash_failures":
            0,

        "eligible_before_deduplication":
            0,

        "exact_duplicates_removed":
            0,

        "copied_images":
            0,
    }


    print()
    print(
        "Scanning eligible images..."
    )


    for image_path in tqdm(
        raw_images,
        desc="Auditing raw images",
    ):

        path_key = normalized_path(
            image_path
        )


        # ---------------------------------------------
        # CORRUPT
        # ---------------------------------------------

        if path_key in corrupt_paths:

            counters[
                "excluded_corrupt"
            ] += 1

            continue


        # ---------------------------------------------
        # SMALL IMAGE
        # ---------------------------------------------

        if path_key in small_paths:

            counters[
                "excluded_small"
            ] += 1

            continue


        # ---------------------------------------------
        # LABEL
        # ---------------------------------------------

        breed, source = detect_label(
            image_path,
            secondary_map,
        )


        if not breed:

            counters[
                "excluded_unknown_label"
            ] += 1

            continue


        # ---------------------------------------------
        # FINAL V1 CLASS FILTER
        # ---------------------------------------------

        if breed not in final_classes:

            counters[
                "excluded_not_v1_class"
            ] += 1

            continue


        # ---------------------------------------------
        # EXTRA SAFETY: IMAGE READ
        # ---------------------------------------------

        try:

            with Image.open(
                image_path
            ) as image:

                width, height = (
                    image.size
                )


                if (
                    width < 224
                    or
                    height < 224
                ):

                    counters[
                        "excluded_small"
                    ] += 1

                    continue


        except Exception:

            counters[
                "excluded_corrupt"
            ] += 1

            continue


        # ---------------------------------------------
        # HASH
        # ---------------------------------------------

        try:

            sha256 = (
                calculate_sha256(
                    image_path
                )
            )

        except OSError:

            counters[
                "hash_failures"
            ] += 1

            continue


        # ---------------------------------------------
        # CROSS-CLASS CONFLICT
        # ---------------------------------------------

        if sha256 in conflict_hashes:

            counters[
                "excluded_conflict_hash"
            ] += 1

            continue


        eligible_by_hash[
            sha256
        ].append(
            {
                "path":
                    image_path,

                "breed":
                    breed,

                "source":
                    source,

                "width":
                    width,

                "height":
                    height,
            }
        )


        counters[
            "eligible_before_deduplication"
        ] += 1


    # =====================================================
    # SECOND PASS
    #
    # Keep exactly one eligible image per SHA256.
    # =====================================================

    selected_records = []


    for sha256, records in (
        eligible_by_hash.items()
    ):

        # deterministic ordering

        records.sort(
            key=lambda item:
                str(
                    item["path"]
                ).lower()
        )


        selected = (
            records[0]
        )


        selected[
            "sha256"
        ] = sha256


        selected_records.append(
            selected
        )


        counters[
            "exact_duplicates_removed"
        ] += (
            len(records)
            - 1
        )


    # =====================================================
    # SORT FOR REPRODUCIBILITY
    # =====================================================

    selected_records.sort(
        key=lambda item: (
            item[
                "breed"
            ].lower(),

            str(
                item[
                    "path"
                ]
            ).lower(),
        )
    )


    # =====================================================
    # COPY TO PROCESSED MASTER
    # =====================================================

    manifest_rows = []

    class_counts = defaultdict(
        int
    )


    print()
    print(
        "Building processed master dataset..."
    )


    for index, record in enumerate(
        tqdm(
            selected_records,
            desc="Copying clean images",
        ),
        start=1,
    ):

        source_path = (
            record[
                "path"
            ]
        )

        breed = (
            record[
                "breed"
            ]
        )

        source = (
            record[
                "source"
            ]
        )

        sha256 = (
            record[
                "sha256"
            ]
        )


        extension = (
            source_path
            .suffix
            .lower()
        )


        # Prevent filename collisions.
        # SHA prefix gives deterministic unique filenames.

        destination_name = (
            f"{sha256[:16]}"
            f"{extension}"
        )


        destination_path = (
            PROCESSED_ROOT
            / breed
            / destination_name
        )


        shutil.copy2(
            source_path,
            destination_path,
        )


        class_counts[
            breed
        ] += 1


        counters[
            "copied_images"
        ] += 1


        manifest_rows.append(
            {
                "processed_id":
                    index,

                "breed":
                    breed,

                "source_dataset":
                    source,

                "source_path":
                    str(
                        source_path
                    ),

                "processed_path":
                    str(
                        destination_path
                    ),

                "sha256":
                    sha256,

                "width":
                    record[
                        "width"
                    ],

                "height":
                    record[
                        "height"
                    ],
            }
        )


    # =====================================================
    # MANIFEST
    # =====================================================

    with MANIFEST_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        fieldnames = [
            "processed_id",
            "breed",
            "source_dataset",
            "source_path",
            "processed_path",
            "sha256",
            "width",
            "height",
        ]


        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            manifest_rows
        )


    # =====================================================
    # SUMMARY
    # =====================================================

    summary = {
        "dataset":
            "BreedVision Processed Master v1",

        "processed_root":
            str(
                PROCESSED_ROOT
            ),

        "final_classes":
            sorted(
                final_classes
            ),

        "class_counts":
            dict(
                sorted(
                    class_counts.items()
                )
            ),

        "counters":
            counters,

        "rules": {
            "raw_modified":
                False,

            "minimum_resolution":
                "224x224",

            "corrupt_images_excluded":
                True,

            "non_v1_classes_excluded":
                True,

            "cross_class_duplicate_conflicts_excluded":
                True,

            "exact_duplicates_removed":
                True,

            "one_image_per_sha256":
                True,
        },
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
    # TERMINAL SUMMARY
    # =====================================================

    print()
    print("=" * 80)
    print("PROCESSED MASTER DATASET COMPLETE")
    print("=" * 80)


    print()

    print(
        "Raw images discovered           :",
        counters[
            "raw_images"
        ],
    )

    print(
        "Unknown labels excluded         :",
        counters[
            "excluded_unknown_label"
        ],
    )

    print(
        "Non-v1 classes excluded         :",
        counters[
            "excluded_not_v1_class"
        ],
    )

    print(
        "Corrupt images excluded         :",
        counters[
            "excluded_corrupt"
        ],
    )

    print(
        "Small images excluded           :",
        counters[
            "excluded_small"
        ],
    )

    print(
        "Conflict images excluded        :",
        counters[
            "excluded_conflict_hash"
        ],
    )

    print(
        "Exact duplicate copies removed  :",
        counters[
            "exact_duplicates_removed"
        ],
    )

    print(
        "Final clean images copied       :",
        counters[
            "copied_images"
        ],
    )


    print()
    print("-" * 80)
    print("FINAL CLASS COUNTS")
    print("-" * 80)


    for breed in sorted(
        final_classes
    ):

        print(
            f"{breed:<25} "
            f"{class_counts.get(breed, 0)}"
        )


    print()

    print(
        "Processed dataset:"
    )

    print(
        PROCESSED_ROOT
    )


    print()

    print(
        "Manifest:"
    )

    print(
        MANIFEST_CSV
    )


    print()

    print(
        "Summary:"
    )

    print(
        SUMMARY_JSON
    )


    print()

    print(
        "Original raw datasets were NOT modified."
    )


if __name__ == "__main__":
    main()