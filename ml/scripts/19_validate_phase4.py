from pathlib import Path
import csv
import json
from collections import defaultdict
from datetime import datetime


# =========================================================
# BREEDVISION AI
# PHASE 4 - FINAL VALIDATION
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORTS_DIR = PROJECT_ROOT / "reports"
CONFIGS_DIR = PROJECT_ROOT / "configs"


REQUIRED_FILES = [
    CONFIGS_DIR / "dataset_sources.json",
    CONFIGS_DIR / "dataset_config.json",
    CONFIGS_DIR / "class_to_index.json",
    CONFIGS_DIR / "species_mapping.json",

    REPORTS_DIR / "processed_master_manifest.csv",
    REPORTS_DIR / "processed_master_summary.json",

    REPORTS_DIR / "near_duplicate_summary.json",
    REPORTS_DIR / "near_duplicate_groups.csv",

    REPORTS_DIR / "dataset_split_manifest.csv",
    REPORTS_DIR / "dataset_split_summary.json",

    REPORTS_DIR / "split_leakage_audit.json",

    REPORTS_DIR / "final_dataset_manifest.csv",
    REPORTS_DIR / "final_dataset_summary.json",
]


COMPLETION_JSON = (
    REPORTS_DIR
    / "phase4_completion.json"
)

COMPLETION_MD = (
    REPORTS_DIR
    / "phase4_completion_report.md"
)


def load_json(path):

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def load_csv(path):

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        return list(
            csv.DictReader(file)
        )


