from pathlib import Path
import csv
import json


# =========================================================
# BREEDVISION AI
# PHASE 6.5
# FINAL BUFFALO CLASS FREEZE
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


GROUP_SUMMARY = (
    REPORTS_DIR
    / "phase6_buffalo_near_duplicate_groups_summary.json"
)

PROVISIONAL_CONFIG = (
    CONFIGS_DIR
    / "phase6_buffalo_candidates.json"
)


OUTPUT_JSON = (
    CONFIGS_DIR
    / "phase6_buffalo_final_classes.json"
)

OUTPUT_CSV = (
    REPORTS_DIR
    / "phase6_buffalo_final_class_freeze.csv"
)


# =========================================================
# FINAL POLICY
# =========================================================

MIN_IMAGES = 80
MIN_GROUPS = 3


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


def main():

    print("=" * 86)
    print(
        "BREEDVISION AI - PHASE 6 FINAL BUFFALO CLASS FREEZE"
    )
    print("=" * 86)


    summary = load_json(
        GROUP_SUMMARY
    )

    provisional = load_json(
        PROVISIONAL_CONFIG
    )


    provisional_classes = (
        provisional[
            "candidate_classes"
        ]
    )


    group_summary = (
        summary[
            "breed_group_summary"
        ]
    )


    final_classes = []

    held_classes = []

    rows = []


    for breed in sorted(
        provisional_classes
    ):

        info = group_summary.get(
            breed,
            {
                "images": 0,
                "distinct_near_duplicate_groups": 0,
                "largest_group_size": 0,
            },
        )


        images = int(
            info[
                "images"
            ]
        )


        groups = int(
            info[
                "distinct_near_duplicate_groups"
            ]
        )


        eligible = (
            images >= MIN_IMAGES
            and
            groups >= MIN_GROUPS
        )


        if eligible:

            decision = (
                "included_in_classifier_v2"
            )

            final_classes.append(
                breed
            )

        else:

            decision = (
                "held_from_classifier_v2"
            )

            held_classes.append(
                breed
            )


        rows.append(
            {
                "breed":
                    breed,

                "images":
                    images,

                "near_duplicate_groups":
                    groups,

                "largest_group_size":
                    info[
                        "largest_group_size"
                    ],

                "minimum_images":
                    MIN_IMAGES,

                "minimum_groups":
                    MIN_GROUPS,

                "included":
                    eligible,

                "decision":
                    decision,
            }
        )


    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "breed",
                "images",
                "near_duplicate_groups",
                "largest_group_size",
                "minimum_images",
                "minimum_groups",
                "included",
                "decision",
            ],
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


    result = {

        "phase":
            "Phase 6.5 - Final Buffalo Class Freeze",

        "freeze_status":
            "final",

        "minimum_images":
            MIN_IMAGES,

        "minimum_near_duplicate_groups":
            MIN_GROUPS,

        "final_buffalo_classes":
            final_classes,

        "held_buffalo_classes":
            held_classes,

        "num_final_buffalo_classes":
            len(
                final_classes
            ),

        "decisions":
            rows,

        "near_duplicate_policy":
            (
                "Near-duplicate images are retained, "
                "but every group must remain entirely "
                "within one dataset split."
            ),

        "data_quality_note":
            (
                "These buffalo classes are limited-data "
                "prototype classes and require per-class "
                "evaluation before production claims."
            ),
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
        "Final buffalo classes:"
    )


    for breed in final_classes:

        print(
            "  +",
            breed
        )


    print()
    print(
        "Held classes:"
    )


    for breed in held_classes:

        print(
            "  -",
            breed
        )


    print()
    print("=" * 86)
    print(
        "PHASE 6.5 CLASS FREEZE: COMPLETE"
    )
    print("=" * 86)


if __name__ == "__main__":

    main()