import json
import shutil
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


CONFIGS_DIR = (
    PROJECT_ROOT
    / "configs"
)

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)

WEIGHTS_DIR = (
    PROJECT_ROOT
    / "weights"
)


PHASE4_REPORT = (
    REPORTS_DIR
    / "phase4_completion.json"
)

SELECTED_MODEL = (
    CONFIGS_DIR
    / "selected_model.json"
)

TEST_METRICS = (
    REPORTS_DIR
    / "selected_model_test_metrics.json"
)

DATASET_SUMMARY = (
    REPORTS_DIR
    / "final_dataset_summary.json"
)

CLASS_MAPPING = (
    CONFIGS_DIR
    / "class_to_index.json"
)

COMPARISON_REPORT = (
    REPORTS_DIR
    / "phase5_model_comparison.json"
)


OUTPUT_MODEL_CONFIG = (
    CONFIGS_DIR
    / "breed_classifier_v1.json"
)

OUTPUT_COMPLETION_JSON = (
    REPORTS_DIR
    / "phase5_completion.json"
)

OUTPUT_COMPLETION_MD = (
    REPORTS_DIR
    / "phase5_completion_report.md"
)


def load_json(path):

    if not path.exists():

        raise FileNotFoundError(
            f"Required file missing:\n{path}"
        )


    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def main():

    print("=" * 84)
    print(
        "BREEDVISION AI - PHASE 5 FINAL VALIDATION"
    )
    print("=" * 84)


    errors = []
    warnings = []


    # =====================================================
    # LOAD
    # =====================================================

    phase4 = load_json(
        PHASE4_REPORT
    )

    selected = load_json(
        SELECTED_MODEL
    )

    metrics = load_json(
        TEST_METRICS
    )

    dataset = load_json(
        DATASET_SUMMARY
    )

    class_to_index = load_json(
        CLASS_MAPPING
    )

    comparison = load_json(
        COMPARISON_REPORT
    )


    # =====================================================
    # PHASE 4 DEPENDENCY
    # =====================================================

    if phase4.get(
        "status"
    ) != "PASS":

        errors.append(
            "Phase 4 completion status is not PASS."
        )


    # =====================================================
    # CHECKPOINT
    # =====================================================

    checkpoint = Path(
        selected[
            "checkpoint"
        ]
    )


    if not checkpoint.exists():

        errors.append(
            f"Selected checkpoint does not exist: "
            f"{checkpoint}"
        )


    # =====================================================
    # TEST SIZE
    # =====================================================

    expected_test_images = int(
        dataset[
            "split_counts"
        ][
            "test"
        ]
    )


    actual_test_images = int(
        metrics[
            "test_images"
        ]
    )


    if (
        actual_test_images
        !=
        expected_test_images
    ):

        errors.append(
            f"Test image count mismatch: "
            f"expected {expected_test_images}, "
            f"got {actual_test_images}."
        )


    # =====================================================
    # CLASS MAPPING
    # =====================================================

    if (
        metrics[
            "class_to_index"
        ]
        !=
        class_to_index
    ):

        errors.append(
            "Selected model class mapping does not "
            "match dataset class mapping."
        )


    # =====================================================
    # METRICS VALIDITY
    # =====================================================

    metric_names = [
        "accuracy",
        "macro_precision",
        "macro_recall",
        "macro_f1",
        "weighted_f1",
    ]


    for metric_name in metric_names:

        value = float(
            metrics[
                metric_name
            ]
        )


        if not (
            0.0
            <=
            value
            <=
            1.0
        ):

            errors.append(
                f"Invalid metric value: "
                f"{metric_name}={value}"
            )


    # =====================================================
    # CLASS REPORT
    # =====================================================

    classification_report = (
        metrics[
            "classification_report"
        ]
    )


    for breed in class_to_index:

        if breed not in classification_report:

            errors.append(
                f"Missing test metrics for class: "
                f"{breed}"
            )


    # =====================================================
    # REQUIRED REPORTS
    # =====================================================

    required_reports = [
        REPORTS_DIR
        / "selected_model_confusion_matrix.csv",

        REPORTS_DIR
        / "selected_model_confusion_matrix.png",

        REPORTS_DIR
        / "selected_model_per_class_metrics.csv",

        REPORTS_DIR
        / "selected_model_test_predictions.csv",
    ]


    for path in required_reports:

        if not path.exists():

            errors.append(
                f"Missing Phase 5 report: {path}"
            )


    # =====================================================
    # COPY PRODUCTION-CANDIDATE WEIGHT
    # =====================================================

    WEIGHTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    final_weight = (
        WEIGHTS_DIR
        / "breed_classifier_v1.pth"
    )


    if not errors:

        shutil.copy2(
            checkpoint,
            final_weight,
        )


    # =====================================================
    # MODEL CONFIG
    # =====================================================

    model_config = {

        "model_version":
            "breed-classifier-v1",

        "architecture":
            selected[
                "architecture"
            ],

        "selected_run":
            selected[
                "selected_run"
            ],

        "weights":
            "weights/breed_classifier_v1.pth",

        "image_size":
            224,

        "input_channels":
            3,

        "normalization": {
            "mean": [
                0.485,
                0.456,
                0.406
            ],

            "std": [
                0.229,
                0.224,
                0.225
            ]
        },

        "num_classes":
            len(
                class_to_index
            ),

        "class_to_index":
            class_to_index,

        "selection_metric":
            "validation_macro_f1",

        "validation_macro_f1":
            selected[
                "validation_macro_f1"
            ],

        "test_metrics": {
            "accuracy":
                metrics[
                    "accuracy"
                ],

            "macro_precision":
                metrics[
                    "macro_precision"
                ],

            "macro_recall":
                metrics[
                    "macro_recall"
                ],

            "macro_f1":
                metrics[
                    "macro_f1"
                ],

            "weighted_f1":
                metrics[
                    "weighted_f1"
                ],
        }
    }


    with OUTPUT_MODEL_CONFIG.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            model_config,
            file,
            indent=4,
        )


    # =====================================================
    # FINAL STATUS
    # =====================================================

    status = (
        "PASS"
        if not errors
        else
        "FAIL"
    )


    completion = {

        "project":
            "BreedVision AI",

        "phase":
            "Phase 5 - Breed Classifier Training & Benchmarking",

        "status":
            status,

        "validated_at":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "selected_model":
            selected[
                "selected_run"
            ],

        "architecture":
            selected[
                "architecture"
            ],

        "selection_metric":
            "validation_macro_f1",

        "validation_macro_f1":
            selected[
                "validation_macro_f1"
            ],

        "test_accuracy":
            metrics[
                "accuracy"
            ],

        "test_macro_precision":
            metrics[
                "macro_precision"
            ],

        "test_macro_recall":
            metrics[
                "macro_recall"
            ],

        "test_macro_f1":
            metrics[
                "macro_f1"
            ],

        "test_weighted_f1":
            metrics[
                "weighted_f1"
            ],

        "training_ready_images":
            dataset[
                "total_images"
            ],

        "test_images":
            actual_test_images,

        "num_classes":
            len(
                class_to_index
            ),

        "classes":
            list(
                class_to_index.keys()
            ),

        "production_candidate_weights":
            str(
                final_weight
            ),

        "candidate_models_compared":
            len(
                comparison[
                    "candidates"
                ]
            ),

        "errors":
            errors,

        "warnings":
            warnings,
    }


    with OUTPUT_COMPLETION_JSON.open(
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

    markdown = [
        "# BreedVision AI - Phase 5 Completion Report",
        "",
        f"**Status:** {status}",
        "",
        f"**Selected Model:** {selected['selected_run']}",
        "",
        f"**Architecture:** {selected['architecture']}",
        "",
        (
            "**Validation Macro F1:** "
            f"{float(selected['validation_macro_f1']):.4f}"
        ),
        "",
        (
            "**Test Accuracy:** "
            f"{float(metrics['accuracy']):.4f}"
        ),
        "",
        (
            "**Test Macro F1:** "
            f"{float(metrics['macro_f1']):.4f}"
        ),
        "",
        "## Dataset",
        "",
        f"- Total images: {dataset['total_images']}",
        f"- Test images: {actual_test_images}",
        f"- Classes: {len(class_to_index)}",
        "",
        "## Model Selection Policy",
        "",
        (
            "- Candidate models were compared using "
            "validation Macro F1."
        ),
        (
            "- Test metrics were not used to select "
            "the model."
        ),
        (
            "- The selected checkpoint was evaluated "
            "on the held-out test split."
        ),
        "",
        "## Classes",
        "",
    ]


    for breed in class_to_index:

        markdown.append(
            f"- {breed}"
        )


    if errors:

        markdown.extend(
            [
                "",
                "## Errors",
                "",
            ]
        )

        for error in errors:

            markdown.append(
                f"- {error}"
            )


    OUTPUT_COMPLETION_MD.write_text(
        "\n".join(
            markdown
        ),
        encoding="utf-8",
    )


    print()
    print("-" * 84)

    print(
        "Selected model :",
        selected[
            "selected_run"
        ]
    )

    print(
        "Val Macro F1   :",
        round(
            float(
                selected[
                    "validation_macro_f1"
                ]
            ),
            4,
        )
    )

    print(
        "Test Accuracy  :",
        round(
            float(
                metrics[
                    "accuracy"
                ]
            ),
            4,
        )
    )

    print(
        "Test Macro F1  :",
        round(
            float(
                metrics[
                    "macro_f1"
                ]
            ),
            4,
        )
    )


    print()
    print("=" * 84)
    print(
        "PHASE 5 STATUS:",
        status
    )
    print("=" * 84)


    if errors:

        print()

        for error in errors:

            print(
                "[ERROR]",
                error
            )


if __name__ == "__main__":

    main()