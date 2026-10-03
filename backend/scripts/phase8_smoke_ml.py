import csv
import json
import sys
from pathlib import Path

from PIL import Image


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


from app.services.ml.inference_pipeline import (
    get_inference_pipeline,
)


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
    / "phase8_backend_ml_smoke.json"
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
        "BREEDVISION AI - PHASE 8 BACKEND ML SMOKE TEST"
    )
    print("=" * 88)

    if not SOURCE_REPORT.exists():

        raise FileNotFoundError(
            SOURCE_REPORT
        )

    with SOURCE_REPORT.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        rows = list(
            csv.DictReader(
                file
            )
        )

    candidates = {
        "cattle": None,
        "buffalo": None,
    }

    for row in rows:

        species = (
            row[
                "species"
            ]
        )

        if (
            species
            in candidates
            and
            candidates[
                species
            ]
            is None
            and
            truthy(
                row[
                    "bovine_detected"
                ]
            )
        ):

            candidates[
                species
            ] = (
                row
            )

    missing = [
        species

        for species, row
        in candidates.items()

        if row is None
    ]

    if missing:

        raise RuntimeError(
            "No previously detected validation "
            f"sample for: {missing}"
        )

    pipeline = (
        get_inference_pipeline()
    )

    outputs = {}

    for species, row in (
        candidates.items()
    ):

        image_path = Path(
            row[
                "image_path"
            ]
        )

        print()
        print(
            "Testing:",
            species,
            image_path,
        )

        with Image.open(
            image_path
        ) as image:

            result = (
                pipeline.predict(
                    image
                )
            )

        outputs[
            species
        ] = (
            result
        )

        print(
            json.dumps(
                result,
                indent=2,
            )
        )

        if not result[
            "bovine"
        ][
            "detected"
        ]:

            raise RuntimeError(
                f"Detector failed smoke test for {species}."
            )

        prediction = (
            result[
                "prediction"
            ]
        )

        if prediction is None:

            raise RuntimeError(
                f"Classifier was not executed for {species}."
            )

        if len(
            prediction[
                "top_predictions"
            ]
        ) != 3:

            raise RuntimeError(
                "Top-3 result missing."
            )

    report = {
        "status":
            "PASS",

        "pipeline":
            (
                "YOLO bovine detector -> crop -> "
                "ResNet18 classifier v2 -> "
                "temperature calibration -> "
                "unknown threshold -> Top-3"
            ),

        "samples":
            outputs,
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
    print("=" * 88)
    print(
        "PHASE 8 BACKEND ML SMOKE: PASS"
    )
    print("=" * 88)


if __name__ == "__main__":

    main()