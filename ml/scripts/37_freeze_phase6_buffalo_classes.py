from pathlib import Path
import csv
import json


# =========================================================
# BREEDVISION AI
# PHASE 6.5
# FINAL BUFFALO CLASS FREEZE
#
# FIX:
# Breeds already held during the provisional eligibility
# gate must remain recorded as held in the final config.
# =========================================================


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

REPORTS_DIR = PROJECT_ROOT / "reports"
CONFIGS_DIR = PROJECT_ROOT / "configs"


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


    provisional_classes = list(
        provisional.get(
            "candidate_classes",
            [],
        )
    )


    previously_held_classes = list(
        provisional.get(
            "held_classes",
            [],
        )
    )


    group_summary = summary.get(
        "breed_group_summary",
        {},
    )


    final_classes = []

    failed_final_gate = []

    rows = []


    # =====================================================
    # FINAL CHECK FOR PROVISIONAL CANDIDATES
    # =====================================================


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
            info.get(
                "images",
                0,
            )
        )


        groups = int(
            info.get(
                "distinct_near_duplicate_groups",
                0,
            )
        )


        largest_group_size = int(
            info.get(
                "largest_group_size",
                0,
            )
        )


        included = (
            images >= MIN_IMAGES
            and
            groups >= MIN_GROUPS
        )


        if included:

            final_classes.append(
                breed
            )

            decision = (
                "included_in_classifier_v2"
            )

        else:

            failed_final_gate.append(
                breed
            )

            decision = (
                "held_after_final_group_gate"
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
                    largest_group_size,

                "minimum_images":
                    MIN_IMAGES,

                "minimum_groups":
                    MIN_GROUPS,

                "included":
                    included,

                "decision":
                    decision,
            }
        )


    # =====================================================
    # PRESERVE CLASSES HELD DURING EARLIER ELIGIBILITY GATE
    # =====================================================


    held_classes = sorted(
        set(
            previously_held_classes
            +
            failed_final_gate
        )
    )


    final_classes = sorted(
        final_classes
    )


    # =====================================================
    # SAFETY
    # =====================================================


    overlap = (
        set(
            final_classes
        )
        &
        set(
            held_classes
        )
    )


    if overlap:

        raise RuntimeError(
            "A breed cannot be both final and held: "
            f"{sorted(overlap)}"
        )


    # =====================================================
    # CSV
    # =====================================================


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


    # =====================================================
    # FINAL CONFIG
    # =====================================================


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

        "num_held_buffalo_classes":
            len(
                held_classes
            ),

        "held_from_provisional_gate":
            sorted(
                previously_held_classes
            ),

        "held_after_final_group_gate":
            sorted(
                failed_final_gate
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
                "Buffalo classes below the eligibility "
                "threshold remain explicitly recorded as "
                "held classes and are not part of "
                "classifier-v2 training."
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


    # =====================================================
    # DISPLAY
    # =====================================================


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
        "Held buffalo classes:"
    )

    for breed in held_classes:

        print(
            "  -",
            breed
        )


    print()
    print(
        "Previously held:",
        sorted(
            previously_held_classes
        )
    )

    print(
        "Failed final gate:",
        sorted(
            failed_final_gate
        )
    )


    print()
    print("=" * 86)
    print(
        "PHASE 6.5 CLASS FREEZE: COMPLETE"
    )
    print("=" * 86)


if __name__ == "__main__":

    main()