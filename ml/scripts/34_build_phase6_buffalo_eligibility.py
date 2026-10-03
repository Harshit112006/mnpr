from pathlib import Path
import csv
import json


# =========================================================
# BREEDVISION AI
# PHASE 6.3
# BUFFALO CLASS ELIGIBILITY GATE
#
# Revised after real dataset audit:
# minimum 80 unique exact-deduplicated real images
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


INPUT_SUMMARY = (
    REPORTS_DIR
    / "phase6_buffalo_duplicate_summary.json"
)

OUTPUT_CSV = (
    REPORTS_DIR
    / "phase6_buffalo_class_eligibility.csv"
)

OUTPUT_JSON = (
    REPORTS_DIR
    / "phase6_buffalo_class_eligibility.json"
)

OUTPUT_CONFIG = (
    CONFIGS_DIR
    / "phase6_buffalo_candidates.json"
)


# =========================================================
# ELIGIBILITY POLICY
# =========================================================

MINIMUM_IMAGES = 80


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


def classify_strength(
    unique_images,
):

    if unique_images >= 500:
        return "strong"

    if unique_images >= 200:
        return "usable"

    if unique_images >= 80:
        return "limited_but_eligible"

    return "insufficient"


def main():

    print("=" * 86)
    print(
        "BREEDVISION AI - PHASE 6 BUFFALO CLASS ELIGIBILITY"
    )
    print("=" * 86)


    summary = load_json(
        INPUT_SUMMARY
    )


    breed_summary = (
        summary.get(
            "breed_summary",
            {}
        )
    )


    if not breed_summary:

        raise RuntimeError(
            "No buffalo breed summary found."
        )


    rows = []

    eligible_breeds = []

    held_breeds = []


    for breed in sorted(
        breed_summary.keys()
    ):

        info = (
            breed_summary[
                breed
            ]
        )


        unique_images = int(
            info[
                "unique_after_exact_dedup"
            ]
        )


        conflict_images = int(
            info[
                "cross_class_conflict_images"
            ]
        )


        strength = classify_strength(
            unique_images
        )


        eligible = (
            unique_images
            >=
            MINIMUM_IMAGES
        )


        if eligible:

            decision = (
                "eligible_for_phase6_v2_candidate"
            )

            eligible_breeds.append(
                breed
            )

        else:

            decision = (
                "hold_insufficient_data"
            )

            held_breeds.append(
                breed
            )


        rows.append(
            {
                "breed":
                    breed,

                "unique_images":
                    unique_images,

                "cross_class_conflict_images":
                    conflict_images,

                "data_strength":
                    strength,

                "minimum_required":
                    MINIMUM_IMAGES,

                "eligible":
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

        fieldnames = [
            "breed",
            "unique_images",
            "cross_class_conflict_images",
            "data_strength",
            "minimum_required",
            "eligible",
            "decision",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


    report = {

        "phase":
            "Phase 6.3 - Buffalo Class Eligibility Gate",

        "minimum_unique_images_required":
            MINIMUM_IMAGES,

        "eligible_breeds":
            eligible_breeds,

        "held_breeds":
            held_breeds,

        "eligible_count":
            len(
                eligible_breeds
            ),

        "held_count":
            len(
                held_breeds
            ),

        "breed_decisions":
            rows,

        "policy_note":
            (
                "Threshold revised to 80 after auditing "
                "the actual available real buffalo dataset. "
                "Classes below 80 unique images remain held. "
                "Near-duplicate grouping is still required "
                "before final freeze."
            ),
    }


    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
        )


    config = {

        "phase":
            "Phase 6",

        "purpose":
            "Buffalo candidate classes for classifier v2",

        "minimum_images":
            MINIMUM_IMAGES,

        "candidate_classes":
            eligible_breeds,

        "held_classes":
            held_breeds,

        "freeze_status":
            "provisional",

        "reason":
            (
                "Final freeze occurs after "
                "near-duplicate grouping."
            ),
    }


    CONFIGS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    with OUTPUT_CONFIG.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            config,
            file,
            indent=4,
        )


    print()
    print("-" * 86)
    print("BUFFALO CLASS ELIGIBILITY")
    print("-" * 86)


    print(
        f"{'Breed':<20}"
        f"{'Unique':>10}"
        f"{'Strength':>25}"
        f"{'Decision':>35}"
    )


    for row in rows:

        print(
            f"{row['breed']:<20}"
            f"{row['unique_images']:>10}"
            f"{row['data_strength']:>25}"
            f"{row['decision']:>35}"
        )


    print()
    print(
        "Eligible buffalo breeds:",
        eligible_breeds
    )

    print(
        "Held buffalo breeds:",
        held_breeds
    )


    print()
    print("=" * 86)
    print(
        "PHASE 6.3 ELIGIBILITY GATE: COMPLETE"
    )
    print("=" * 86)


if __name__ == "__main__":

    main()