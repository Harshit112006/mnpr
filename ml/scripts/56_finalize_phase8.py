import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

ML_ROOT = (
    PROJECT_ROOT
    / "ml"
)

BACKEND_ROOT = (
    PROJECT_ROOT
    / "backend"
)

FRONTEND_ROOT = (
    PROJECT_ROOT
    / "frontend"
)

REPORTS_DIR = (
    ML_ROOT
    / "reports"
)


def load_json(
    path,
):

    if not path.exists():

        raise FileNotFoundError(
            path
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(
            file
        )


def main():

    print("=" * 90)
    print(
        "BREEDVISION AI - PHASE 8 FINAL VALIDATION"
    )
    print("=" * 90)

    errors = []
    warnings = []


    phase7 = load_json(
        REPORTS_DIR
        / "phase7_completion.json"
    )

    backend_smoke = (
        load_json(
            REPORTS_DIR
            / "phase8_backend_ml_smoke.json"
        )
    )

    api_test = (
        load_json(
            REPORTS_DIR
            / "phase8_api_integration.json"
        )
    )

    frontend_build = (
        load_json(
            REPORTS_DIR
            / "phase8_frontend_build.json"
        )
    )


    if (
        phase7[
            "status"
        ]
        !=
        "PASS"
    ):

        errors.append(
            "Phase 7 is not PASS."
        )


    if (
        backend_smoke[
            "status"
        ]
        !=
        "PASS"
    ):

        errors.append(
            "Backend ML smoke test failed."
        )


    if (
        api_test[
            "status"
        ]
        !=
        "PASS"
    ):

        errors.append(
            "API integration test failed."
        )


    if (
        frontend_build[
            "status"
        ]
        !=
        "PASS"
    ):

        errors.append(
            "Frontend build failed."
        )


    required_files = [

        BACKEND_ROOT
        / "app"
        / "services"
        / "ml"
        / "paths.py",

        BACKEND_ROOT
        / "app"
        / "services"
        / "ml"
        / "classifier_service.py",

        BACKEND_ROOT
        / "app"
        / "services"
        / "ml"
        / "detector_service.py",

        BACKEND_ROOT
        / "app"
        / "services"
        / "ml"
        / "inference_pipeline.py",

        BACKEND_ROOT
        / "app"
        / "api"
        / "detection.py",

        FRONTEND_ROOT
        / "src"
        / "services"
        / "detectionDataService.js",

        FRONTEND_ROOT
        / "src"
        / "components"
        / "detection"
        / "BackendResultPanel.jsx",

        ML_ROOT
        / "weights"
        / "breed_classifier_v2.pth",

        ML_ROOT
        / "yolov8n.pt",
    ]


    for path in required_files:

        if not path.exists():

            errors.append(
                f"Missing required file: {path}"
            )


    persistence_file = (
        FRONTEND_ROOT
        / "src"
        / "services"
        / "detectionDataService.js"
    )


    persistence_text = (
        persistence_file
        .read_text(
            encoding="utf-8"
        )
    )


    required_persistence_fields = [
        "species:",
        "predicted_breed:",
        "confidence:",
        "top_predictions:",
        "model_version:",
        "backendResult",
    ]


    for token in (
        required_persistence_fields
    ):

        if (
            token
            not in
            persistence_text
        ):

            errors.append(
                "Frontend persistence missing "
                f"token: {token}"
            )


    detection_page = (
        FRONTEND_ROOT
        / "src"
        / "pages"
        / "detection"
        / "Detection.jsx"
    )


    detection_text = (
        detection_page
        .read_text(
            encoding="utf-8"
        )
    )


    if (
        "backendResult:"
        not in
        detection_text
    ):

        errors.append(
            "Detection page does not pass "
            "backend ML result to persistence."
        )


    api_sample = (
        api_test[
            "sample_response"
        ]
    )


    if (
        api_sample.get(
            "prediction"
        )
        is None
    ):

        errors.append(
            "API sample response contains "
            "no classifier prediction."
        )

    else:

        prediction = (
            api_sample[
                "prediction"
            ]
        )

        if len(
            prediction.get(
                "top_predictions",
                [],
            )
        ) != 3:

            errors.append(
                "API sample does not contain Top-3."
            )


        confidence = (
            prediction.get(
                "calibrated_probability"
            )
        )


        if (
            confidence is None
            or
            not (
                0.0
                <=
                float(
                    confidence
                )
                <=
                1.0
            )
        ):

            errors.append(
                "Invalid calibrated probability."
            )


    ml_health = (
        api_test[
            "ml_health"
        ]
    )


    if (
        ml_health.get(
            "status"
        )
        !=
        "ready"
    ):

        errors.append(
            "ML health is not ready."
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
                "Phase 8 - Production ML, "
                "FastAPI, Supabase and "
                "Frontend Integration"
            ),

        "status":
            status,

        "validated_at":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "pipeline": (
            "YOLO bovine detector -> "
            "bovine crop -> "
            "ResNet18 breed classifier v2 -> "
            "temperature scaling -> "
            "unknown handling -> "
            "Top-3 -> FastAPI -> "
            "Supabase -> React"
        ),

        "backend_ml_smoke":
            backend_smoke[
                "status"
            ],

        "api_integration":
            api_test[
                "status"
            ],

        "frontend_build":
            frontend_build[
                "status"
            ],

        "supabase_ml_fields": [
            "species",
            "predicted_breed",
            "confidence",
            "top_predictions",
            "model_version",
        ],

        "errors":
            errors,

        "warnings":
            warnings,
    }


    output = (
        REPORTS_DIR
        / "phase8_completion.json"
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
    print("=" * 90)
    print(
        "PHASE 8 STATUS:",
        status
    )
    print("=" * 90)


    for error in errors:

        print(
            "[ERROR]",
            error
        )


if __name__ == "__main__":

    main()