import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

FRONTEND = (
    PROJECT_ROOT
    / "frontend"
)

BACKEND = (
    PROJECT_ROOT
    / "backend"
)

REPORTS = (
    PROJECT_ROOT
    / "ml"
    / "reports"
)


def main():

    errors = []


    required_files = [

        FRONTEND
        / "vite.config.js",

        FRONTEND
        / "src/components/pwa/PWAStatus.jsx",

        FRONTEND
        / "src/hooks/useInstallPrompt.js",

        FRONTEND
        / "src/styles/PWA.css",

        FRONTEND
        / "src/styles/Mobile.css",

        FRONTEND
        / "public/icons/pwa-192x192.png",

        FRONTEND
        / "public/icons/pwa-512x512.png",

        FRONTEND
        / "public/icons/pwa-maskable-512x512.png",

        FRONTEND
        / ".env.example",

        BACKEND
        / ".env.example",

    ]


    for path in required_files:

        if not path.exists():

            errors.append(
                f"Missing file: {path}"
            )


    package = json.loads(
        (
            FRONTEND
            / "package.json"
        ).read_text(
            encoding="utf-8"
        )
    )


    dev_dependencies = (
        package.get(
            "devDependencies",
            {}
        )
    )


    dependencies = (
        package.get(
            "dependencies",
            {}
        )
    )


    if (
        "vite-plugin-pwa"
        not in dev_dependencies
        and
        "vite-plugin-pwa"
        not in dependencies
    ):

        errors.append(
            "vite-plugin-pwa is not installed."
        )


    vite_config = (
        FRONTEND
        / "vite.config.js"
    ).read_text(
        encoding="utf-8"
    )


    for token in [

        "VitePWA",

        "registerType",

        "manifest",

        "workbox",

        "navigateFallback",

    ]:

        if token not in vite_config:

            errors.append(
                f"vite.config.js missing {token}"
            )


    pwa_status = (
        FRONTEND
        / "src/components/pwa/PWAStatus.jsx"
    ).read_text(
        encoding="utf-8"
    )


    for token in [

        "offlineReady",

        "needRefresh",

        "updateServiceWorker",

        "navigator.onLine",

        "installAvailable",

    ]:

        if token not in pwa_status:

            errors.append(
                f"PWAStatus missing {token}"
            )


    mobile_css = (
        FRONTEND
        / "src/styles/Mobile.css"
    ).read_text(
        encoding="utf-8"
    )


    for token in [

        "mobile-sidebar-backdrop",

        "translateX",

        "safe-area-inset-bottom",

        "detection-workspace",

    ]:

        if token not in mobile_css:

            errors.append(
                f"Mobile.css missing {token}"
            )


    frontend_env = (
        FRONTEND
        / ".env.example"
    ).read_text(
        encoding="utf-8-sig"
    )


    for token in [

        "VITE_API_BASE_URL",

        "VITE_SUPABASE_URL",

        "VITE_SUPABASE_PUBLISHABLE_KEY",

    ]:

        if token not in frontend_env:

            errors.append(
                f"Frontend environment template missing {token}"
            )


    backend_main = (
        BACKEND
        / "app/main.py"
    ).read_text(
        encoding="utf-8"
    )


    if (
        "CORS_ORIGINS"
        not in backend_main
    ):

        errors.append(
            "Backend CORS is not environment configurable."
        )


    dist = (
        FRONTEND
        / "dist"
    )


    if not (
        dist
        / "sw.js"
    ).exists():

        errors.append(
            "Production service worker is missing."
        )


    manifest_files = [

        path

        for path
        in dist.rglob("*")

        if (
            path.is_file()
            and
            "manifest"
            in path.name.lower()
        )

    ]


    if not manifest_files:

        errors.append(
            "Production web manifest is missing."
        )


    status = (
        "PASS"
        if not errors
        else "FAIL"
    )


    report = {

        "project":
            "BreedVision AI",

        "phase":
            11,

        "status":
            status,

        "validated_at":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "checks": {

            "pwa_configuration":
                "PASS"
                if "VitePWA"
                in vite_config
                else "FAIL",

            "service_worker":
                "PASS"
                if (
                    dist /
                    "sw.js"
                ).exists()
                else "FAIL",

            "manifest":
                "PASS"
                if manifest_files
                else "FAIL",

            "install_update_ui":
                "PASS"
                if (
                    "updateServiceWorker"
                    in pwa_status
                    and
                    "installAvailable"
                    in pwa_status
                )
                else "FAIL",

            "mobile_ui":
                "PASS"
                if (
                    "mobile-sidebar-backdrop"
                    in mobile_css
                )
                else "FAIL",

            "frontend_environment":
                "PASS"
                if (
                    "VITE_API_BASE_URL"
                    in frontend_env
                )
                else "FAIL",

            "backend_cors":
                "PASS"
                if (
                    "CORS_ORIGINS"
                    in backend_main
                )
                else "FAIL",
        },

        "errors":
            errors,
    }


    output = (
        REPORTS
        / "phase11_readiness.json"
    )


    output.write_text(
        json.dumps(
            report,
            indent=4,
        ),
        encoding="utf-8",
    )


    print("=" * 70)

    print(
        "PHASE 11 INTEGRATION READINESS:",
        status,
    )

    print(
        "Errors:",
        len(
            errors
        ),
    )

    print("=" * 70)


    for error in errors:

        print(
            "[ERROR]",
            error
        )


if __name__ == "__main__":

    main()