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


DATASET_CONFIG = (
    CONFIGS_DIR
    / "dataset_config.json"
)

LABEL_REVIEW_CSV = (
    REPORTS_DIR
    / "label_normalization_review.csv"
)

EXCLUSION_CSV = (
    REPORTS_DIR
    / "hard_exclusion_manifest.csv"
)

OUTPUT_MANIFEST = (
    REPORTS_DIR
    / "processed_master_manifest.csv"
)

OUTPUT_SUMMARY = (
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


def sha256_file(path):
    hasher = hashlib.sha256()

    with path.open("rb") as file:
        while True:
            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            hasher.update(chunk)

    return hasher.hexdigest()


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Missing required file:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_exclusions():
    excluded = set()

    if not EXCLUSION_CSV.exists():
        return excluded

    with EXCLUSION_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            path = (
                row.get("path", "")
                .strip()
            )

            if path:
                excluded.add(
                    str(
                        Path(path).resolve()
                    )
                )

    return excluded


def load_secondary_label_map():
    mapping = {}

    if not LABEL_REVIEW_CSV.exists():
        raise FileNotFoundError(
            f"Missing label review file:\n"
            f"{LABEL_REVIEW_CSV}"
        )

    with LABEL_REVIEW_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if (
                row["source"].strip()
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
# LABEL DETECTION
# =========================================================


def detect_source_and_label(
    image_path,
    secondary_map,
    known_classes,
):

    parts = list(
        image_path.parts
    )


    # =====================================================
    # IICBD
    # =====================================================

    if "iicbd_2026" in parts:

        for part in parts:

            for breed in known_classes:

                if (
                    normalize_key(part)
                    ==
                    normalize_key(breed)
                ):
                    return (
                        "iicbd_2026",
                        part,
                        breed,
                    )

        return (
            "iicbd_2026",
            None,
            None,
        )


    # =====================================================
    # SECONDARY KAGGLE DATASET
    # =====================================================

    if "indian_bovine_kaggle" in parts:

        original_label = (
            image_path.parent.name
        )

        key = normalize_key(
            original_label
        )

        normalized = (
            secondary_map.get(key)
        )

        return (
            "indian_bovine_secondary",
            original_label,
            normalized,
        )


    return (
        "unknown",
        None,
        None,
    )


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 80)
    print("BREEDVISION AI - BUILD PROCESSED MASTER DATASET")
    print("=" * 80)


    config = load_json(
        DATASET_CONFIG
    )


    v1_classes = set(
        config[
            "classes"
        ]
    )


    species_mapping = (
        config[
            "species_mapping"
        ]
    )


    secondary_map = (
        load_secondary_label_map()
    )


    excluded_paths = (
        load_exclusions()
    )


    # =====================================================
    # RESET PROCESSED MASTER
    # =====================================================

    if PROCESSED_ROOT.exists():

        print()
        print(
            "Removing previous generated processed/master..."
        )

        shutil.rmtree(
            PROCESSED_ROOT
        )


    PROCESSED_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )


    # Create breed folders

    for breed in sorted(
        v1_classes
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

    print(
        "Hard exclusions loaded:",
        len(excluded_paths),
    )

    print(
        "Frozen v1 classes:",
        len(v1_classes),
    )


    # =====================================================
    # BUILD CANDIDATE RECORDS
    # =====================================================

    candidates = []

    skipped_hard_exclusion = 0
    skipped_non_v1 = 0
    skipped_unknown_label = 0
    failed_read = 0


    for image_path in tqdm(
        raw_images,
        desc="Preparing candidates",
    ):

        resolved_path = str(
            image_path.resolve()
        )


        # Hard exclusion

        if resolved_path in excluded_paths:

            skipped_hard_exclusion += 1

            continue


        (
            source,
            original_label,
            normalized_label,
        ) = detect_source_and_label(
            image_path,
            secondary_map,
            v1_classes,
        )


        if not normalized_label:

            skipped_unknown_label += 1

            continue


        if normalized_label not in v1_classes:

            skipped_non_v1 += 1

            continue


        # Defensive readability check

        try:
            with Image.open(
                image_path
            ) as image:

                width, height = (
                    image.size
                )

        except Exception:

            failed_read += 1

            continue


        try:
            file_hash = sha256_file(
                image_path
            )

        except OSError:

            failed_read += 1

            continue


        candidates.append(
            {
                "source_path":
                    image_path,

                "source_dataset":
                    source,

                "original_label":
                    original_label,

                "breed":
                    normalized_label,

                "species":
                    species_mapping.get(
                        normalized_label,
                        "unknown",
                    ),

                "sha256":
                    file_hash,

                "width":
                    width,

                "height":
                    height,
            }
        )


    # =====================================================
    # GLOBAL HASH CONFLICT CHECK
    # =====================================================

    hash_labels = defaultdict(
        set
    )


    for row in candidates:

        hash_labels[
            row["sha256"]
        ].add(
            row["breed"]
        )


    unexpected_conflict_hashes = {
        image_hash

        for image_hash, labels
        in hash_labels.items()

        if len(labels) > 1
    }


    # =====================================================
    # SAME-CLASS DEDUPLICATION
    # =====================================================

    seen_class_hashes = set()

    final_records = []

    same_class_duplicates_removed = 0

    unexpected_conflict_images = 0


    for row in tqdm(
        candidates,
        desc="Building master dataset",
    ):

        image_hash = (
            row["sha256"]
        )


        # Defensive cross-class conflict exclusion

        if (
            image_hash
            in
            unexpected_conflict_hashes
        ):

            unexpected_conflict_images += 1

            continue


        class_hash_key = (
            row["breed"],
            image_hash,
        )


        if (
            class_hash_key
            in
            seen_class_hashes
        ):

            same_class_duplicates_removed += 1

            continue


        seen_class_hashes.add(
            class_hash_key
        )


        breed = (
            row["breed"]
        )


        source_path = (
            row["source_path"]
        )


        # Unique deterministic output name

        extension = (
            source_path
            .suffix
            .lower()
        )


        output_name = (
            f"{image_hash[:16]}"
            f"{extension}"
        )


        destination = (
            PROCESSED_ROOT
            / breed
            / output_name
        )


        shutil.copy2(
            source_path,
            destination,
        )


        final_records.append(
            {
                "processed_path":
                    str(
                        destination.resolve()
                    ),

                "source_path":
                    str(
                        source_path.resolve()
                    ),

                "source_dataset":
                    row[
                        "source_dataset"
                    ],

                "original_label":
                    row[
                        "original_label"
                    ],

                "normalized_breed":
                    breed,

                "species":
                    row[
                        "species"
                    ],

                "sha256":
                    image_hash,

                "width":
                    row[
                        "width"
                    ],

                "height":
                    row[
                        "height"
                    ],

                "file_size_bytes":
                    destination.stat().st_size,
            }
        )


    # =====================================================
    # CLASS COUNTS
    # =====================================================

    class_counts = defaultdict(
        int
    )


    for row in final_records:

        class_counts[
            row[
                "normalized_breed"
            ]
        ] += 1


    # =====================================================
    # MANIFEST CSV
    # =====================================================

    with OUTPUT_MANIFEST.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        fieldnames = [
            "processed_path",
            "source_path",
            "source_dataset",
            "original_label",
            "normalized_breed",
            "species",
            "sha256",
            "width",
            "height",
            "file_size_bytes",
        ]


        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            final_records
        )


    # =====================================================
    # SUMMARY JSON
    # =====================================================

    summary = {
        "raw_images_discovered":
            len(raw_images),

        "candidate_images":
            len(candidates),

        "final_processed_images":
            len(final_records),

        "hard_exclusions_skipped":
            skipped_hard_exclusion,

        "non_v1_images_skipped":
            skipped_non_v1,

        "unknown_label_images_skipped":
            skipped_unknown_label,

        "failed_read_images":
            failed_read,

        "same_class_exact_duplicates_removed":
            same_class_duplicates_removed,

        "unexpected_cross_class_hash_groups":
            len(
                unexpected_conflict_hashes
            ),

        "unexpected_cross_class_images_removed":
            unexpected_conflict_images,

        "num_classes":
            len(
                class_counts
            ),

        "class_counts":
            dict(
                sorted(
                    class_counts.items()
                )
            ),

        "processed_root":
            str(
                PROCESSED_ROOT.resolve()
            ),

        "raw_data_modified":
            False,
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
    # OUTPUT
    # =====================================================

    print()
    print("=" * 80)
    print("PROCESSED MASTER RESULT")
    print("=" * 80)


    print(
        "Raw images discovered          :",
        len(raw_images),
    )

    print(
        "Candidate images               :",
        len(candidates),
    )

    print(
        "Hard exclusions skipped        :",
        skipped_hard_exclusion,
    )

    print(
        "Non-v1 images skipped          :",
        skipped_non_v1,
    )

    print(
        "Unknown labels skipped         :",
        skipped_unknown_label,
    )

    print(
        "Same-class duplicates removed  :",
        same_class_duplicates_removed,
    )

    print(
        "Unexpected conflict groups     :",
        len(
            unexpected_conflict_hashes
        ),
    )

    print(
        "Final processed images         :",
        len(final_records),
    )


    print()
    print("-" * 80)
    print("FINAL CLASS COUNTS")
    print("-" * 80)


    for breed, count in sorted(
        class_counts.items()
    ):

        print(
            f"{breed:<25} : {count}"
        )


    print()
    print(
        "Master dataset:"
    )

    print(
        PROCESSED_ROOT
    )


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


    print()
    print(
        "Raw dataset was not modified."
    )


if __name__ == "__main__":
    main()