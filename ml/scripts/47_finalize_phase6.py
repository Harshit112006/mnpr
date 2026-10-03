import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)

CONFIGS_DIR = (
    PROJECT_ROOT
    / "configs"
)

WEIGHTS_DIR = (
    PROJECT_ROOT
    / "weights"
)


def load_json(path):

    if not path.exists():

        raise FileNotFoundError(
            path
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def main():

    print("=" * 88)
    print(
        "BREEDVISION AI - PHASE 6 FINAL VALIDATION"
    )
    print("=" * 88)

    errors = []
    warnings = []

    leakage = load_json(
        REPORTS_DIR
        / "classifier_v2_leakage_audit.json"
    )

    classifier = load_json(
        REPORTS_DIR
        / "classifier_v2_test_metrics.json"
    )

    detector = load_json(
        REPORTS_DIR
        / "bovine_detector_validation.json"
    )

    pipeline = load_json(
        REPORTS_DIR
        / "bovine_classifier_pipeline_smoke.json"
    )

    dataset_config = load_json(
        CONFIGS_DIR
        / "classifier_v2_dataset_config.json"
    )

    if leakage[
        "status"
    ] != "PASS":

        errors.append(
            "Classifier-v2 leakage audit failed."
        )

    if leakage[
        "group_leakage_count"
    ] != 0:

        errors.append(
            "Group leakage is not zero."
        )

    if leakage[
        "sha256_leakage_count"
    ] != 0:

        errors.append(
            "SHA256 leakage is not zero."
        )

    expected_classes = int(
        dataset_config[
            "num_classes"
        ]
    )

    if len(
        classifier[
            "class_to_index"
        ]
    ) != expected_classes:

        errors.append(
            "Classifier class count mismatch."
        )

    for metric in [
        "accuracy",
        "macro_precision",
        "macro_recall",
        "macro_f1",
        "weighted_f1",
    ]:

        value = float(
            classifier[
                metric
            ]
        )

        if not (
            0.0
            <= value
            <= 1.0
        ):

            errors.append(
                f"Invalid metric {metric}."
            )

    species_summary = (
        detector[
            "species_summary"
        ]
    )

    for species in [
        "cattle",
        "buffalo",
    ]:

        if (
            species
            not in
            species_summary
        ):

            errors.append(
                f"Detector missing species: "
                f"{species}"
            )

            continue

        detected = int(
            species_summary[
                species
            ][
                "detected"
            ]
        )

        coverage = float(
            species_summary[
                species
            ][
                "detection_coverage"
            ]
        )

        if detected <= 0:

            errors.append(
                f"Detector produced zero "
                f"detections for {species}."
            )

        if coverage < 0.60:

            warnings.append(
                f"Detector coverage for "
                f"{species} is below 60%: "
                f"{coverage:.4f}"
            )

    pipeline_species = (
        pipeline[
            "species_summary"
        ]
    )

    for species in [
        "cattle",
        "buffalo",
    ]:

        if (
            species
            not in
            pipeline_species
        ):

            errors.append(
                f"Pipeline missing species: "
                f"{species}"
            )

            continue

        if int(
            pipeline_species[
                species
            ][
                "classified"
            ]
        ) <= 0:

            errors.append(
                f"Pipeline classified zero "
                f"{species} images."
            )

    required_files = [
        WEIGHTS_DIR
        / "breed_classifier_v2.pth",

        CONFIGS_DIR
        / "breed_classifier_v2.json",

        CONFIGS_DIR
        / "bovine_detector_v1.json",

        REPORTS_DIR
        / "classifier_v2_confusion_matrix.png",

        REPORTS_DIR
        / "classifier_v2_per_class_metrics.csv",

        REPORTS_DIR
        / "bovine_detector_validation.csv",

        REPORTS_DIR
        / "bovine_classifier_pipeline_smoke.csv",
    ]

    for path in required_files:

        if not path.exists():

            errors.append(
                f"Missing required file: "
                f"{path}"
            )

    status = (
        "PASS"
        if not errors
        else "FAIL"
    )

    result = {
        "project":
            "BreedVision AI",

        "phase":
            (
                "Phase 6 - Cattle + Buffalo Expansion "
                "and Bovine Detection"
            ),

        "status":
            status,

        "validated_at":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "classifier_version":
            "v2",

        "num_classes":
            expected_classes,

        "cattle_classes":
            dataset_config[
                "cattle_classes"
            ],

        "buffalo_classes":
            dataset_config[
                "buffalo_classes"
            ],

        "classifier_test_accuracy":
            classifier[
                "accuracy"
            ],

        "classifier_test_macro_f1":
            classifier[
                "macro_f1"
            ],

        "detector":
            detector[
                "detector"
            ],

        "detector_species_summary":
            species_summary,

        "pipeline_species_summary":
            pipeline_species,

        "errors":
            errors,

        "warnings":
            warnings,
    }

    output = (
        REPORTS_DIR
        / "phase6_completion.json"
    )

    with output.open(
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
        "Classifier Macro F1:",
        round(
            float(
                classifier[
                    "macro_f1"
                ]
            ),
            4,
        )
    )

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
    print("=" * 88)
    print(
        "PHASE 6 STATUS:",
        status
    )
    print("=" * 88)

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