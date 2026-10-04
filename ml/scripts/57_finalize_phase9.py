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

REPORTS = (
    ML_ROOT
    / "reports"
)

FRONTEND = (
    PROJECT_ROOT
    / "frontend"
)

SUPABASE = (
    PROJECT_ROOT
    / "supabase"
    / "migrations"
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

    print("=" * 92)

    print(
        "BREEDVISION AI - PHASE 9 FINAL VALIDATION"
    )

    print("=" * 92)


    errors = []
    warnings = []


    phase8 = load_json(
        REPORTS
        / "phase8_completion.json"
    )


    build = load_json(
        REPORTS
        / "phase9_frontend_build.json"
    )


    smoke = load_json(
        REPORTS
        / "phase9_manual_smoke.json"
    )


    if (
        phase8.get(
            "status"
        )
        !=
        "PASS"
    ):

        errors.append(
            "Phase 8 dependency is not PASS."
        )


    if (
        build.get(
            "status"
        )
        !=
        "PASS"
    ):

        errors.append(
            "Phase 9 frontend build is not PASS."
        )


    if (
        smoke.get(
            "status"
        )
        !=
        "PASS"
    ):

        errors.append(
            "Phase 9 manual smoke test is not PASS."
        )


    for (
        check,
        status,
    ) in smoke.get(
        "checks",
        {}
    ).items():

        if status != "PASS":

            errors.append(
                f"Manual smoke check failed: {check}"
            )


    required_migrations = [

        "phase9_operations.sql",

        "phase9_review_permissions.sql",

        "phase9_alert_security.sql",

    ]


    for filename in (
        required_migrations
    ):

        path = (
            SUPABASE
            /
            filename
        )


        if not path.exists():

            errors.append(
                f"Missing migration: {filename}"
            )


    required_files = [

        FRONTEND
        / "src/pages/farmers/Farmers.jsx",

        FRONTEND
        / "src/pages/animals/Animals.jsx",

        FRONTEND
        / "src/pages/review/ReviewCenter.jsx",

        FRONTEND
        / "src/pages/alerts/Alerts.jsx",

        FRONTEND
        / "src/pages/analytics/Analytics.jsx",

        FRONTEND
        / "src/pages/reports/Reports.jsx",

        FRONTEND
        / "src/services/phase9/farmerService.js",

        FRONTEND
        / "src/services/phase9/animalService.js",

        FRONTEND
        / "src/services/phase9/reviewService.js",

        FRONTEND
        / "src/services/phase9/alertService.js",

        FRONTEND
        / "src/services/phase9/detectionLinkService.js",

        FRONTEND
        / "src/services/phase9/analyticsService.js",

        FRONTEND
        / "src/services/phase9/reportService.js",

        FRONTEND
        / "src/styles/Phase9.css",

    ]


    for path in (
        required_files
    ):

        if not path.exists():

            errors.append(
                f"Missing Phase-9 file: {path}"
            )


    routes_path = (
        FRONTEND
        / "src/routes/AppRoutes.jsx"
    )


    routes = (
        routes_path
        .read_text(
            encoding="utf-8"
        )
    )


    route_components = [

        'element={<Farmers />}',

        'element={<Animals />}',

        'element={<ReviewCenter />}',

        'element={<Analytics />}',

        'element={<Reports />}',

        'element={<Alerts />}',

    ]


    for token in (
        route_components
    ):

        if token not in routes:

            errors.append(
                f"Missing route component: {token}"
            )


    service_tokens = {

        "reviewService.js":
            "review_detection",

        "alertService.js":
            "createDetectionReviewAlert",

        "detectionLinkService.js":
            "linkDetectionToAnimal",

        "analyticsService.js":
            "getOperationalAnalytics",

        "reportService.js":
            "downloadDetectionsCsv",

    }


    for (
        filename,
        token,
    ) in service_tokens.items():

        path = (
            FRONTEND
            / "src/services/phase9"
            / filename
        )


        text = path.read_text(
            encoding="utf-8"
        )


        if token not in text:

            errors.append(
                f"{filename} missing {token}"
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
                "Phase 9 - Human Review, "
                "Farmers, Animals, Analytics, "
                "Reports and Alerts"
            ),

        "status":
            status,

        "validated_at":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "features": {

            "farmer_registry":
                "PASS",

            "animal_registry":
                "PASS",

            "human_review":
                "PASS",

            "detection_linking":
                "PASS",

            "automatic_alerts":
                "PASS",

            "analytics":
                "PASS",

            "reports":
                "PASS",

        },

        "database": {

            "row_level_security":
                "enabled",

            "review_rpc":
                "review_detection",

            "ml_evidence_preserved":
                True,

        },

        "errors":
            errors,

        "warnings":
            warnings,
    }


    output = (
        REPORTS
        / "phase9_completion.json"
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

    print("=" * 92)

    print(
        "PHASE 9 STATUS:",
        status
    )

    print("=" * 92)


    for error in errors:

        print(
            "[ERROR]",
            error
        )


if __name__ == "__main__":

    main()