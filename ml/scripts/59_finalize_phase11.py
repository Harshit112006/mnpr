import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

REPORTS = (
    PROJECT_ROOT
    / "ml"
    / "reports"
)


def load_report(
    filename,
):

    path = (
        REPORTS
        / filename
    )


    if not path.exists():

        raise FileNotFoundError(
            path
        )


    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def main():

    errors = []

    warnings = []


    phase9 = load_report(
        "phase9_completion.json"
    )


    build = load_report(
        "phase11_build.json"
    )


    readiness = load_report(
        "phase11_readiness.json"
    )


    smoke = load_report(
        "phase11_manual_smoke.json"
    )


    if (
        phase9.get(
            "status"
        )
        !=
        "PASS"
    ):

        errors.append(
            "Phase 9 dependency is not PASS."
        )


    if (
        build.get(
            "status"
        )
        !=
        "PASS"
    ):

        errors.append(
            "Phase 11 build report is not PASS."
        )


    if (
        readiness.get(
            "status"
        )
        !=
        "PASS"
    ):

        errors.append(
            "Phase 11 integration readiness is not PASS."
        )


    if (
        smoke.get(
            "status"
        )
        !=
        "PASS"
    ):

        errors.append(
            "Phase 11 manual smoke test is not PASS."
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
                f"Manual smoke failed: {check}"
            )


    if not build.get(
        "service_worker",
        False,
    ):

        errors.append(
            "Service worker build evidence missing."
        )


    if not build.get(
        "manifest_files",
        [],
    ):

        errors.append(
            "Manifest build evidence missing."
        )


    physical_device = (
        smoke
        .get(
            "test_environment",
            {}
        )
        .get(
            "physical_device",
            ""
        )
    )


    if (
        "Not required"
        in physical_device
    ):

        warnings.append(
            (
                "Physical-device HTTPS camera verification "
                "is deferred to Phase 12 deployment testing."
            )
        )


    status = (
        "PASS"
        if not errors
        else "FAIL"
    )


    feature_status = (
        "PASS"
        if status == "PASS"
        else "FAIL"
    )


    report = {

        "project":
            "BreedVision AI",

        "phase":
            (
                "Phase 11 - PWA, Mobile Experience "
                "and Integration Readiness"
            ),

        "status":
            status,

        "validated_at":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "phase10_dependency":
            "NOT REQUIRED",

        "features": {

            "pwa_manifest":
                feature_status,

            "service_worker":
                feature_status,

            "offline_shell":
                feature_status,

            "install_workflow":
                feature_status,

            "update_workflow":
                feature_status,

            "connectivity_awareness":
                feature_status,

            "mobile_navigation":
                feature_status,

            "mobile_detection_ux":
                feature_status,

            "touch_readiness":
                feature_status,

            "production_environment_config":
                feature_status,

            "production_cors_config":
                feature_status,
        },

        "errors":
            errors,

        "warnings":
            warnings,
    }


    output = (
        REPORTS
        / "phase11_completion.json"
    )


    output.write_text(
        json.dumps(
            report,
            indent=4,
        ),
        encoding="utf-8",
    )


    print()

    print("=" * 78)

    print(
        "BREEDVISION AI - PHASE 11 FINAL VALIDATION"
    )

    print("=" * 78)

    print(
        "Status:",
        status
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

    print("=" * 78)


    for error in errors:

        print(
            "[ERROR]",
            error
        )


    for warning in warnings:

        print(
            "[WARNING]",
            warning
        )


if __name__ == "__main__":

    main()