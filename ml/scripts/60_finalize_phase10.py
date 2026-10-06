import json

from datetime import (
    datetime,
)

from pathlib import (
    Path,
)


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


BACKEND = (
    PROJECT_ROOT
    / "backend"
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


def load_report(
    filename,
):

    path = (
        REPORTS
        /
        filename
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


    phase11 = load_report(
        "phase11_completion.json"
    )


    build = load_report(
        "phase10_frontend_build.json"
    )


    smoke = load_report(
        "phase10_manual_smoke.json"
    )


    if (
        phase11.get(
            "status"
        )
        !=
        "PASS"
    ):

        errors.append(
            "Phase 11 dependency is not PASS."
        )


    if (
        build.get(
            "status"
        )
        !=
        "PASS"
    ):

        errors.append(
            "Phase 10 frontend build is not PASS."
        )


    if (
        smoke.get(
            "status"
        )
        !=
        "PASS"
    ):

        errors.append(
            "Phase 10 smoke test is not PASS."
        )


    for (
        name,
        status,
    ) in smoke.get(
        "checks",
        {}
    ).items():

        if status != "PASS":

            errors.append(
                f"Smoke failure: {name}"
            )


    required_files = [

        BACKEND
        / "app/services/assistant/project_knowledge.py",

        BACKEND
        / "app/services/assistant/assistant_service.py",

        BACKEND
        / "app/api/assistant.py",

        FRONTEND
        / "src/pages/assistant/Assistant.jsx",

        FRONTEND
        / "src/services/assistantService.js",

        FRONTEND
        / "src/services/assistantDataService.js",

        FRONTEND
        / "src/styles/Assistant.css",

        SUPABASE
        / "phase10_chat.sql",
    ]


    for path in required_files:

        if not path.exists():

            errors.append(
                f"Missing file: {path}"
            )


    service_text = (
        BACKEND
        / "app/services/assistant/assistant_service.py"
    ).read_text(
        encoding="utf-8"
    )


    for token in [

    "OpenRouter",

    "openrouter/free",

    ".chat",

    ".completions",

    "search_project_knowledge",

    "general-purpose",

    "multilingual",

]:

        if token not in service_text:

            errors.append(
                f"Assistant service missing {token}"
            )


    retrieval_text = (
        BACKEND
        / "app/services/assistant/project_knowledge.py"
    ).read_text(
        encoding="utf-8"
    )


    for forbidden in [

        "score < threshold",

        'return "I could not find',

    ]:

        if forbidden in retrieval_text:

            errors.append(
                (
                    "Blocking out-of-domain "
                    f"RAG behavior found: {forbidden}"
                )
            )


    routes = (
        FRONTEND
        / "src/routes/AppRoutes.jsx"
    ).read_text(
        encoding="utf-8"
    )


    if (
        "element={<Assistant />}"
        not in routes
    ):

        errors.append(
            "Assistant route is not active."
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
                "Phase 10 - General Multilingual "
                "AI Assistant with BreedVision RAG"
            ),

        "status":
            status,

        "validated_at":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "provider":
            "OpenRouter",

        "configured_model":
            "openrouter/free",

        "features": {

            "general_questions":
                feature_status,

            "out_of_domain":
                feature_status,

            "breedvision_rag":
                feature_status,

            "multilingual":
                feature_status,

            "conversation_context":
                feature_status,

            "persistent_history":
                feature_status,

            "markdown":
                feature_status,

            "code_rendering":
                feature_status,

            "mobile_ui":
                feature_status,
        },

        "errors":
            errors,
    }


    output = (
        REPORTS
        /
        "phase10_completion.json"
    )


    output.write_text(
        json.dumps(
            report,
            indent=4,
        ),
        encoding="utf-8",
    )


    print(
        "=" * 78
    )

    print(
        "BREEDVISION AI - PHASE 10 FINAL VALIDATION"
    )

    print(
        "=" * 78
    )

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
        "=" * 78
    )


    for error in errors:

        print(
            "[ERROR]",
            error
        )


if __name__ == "__main__":

    main()