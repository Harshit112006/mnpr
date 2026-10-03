import csv
import json
import sys
from pathlib import Path

from fastapi.testclient import (
    TestClient,
)


BACKEND_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

REPO_ROOT = (
    BACKEND_ROOT
    .parent
)

if str(
    BACKEND_ROOT
) not in sys.path:

    sys.path.insert(
        0,
        str(
            BACKEND_ROOT
        ),
    )


from app.main import app


SOURCE_REPORT = (
    REPO_ROOT
    / "ml"
    / "reports"
    / "bovine_detector_validation.csv"
)

OUTPUT_REPORT = (
    REPO_ROOT
    / "ml"
    / "reports"
    / "phase8_api_integration.json"
)


def truthy(
    value,
):

    return (
        str(
            value
        )
        .strip()
        .lower()
        in {
            "true",
            "1",
            "yes",
        }
    )


def main():

    print("=" * 88)
    print(
        "BREEDVISION AI - PHASE 8 API INTEGRATION TEST"
    )
    print("=" * 88)

    client = TestClient(
        app
    )

    health = client.get(
        "/api/health"
    )

    if health.status_code != 200:

        raise RuntimeError(
            "Backend health endpoint failed."
        )

    ml_health = client.get(
        "/api/ml/health"
    )

    if ml_health.status_code != 200:

        raise RuntimeError(
            "ML health endpoint failed."
        )

    ml_health_json = (
        ml_health.json()
    )

    if (
        ml_health_json.get(
            "status"
        )
        !=
        "ready"
    ):

        raise RuntimeError(
            f"ML health not ready: "
            f"{ml_health_json}"
        )

    with SOURCE_REPORT.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        rows = [
            row

            for row
            in csv.DictReader(
                file
            )

            if truthy(
                row[
                    "bovine_detected"
                ]
            )
        ]

    if not rows:

        raise RuntimeError(
            "No detected bovine samples available."
        )

    successful_response = None

    attempted = 0

    for row in rows[
        :10
    ]:

        path = Path(
            row[
                "image_path"
            ]
        )

        if not path.exists():

            continue

        attempted += 1

        suffix = (
            path.suffix.lower()
        )

        mime = (
            "image/png"
            if suffix == ".png"
            else
            "image/webp"
            if suffix == ".webp"
            else
            "image/jpeg"
        )

        with path.open(
            "rb"
        ) as file:

            response = client.post(
                "/api/detect",
                files={
                    "file": (
                        path.name,
                        file,
                        mime,
                    )
                },
            )

        if (
            response.status_code
            !=
            200
        ):

            raise RuntimeError(
                f"/api/detect returned "
                f"{response.status_code}: "
                f"{response.text}"
            )

        body = (
            response.json()
        )

        if (
            body.get(
                "success"
            )
            and
            body.get(
                "bovine",
                {},
            ).get(
                "detected"
            )
            and
            body.get(
                "prediction"
            )
        ):

            successful_response = (
                body
            )

            break

    if successful_response is None:

        raise RuntimeError(
            "Could not obtain one complete "
            "detector + classifier API response."
        )

    prediction = (
        successful_response[
            "prediction"
        ]
    )

    if len(
        prediction[
            "top_predictions"
        ]
    ) != 3:

        raise RuntimeError(
            "API did not return Top-3 predictions."
        )

    report = {
        "status":
            "PASS",

        "attempted_images":
            attempted,

        "health":
            health.json(),

        "ml_health":
            ml_health_json,

        "sample_response":
            successful_response,
    }

    with OUTPUT_REPORT.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
        )

    print()
    print(
        json.dumps(
            successful_response,
            indent=2,
        )
    )

    print()
    print("=" * 88)
    print(
        "PHASE 8 API INTEGRATION: PASS"
    )
    print("=" * 88)


if __name__ == "__main__":

    main()