import json
import math
from datetime import datetime
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

PHASE7_DIR = (
    PROJECT_ROOT
    / "phase7"
)


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


def valid_probability(
    value,
):

    return (
        isinstance(
            value,
            (
                int,
                float,
            ),
        )
        and
        math.isfinite(
            float(
                value
            )
        )
        and
        0.0
        <=
        float(
            value
        )
        <=
        1.0
    )


def main():

    print("=" * 94)
    print(
        "BREEDVISION AI - PHASE 7 FINAL VALIDATION"
    )
    print("=" * 94)


    errors = []
    warnings = []


    calibration = load_json(
        CONFIGS_DIR
        / "phase7_calibration.json"
    )


    calibration_metrics = load_json(
        REPORTS_DIR
        / "phase7_calibration_metrics.json"
    )


    ood_summary = load_json(
        REPORTS_DIR
        / "phase7_ood_summary.json"
    )


    threshold = load_json(
        CONFIGS_DIR
        / "phase7_unknown_threshold.json"
    )


    threshold_report = load_json(
        REPORTS_DIR
        / "phase7_unknown_threshold_selection.json"
    )


    open_set = load_json(
        REPORTS_DIR
        / "phase7_open_set_evaluation.json"
    )


    predictor = load_json(
        REPORTS_DIR
        / "phase7_top3_predictor_smoke.json"
    )


    gradcam = load_json(
        REPORTS_DIR
        / "phase7_gradcam_summary.json"
    )


    # =====================================================
    # CALIBRATION
    # =====================================================


    temperature = float(
        calibration[
            "temperature"
        ]
    )


    if not (
        math.isfinite(
            temperature
        )
        and
        temperature
        >
        0
    ):

        errors.append(
            "Invalid calibration temperature."
        )


    before_nll = float(
        calibration_metrics[
            "before_calibration"
        ][
            "negative_log_likelihood"
        ]
    )


    after_nll = float(
        calibration_metrics[
            "after_calibration"
        ][
            "negative_log_likelihood"
        ]
    )


    if (
        after_nll
        >
        before_nll
        +
        1e-6
    ):

        errors.append(
            "Validation NLL worsened after "
            "temperature scaling."
        )


    # =====================================================
    # OOD DATASET
    # =====================================================


    if (
        ood_summary[
            "group_leakage_count"
        ]
        !=
        0
    ):

        errors.append(
            "OOD near-duplicate leakage detected."
        )


    if (
        ood_summary[
            "threshold_tuning_images"
        ]
        <=
        0
        or
        ood_summary[
            "evaluation_images"
        ]
        <=
        0
    ):

        errors.append(
            "OOD tuning/evaluation split incomplete."
        )


    # =====================================================
    # THRESHOLD
    # =====================================================


    unknown_threshold = float(
        threshold[
            "threshold"
        ]
    )


    if not (
        0.0
        <
        unknown_threshold
        <
        1.0
    ):

        errors.append(
            "Invalid unknown threshold."
        )


    if (
        threshold[
            "test_data_used_for_selection"
        ]
        is not False
    ):

        errors.append(
            "Test data was used for threshold tuning."
        )


    # =====================================================
    # FINAL TEST PROTOCOL
    # =====================================================


    protocol = (
        open_set[
            "evaluation_protocol"
        ]
    )


    if (
        protocol[
            "threshold_frozen_before_test"
        ]
        is not True
    ):

        errors.append(
            "Threshold was not frozen before test."
        )


    if (
        protocol[
            "test_used_for_tuning"
        ]
        is not False
    ):

        errors.append(
            "Test data contamination detected."
        )


    # =====================================================
    # KNOWN TEST
    # =====================================================


    known = (
        open_set[
            "known_test"
        ]
    )


    for metric in [
        "top1_accuracy",
        "top3_accuracy",
        "known_acceptance_rate",
        "known_rejection_rate",
    ]:

        if not valid_probability(
            known[
                metric
            ]
        ):

            errors.append(
                f"Invalid known-test metric: "
                f"{metric}"
            )


    if (
        known[
            "top3_accuracy"
        ]
        <
        known[
            "top1_accuracy"
        ]
    ):

        errors.append(
            "Top-3 accuracy is below Top-1 accuracy."
        )


    # =====================================================
    # OOD + OPEN SET
    # =====================================================


    ood = (
        open_set[
            "ood_evaluation"
        ]
    )


    open_metrics = (
        open_set[
            "open_set"
        ]
    )


    for metric in [
        "ood_rejection_rate",
        "ood_false_acceptance_rate",
    ]:

        if not valid_probability(
            ood[
                metric
            ]
        ):

            errors.append(
                f"Invalid OOD metric: "
                f"{metric}"
            )


    for metric in [
        "balanced_accuracy",
        "auroc",
        "aupr_ood",
        "unknown_f1",
    ]:

        if not valid_probability(
            open_metrics[
                metric
            ]
        ):

            errors.append(
                f"Invalid open-set metric: "
                f"{metric}"
            )


    # Performance warnings only.
    # They do NOT invalidate methodology.

    if (
        open_metrics[
            "auroc"
        ]
        <
        0.70
    ):

        warnings.append(
            "Open-set AUROC is below 0.70. "
            "Unknown/OOD separation may need "
            "stronger methods in future versions."
        )


    if (
        ood[
            "ood_rejection_rate"
        ]
        <
        0.60
    ):

        warnings.append(
            "Final OOD rejection rate is below 60%."
        )


    # =====================================================
    # TOP-3 PREDICTOR
    # =====================================================


    if (
        predictor[
            "status"
        ]
        !=
        "PASS"
    ):

        errors.append(
            "Top-3 predictor smoke test failed."
        )


    if (
        predictor[
            "top_k"
        ]
        !=
        3
    ):

        errors.append(
            "Top-3 predictor is not configured for k=3."
        )


    # =====================================================
    # GRAD-CAM
    # =====================================================


    if (
        gradcam[
            "status"
        ]
        !=
        "PASS"
    ):

        errors.append(
            "Grad-CAM validation failed."
        )


    if (
        gradcam[
            "samples_generated"
        ]
        <=
        0
    ):

        errors.append(
            "No Grad-CAM samples generated."
        )


    for file_path in (
        gradcam[
            "files"
        ]
    ):

        if not Path(
            file_path
        ).exists():

            errors.append(
                f"Missing Grad-CAM file: "
                f"{file_path}"
            )


    # =====================================================
    # REQUIRED FILES
    # =====================================================


    required_files = [

        CONFIGS_DIR
        / "phase7_config.json",

        CONFIGS_DIR
        / "phase7_calibration.json",

        CONFIGS_DIR
        / "phase7_unknown_threshold.json",

        REPORTS_DIR
        / "phase7_validation_predictions_raw.csv",

        REPORTS_DIR
        / "phase7_calibration_metrics.json",

        REPORTS_DIR
        / "phase7_ood_manifest.csv",

        REPORTS_DIR
        / "phase7_ood_summary.json",

        REPORTS_DIR
        / "phase7_unknown_threshold_selection.json",

        REPORTS_DIR
        / "phase7_open_set_predictions.csv",

        REPORTS_DIR
        / "phase7_open_set_evaluation.json",

        REPORTS_DIR
        / "phase7_top3_predictor_smoke.json",

        REPORTS_DIR
        / "phase7_gradcam_examples.csv",

        REPORTS_DIR
        / "phase7_gradcam_summary.json",
    ]


    for path in required_files:

        if not path.exists():

            errors.append(
                f"Missing Phase-7 artifact: "
                f"{path}"
            )


    # =====================================================
    # COMPLETION
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
            (
                "Phase 7 - Confidence, Top-3, "
                "Unknown Handling, Grad-CAM and Evaluation"
            ),

        "status":
            status,

        "validated_at":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "classifier_version":
            "v2",

        "calibration": {
            "method":
                calibration[
                    "method"
                ],

            "temperature":
                temperature,

            "validation_nll_before":
                before_nll,

            "validation_nll_after":
                after_nll,

            "validation_ece_before":
                calibration_metrics[
                    "before_calibration"
                ][
                    "expected_calibration_error"
                ],

            "validation_ece_after":
                calibration_metrics[
                    "after_calibration"
                ][
                    "expected_calibration_error"
                ],
        },

        "unknown_handling": {
            "threshold":
                unknown_threshold,

            "ood_breeds":
                ood_summary[
                    "ood_breeds"
                ],

            "threshold_tuning_balanced_accuracy":
                threshold_report[
                    "selected"
                ][
                    "balanced_accuracy"
                ],

            "test_known_acceptance_rate":
                known[
                    "known_acceptance_rate"
                ],

            "test_ood_rejection_rate":
                ood[
                    "ood_rejection_rate"
                ],

            "test_open_set_auroc":
                open_metrics[
                    "auroc"
                ],
        },

        "classification": {
            "test_top1_accuracy":
                known[
                    "top1_accuracy"
                ],

            "test_top3_accuracy":
                known[
                    "top3_accuracy"
                ],

            "selective_top1_accuracy":
                known[
                    "selective_top1_accuracy"
                ],
        },

        "explainability": {
            "method":
                gradcam[
                    "method"
                ],

            "target_layer":
                gradcam[
                    "target_layer"
                ],

            "gradcam_examples":
                gradcam[
                    "samples_generated"
                ],
        },

        "errors":
            errors,

        "warnings":
            warnings,
    }


    output = (
        REPORTS_DIR
        / "phase7_completion.json"
    )


    with output.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            completion,
            file,
            indent=4,
        )


    print()
    print(
        "Errors:",
        len(
            errors
        )
    )

    print(
        "Warnings:",
        len(
            warnings
        )
    )

    print()
    print(
        "Top-1:",
        round(
            float(
                known[
                    "top1_accuracy"
                ]
            ),
            4,
        )
    )

    print(
        "Top-3:",
        round(
            float(
                known[
                    "top3_accuracy"
                ]
            ),
            4,
        )
    )

    print(
        "Known acceptance:",
        round(
            float(
                known[
                    "known_acceptance_rate"
                ]
            ),
            4,
        )
    )

    print(
        "OOD rejection:",
        round(
            float(
                ood[
                    "ood_rejection_rate"
                ]
            ),
            4,
        )
    )

    print(
        "Open-set AUROC:",
        round(
            float(
                open_metrics[
                    "auroc"
                ]
            ),
            4,
        )
    )


    print()
    print("=" * 94)
    print(
        "PHASE 7 STATUS:",
        status
    )
    print("=" * 94)


    for warning in warnings:

        print(
            "[WARNING]",
            warning
        )


    for error in errors:

        print(
            "[ERROR]",
            error
        )


if __name__ == "__main__":
    main()