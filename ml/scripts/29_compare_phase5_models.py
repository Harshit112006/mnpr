import csv
import json
from pathlib import Path


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


CANDIDATES = [
    {
        "name":
            "resnet18_baseline",

        "summary":
            REPORTS_DIR
            / "resnet18_baseline_summary.json",

        "architecture":
            "resnet18",
    },

    {
        "name":
            "efficientnetv2s_stage1",

        "summary":
            REPORTS_DIR
            / "efficientnetv2s_stage1_summary.json",

        "architecture":
            "tf_efficientnetv2_s.in21k_ft_in1k",
    },

    {
        "name":
            "efficientnetv2s_stage2",

        "summary":
            REPORTS_DIR
            / "efficientnetv2s_stage2_summary.json",

        "architecture":
            "tf_efficientnetv2_s.in21k_ft_in1k",
    },
]


def load_json(path):

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def main():

    print("=" * 84)
    print(
        "BREEDVISION AI - PHASE 5 MODEL COMPARISON"
    )
    print("=" * 84)


    results = []


    for candidate in CANDIDATES:

        if not candidate[
            "summary"
        ].exists():

            raise FileNotFoundError(
                f"Missing summary:\n"
                f"{candidate['summary']}"
            )


        summary = load_json(
            candidate[
                "summary"
            ]
        )


        checkpoint = Path(
            summary[
                "checkpoint"
            ]
        )


        if not checkpoint.exists():

            raise FileNotFoundError(
                f"Checkpoint missing:\n"
                f"{checkpoint}"
            )


        results.append(
            {
                "name":
                    candidate[
                        "name"
                    ],

                "architecture":
                    candidate[
                        "architecture"
                    ],

                "validation_macro_f1":
                    float(
                        summary[
                            "best_validation_macro_f1"
                        ]
                    ),

                "best_epoch":
                    int(
                        summary[
                            "best_epoch"
                        ]
                    ),

                "checkpoint":
                    str(
                        checkpoint
                    ),
            }
        )


    results.sort(
        key=lambda row:
            row[
                "validation_macro_f1"
            ],
        reverse=True,
    )


    selected = results[0]


    print()

    for index, result in enumerate(
        results,
        start=1,
    ):

        print(
            f"{index}. "
            f"{result['name']:<28} "
            f"Val Macro F1 = "
            f"{result['validation_macro_f1']:.4f}"
        )


    print()
    print("-" * 84)

    print(
        "Selected model:",
        selected[
            "name"
        ]
    )

    print(
        "Validation Macro F1:",
        round(
            selected[
                "validation_macro_f1"
            ],
            4,
        )
    )


    comparison_csv = (
        REPORTS_DIR
        / "phase5_model_comparison.csv"
    )


    with comparison_csv.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "name",
                "architecture",
                "validation_macro_f1",
                "best_epoch",
                "checkpoint",
            ],
        )

        writer.writeheader()

        writer.writerows(
            results
        )


    comparison_json = (
        REPORTS_DIR
        / "phase5_model_comparison.json"
    )


    with comparison_json.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            {
                "selection_metric":
                    "validation_macro_f1",

                "test_metrics_used_for_selection":
                    False,

                "candidates":
                    results,

                "selected":
                    selected,
            },
            file,
            indent=4,
        )


    selected_config = {

        "model_version":
            "breed-classifier-v1",

        "selected_run":
            selected[
                "name"
            ],

        "architecture":
            selected[
                "architecture"
            ],

        "checkpoint":
            selected[
                "checkpoint"
            ],

        "selection_metric":
            "validation_macro_f1",

        "validation_macro_f1":
            selected[
                "validation_macro_f1"
            ],

        "best_epoch":
            selected[
                "best_epoch"
            ],

        "test_metrics_used_for_selection":
            False,
    }


    selected_path = (
        CONFIGS_DIR
        / "selected_model.json"
    )


    with selected_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            selected_config,
            file,
            indent=4,
        )


    print()
    print("=" * 84)
    print(
        "MODEL SELECTION STATUS: PASS"
    )
    print("=" * 84)


if __name__ == "__main__":

    main()