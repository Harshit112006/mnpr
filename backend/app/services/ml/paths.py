from pathlib import Path


# =========================================================
# BREEDVISION AI
# PHASE 8 - PRODUCTION ML PATHS
# =========================================================


REPO_ROOT = (
    Path(__file__)
    .resolve()
    .parents[4]
)

BACKEND_ROOT = (
    REPO_ROOT
    / "backend"
)

ML_ROOT = (
    REPO_ROOT
    / "ml"
)


CLASSIFIER_WEIGHTS = (
    ML_ROOT
    / "weights"
    / "breed_classifier_v2.pth"
)

CLASSIFIER_CONFIG = (
    ML_ROOT
    / "configs"
    / "breed_classifier_v2.json"
)

SPECIES_MAPPING = (
    ML_ROOT
    / "configs"
    / "classifier_v2_species_mapping.json"
)

CALIBRATION_CONFIG = (
    ML_ROOT
    / "configs"
    / "phase7_calibration.json"
)

UNKNOWN_THRESHOLD_CONFIG = (
    ML_ROOT
    / "configs"
    / "phase7_unknown_threshold.json"
)

DETECTOR_CONFIG = (
    ML_ROOT
    / "configs"
    / "bovine_detector_v1.json"
)

YOLO_WEIGHTS = (
    ML_ROOT
    / "yolov8n.pt"
)


REQUIRED_ML_FILES = {
    "classifier_weights":
        CLASSIFIER_WEIGHTS,

    "classifier_config":
        CLASSIFIER_CONFIG,

    "species_mapping":
        SPECIES_MAPPING,

    "calibration_config":
        CALIBRATION_CONFIG,

    "unknown_threshold_config":
        UNKNOWN_THRESHOLD_CONFIG,

    "detector_config":
        DETECTOR_CONFIG,

    "detector_weights":
        YOLO_WEIGHTS,
}


def validate_ml_paths():

    missing = {
        name:
            str(path)

        for name, path
        in REQUIRED_ML_FILES.items()

        if not path.exists()
    }

    return {
        "repo_root":
            str(REPO_ROOT),

        "ml_root":
            str(ML_ROOT),

        "ready":
            len(missing) == 0,

        "missing":
            missing,
    }