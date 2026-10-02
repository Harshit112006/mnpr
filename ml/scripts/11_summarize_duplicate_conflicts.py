from pathlib import Path
import csv
import json
from collections import Counter, defaultdict


# =========================================================
# BREEDVISION AI
# PHASE 4 - DUPLICATE LABEL CONFLICT TRIAGE
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORTS_DIR = PROJECT_ROOT / "reports"


INPUT_CSV = (
    REPORTS_DIR
    / "duplicate_label_conflicts.csv"
)

GROUP_OUTPUT_CSV = (
    REPORTS_DIR
    / "duplicate_conflict_groups.csv"
)

PAIR_OUTPUT_CSV = (
    REPORTS_DIR
    / "duplicate_conflict_pairs.csv"
)

SUMMARY_JSON = (
    REPORTS_DIR
    / "duplicate_conflict_triage_summary.json"
)


def main():

    print("=" * 80)
    print("BREEDVISION AI - DUPLICATE CONFLICT TRIAGE")
    print("=" * 80)


    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            "\nConflict report not found:\n"
            f"{INPUT_CSV}\n\n"
            "Run 10_audit_duplicate_label_conflicts.py first."
        )


    # =====================================================
    # LOAD CONFLICT ROWS
    # =====================================================

    groups = defaultdict(list)


    with INPUT_CSV.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if (
                row.get("status")
                !=
                "cross_class_conflict"
            ):
                continue

            sha256 = (
                row["sha256"]
                .strip()
            )

            groups[sha256].append(row)


    # =====================================================
    # BUILD ONE ROW PER CONFLICT GROUP
    # =====================================================

    group_rows = []

    pair_counter = Counter()

    source_pair_counter = Counter()


    for sha256, rows in groups.items():

        labels = sorted(
            {
                row[
                    "detected_label"
                ].strip()

                for row in rows
            }
        )


        sources = sorted(
            {
                row[
                    "source"
                ].strip()

                for row in rows
            }
        )


        paths = sorted(
            {
                row[
                    "path"
                ].strip()

                for row in rows
            }
        )


        label_pair = (
            " <-> ".join(
                labels
            )
        )


        source_pair = (
            " <-> ".join(
                sources
            )
        )


        pair_counter[
            label_pair
        ] += 1


        source_pair_counter[
            source_pair
        ] += 1


        group_rows.append(
            {
                "sha256":
                    sha256,

                "labels":
                    " | ".join(
                        labels
                    ),

                "sources":
                    " | ".join(
                        sources
                    ),

                "file_count":
                    len(paths),

                "paths":
                    " || ".join(
                        paths
                    ),

                "review_status":
                    "manual_review_required",
            }
        )


    # =====================================================
    # SAVE GROUP-LEVEL REPORT
    # =====================================================

    group_rows.sort(
        key=lambda row: (
            row["labels"],
            row["sha256"],
        )
    )


    with GROUP_OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        fieldnames = [
            "sha256",
            "labels",
            "sources",
            "file_count",
            "paths",
            "review_status",
        ]


        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            group_rows
        )


    # =====================================================
    # SAVE BREED-PAIR SUMMARY
    # =====================================================

    pair_rows = []


    for pair, count in pair_counter.most_common():

        pair_rows.append(
            {
                "conflicting_labels":
                    pair,

                "duplicate_groups":
                    count,
            }
        )


    with PAIR_OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "conflicting_labels",
                "duplicate_groups",
            ],
        )

        writer.writeheader()

        writer.writerows(
            pair_rows
        )


    # =====================================================
    # JSON SUMMARY
    # =====================================================

    summary = {
        "cross_class_conflict_groups":
            len(groups),

        "unique_conflicting_label_combinations":
            len(pair_counter),

        "label_pair_counts":
            dict(
                pair_counter.most_common()
            ),

        "source_pair_counts":
            dict(
                source_pair_counter.most_common()
            ),

        "decision":
            (
                "Do not use conflicting images in the processed "
                "dataset until manually reviewed."
            ),
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
    # TERMINAL OUTPUT
    # =====================================================

    print()

    print(
        "Cross-class conflict groups :",
        len(groups),
    )

    print(
        "Unique label combinations   :",
        len(pair_counter),
    )


    print()
    print("-" * 80)
    print("MOST COMMON CONFLICTING BREED PAIRS")
    print("-" * 80)


    for pair, count in pair_counter.most_common(20):

        print(
            f"{pair:<50} : {count}"
        )


    print()
    print("-" * 80)
    print("CONFLICTS BY SOURCE COMBINATION")
    print("-" * 80)


    for pair, count in source_pair_counter.most_common():

        print(
            f"{pair:<60} : {count}"
        )


    print()

    print(
        "Group report :",
        GROUP_OUTPUT_CSV,
    )

    print(
        "Pair report  :",
        PAIR_OUTPUT_CSV,
    )

    print(
        "Summary      :",
        SUMMARY_JSON,
    )


    print()
    print(
        "No images were modified or deleted."
    )


if __name__ == "__main__":
    main()