def main():

    print("=" * 84)
    print("BREEDVISION AI - PHASE 4 FINAL VALIDATION")
    print("=" * 84)


    errors = []
    warnings = []


    # =====================================================
    # REQUIRED FILES
    # =====================================================

    missing_files = [
        str(path)

        for path in REQUIRED_FILES

        if not path.exists()
    ]


    if missing_files:

        for path in missing_files:

            errors.append(
                f"Missing required Phase 4 file: {path}"
            )


    if errors:

        print()

        for error in errors:

            print(
                "[FAIL]",
                error,
            )

        print()

        print(
            "PHASE 4 STATUS: FAIL"
        )

        return


    # =====================================================
    # LOAD CORE FILES
    # =====================================================

    config = load_json(
        CONFIGS_DIR
        / "dataset_config.json"
    )

    class_to_index = load_json(
        CONFIGS_DIR
        / "class_to_index.json"
    )

    species_mapping = load_json(
        CONFIGS_DIR
        / "species_mapping.json"
    )

    processed_summary = load_json(
        REPORTS_DIR
        / "processed_master_summary.json"
    )

    split_summary = load_json(
        REPORTS_DIR
        / "dataset_split_summary.json"
    )

    leakage = load_json(
        REPORTS_DIR
        / "split_leakage_audit.json"
    )

    final_summary = load_json(
        REPORTS_DIR
        / "final_dataset_summary.json"
    )

    final_rows = load_csv(
        REPORTS_DIR
        / "final_dataset_manifest.csv"
    )


    # =====================================================
    # CONFIG CONSISTENCY
    # =====================================================

    configured_classes = (
        config[
            "classes"
        ]
    )


    if (
        len(configured_classes)
        !=
        len(class_to_index)
    ):

        errors.append(
            "Class count differs between dataset_config and class_to_index."
        )


    if set(
        configured_classes
    ) != set(
        species_mapping.keys()
    ):

        errors.append(
            "Species mapping does not match configured class list."
        )


    indexes = sorted(
        class_to_index.values()
    )


    expected_indexes = list(
        range(
            len(
                class_to_index
            )
        )
    )


    if indexes != expected_indexes:

        errors.append(
            "class_to_index values are not contiguous from 0 to N-1."
        )


    # =====================================================
    # DATASET SIZE CONSISTENCY
    # =====================================================

    processed_count = (
        processed_summary[
            "final_processed_images"
        ]
    )

    final_count = (
        final_summary[
            "total_images"
        ]
    )


    if processed_count != final_count:

        errors.append(
            f"Processed image count ({processed_count}) "
            f"does not match final manifest count ({final_count})."
        )


    if (
        final_summary[
            "missing_split_rows"
        ]
        != 0
    ):

        errors.append(
            "Some processed images are missing split assignments."
        )


    # =====================================================
    # LEAKAGE
    # =====================================================

    if leakage.get(
        "status"
    ) != "PASS":

        errors.append(
            "Independent split leakage audit did not pass."
        )


    if (
        split_summary.get(
            "group_leakage_count",
            0,
        )
        != 0
    ):

        errors.append(
            "Group leakage exists in split summary."
        )


    # =====================================================
    # SPLIT VALIDITY
    # =====================================================

    split_counts = defaultdict(
        int
    )

    class_split_counts = {
        breed: {
            "train": 0,
            "validation": 0,
            "test": 0,
        }

        for breed in configured_classes
    }


    missing_image_files = 0


    for row in final_rows:

        image_path = Path(
            row[
                "image_path"
            ]
        )


        if not image_path.exists():

            missing_image_files += 1


        split = (
            row[
                "split"
            ]
        )

        breed = (
            row[
                "breed"
            ]
        )


        split_counts[
            split
        ] += 1


        if breed in class_split_counts:

            class_split_counts[
                breed
            ][
                split
            ] += 1


    if missing_image_files > 0:

        errors.append(
            f"{missing_image_files} manifest images do not exist."
        )


    for breed, counts in class_split_counts.items():

        for split, count in counts.items():

            if count == 0:

                errors.append(
                    f"{breed} has zero images in {split}."
                )


    # =====================================================
    # RATIO SANITY
    # =====================================================

    total = len(
        final_rows
    )


    actual_ratios = {}


    for split in [
        "train",
        "validation",
        "test",
    ]:

        percentage = (
            split_counts[
                split
            ]
            /
            max(
                total,
                1,
            )
        )


        actual_ratios[
            split
        ] = round(
            percentage,
            4,
        )


    if not (
        0.60
        <=
        actual_ratios[
            "train"
        ]
        <=
        0.80
    ):

        warnings.append(
            "Train ratio deviates substantially from the 70% target."
        )


    if not (
        0.08
        <=
        actual_ratios[
            "validation"
        ]
        <=
        0.25
    ):

        warnings.append(
            "Validation ratio deviates substantially from the 15% target."
        )


    if not (
        0.08
        <=
        actual_ratios[
            "test"
        ]
        <=
        0.25
    ):

        warnings.append(
            "Test ratio deviates substantially from the 15% target."
        )


    # =====================================================
    # FINAL STATUS
    # =====================================================

    status = (
        "PASS"
        if len(errors) == 0
        else
        "FAIL"
    )


    completion = {
        "project":
            "BreedVision AI",

        "phase":
            "Phase 4 - ML Dataset Foundation",

        "status":
            status,

        "validated_at":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "classifier_version":
            config[
                "classifier_version"
            ],

        "num_classes":
            len(
                configured_classes
            ),

        "classes":
            configured_classes,

        "total_training_ready_images":
            total,

        "split_counts":
            dict(
                split_counts
            ),

        "actual_split_ratios":
            actual_ratios,

        "leakage_status":
            leakage[
                "status"
            ],

        "errors":
            errors,

        "warnings":
            warnings,
    }


    with COMPLETION_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            completion,
            file,
            indent=4,
        )


    # =====================================================
    # MARKDOWN REPORT
    # =====================================================

    markdown = []

    markdown.append(
        "# BreedVision AI - Phase 4 Completion Report"
    )

    markdown.append("")

    markdown.append(
        f"**Status:** {status}"
    )

    markdown.append("")

    markdown.append(
        f"**Classifier Version:** "
        f"{config['classifier_version']}"
    )

    markdown.append("")

    markdown.append(
        f"**Final Classes:** "
        f"{len(configured_classes)}"
    )

    markdown.append("")

    markdown.append(
        f"**Training-ready Images:** "
        f"{total}"
    )

    markdown.append("")

    markdown.append(
        "## Dataset Split"
    )

    markdown.append("")

    markdown.append(
        f"- Train: {split_counts['train']}"
    )

    markdown.append(
        f"- Validation: {split_counts['validation']}"
    )

    markdown.append(
        f"- Test: {split_counts['test']}"
    )

    markdown.append("")

    markdown.append(
        "## Leakage Validation"
    )

    markdown.append("")

    markdown.append(
        f"- Status: {leakage['status']}"
    )

    markdown.append(
        f"- Group leakage: "
        f"{leakage['group_leakage_count']}"
    )

    markdown.append(
        f"- Exact hash leakage: "
        f"{leakage['exact_hash_cross_split_count']}"
    )

    markdown.append(
        f"- Near-duplicate pair leakage: "
        f"{leakage['near_duplicate_pair_cross_split_count']}"
    )

    markdown.append("")

    markdown.append(
        "## Phase 4 Dataset Policy"
    )

    markdown.append("")

    markdown.append(
        "- Raw datasets remain unchanged."
    )

    markdown.append(
        "- Corrupt and invalid images are excluded."
    )

    markdown.append(
        "- Exact duplicates are removed."
    )

    markdown.append(
        "- Cross-class exact conflicts are excluded."
    )

    markdown.append(
        "- Near-duplicate groups remain within one split."
    )

    markdown.append(
        "- Train, validation and test leakage has been checked."
    )

    markdown.append(
        "- Synthetic data is not used as primary evaluation data."
    )

    markdown.append("")

    if errors:

        markdown.append(
            "## Errors"
        )

        markdown.append("")

        for error in errors:

            markdown.append(
                f"- {error}"
            )


    if warnings:

        markdown.append("")
        markdown.append(
            "## Warnings"
        )

        markdown.append("")

        for warning in warnings:

            markdown.append(
                f"- {warning}"
            )


    COMPLETION_MD.write_text(
        "\n".join(
            markdown
        ),
        encoding="utf-8",
    )


    # =====================================================
    # TERMINAL
    # =====================================================

    print()
    print("-" * 84)

    print(
        "Final images :",
        total,
    )

    print(
        "Classes      :",
        len(
            configured_classes
        ),
    )

    print(
        "Train        :",
        split_counts[
            "train"
        ],
    )

    print(
        "Validation   :",
        split_counts[
            "validation"
        ],
    )

    print(
        "Test         :",
        split_counts[
            "test"
        ],
    )

    print(
        "Leakage audit:",
        leakage[
            "status"
        ],
    )


    print()
    print("=" * 84)
    print("PHASE 4 STATUS:", status)
    print("=" * 84)


    if errors:

        print()

        for error in errors:

            print(
                "[ERROR]",
                error,
            )


    if warnings:

        print()

        for warning in warnings:

            print(
                "[WARNING]",
                warning,
            )


    print()
    print(
        "Completion JSON:",
        COMPLETION_JSON
    )

    print(
        "Completion report:",
        COMPLETION_MD
    )


if __name__ == "__main__":
    main()