import json
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from inference.phase7_predictor import (
    BreedVisionPhase7Predictor
)


KNOWN_MANIFEST = (
    PROJECT_ROOT
    / "reports"
    / "classifier_v2_final_manifest.csv"
)

OOD_MANIFEST = (
    PROJECT_ROOT
    / "reports"
    / "phase7_ood_manifest.csv"
)

OUTPUT = (
    PROJECT_ROOT
    / "reports"
    / "phase7_top3_predictor_smoke.json"
)


def main():

    print("=" * 90)
    print(
        "BREEDVISION AI - PHASE 7 TOP-3 PREDICTOR TEST"
    )
    print("=" * 90)


    predictor = (
        BreedVisionPhase7Predictor()
    )


    known = pd.read_csv(
        KNOWN_MANIFEST
    )


    known = (
        known[
            known[
                "split"
            ]
            ==
            "test"
        ]
        .head(3)
    )


    ood = pd.read_csv(
        OOD_MANIFEST
    )


    ood = (
        ood[
            ood[
                "ood_split"
            ]
            ==
            "evaluation"
        ]
        .head(3)
    )


    samples = []


    for _, row in known.iterrows():

        samples.append(
            {
                "source":
                    "known_test",

                "actual":
                    row[
                        "breed"
                    ],

                "image_path":
                    row[
                        "image_path"
                    ],
            }
        )


    for _, row in ood.iterrows():

        samples.append(
            {
                "source":
                    "ood_evaluation",

                "actual":
                    row[
                        "breed"
                    ],

                "image_path":
                    row[
                        "image_path"
                    ],
            }
        )


    outputs = []


    for sample in samples:

        prediction = (
            predictor.predict(
                sample[
                    "image_path"
                ],
                top_k=3,
            )
        )


        if len(
            prediction[
                "top3"
            ]
        ) != 3:

            raise RuntimeError(
                "Predictor did not return "
                "exactly Top-3 candidates."
            )


        probabilities = [
            item[
                "calibrated_probability"
            ]

            for item
            in prediction[
                "top3"
            ]
        ]


        if not all(
            0.0
            <=
            probability
            <=
            1.0

            for probability
            in probabilities
        ):

            raise RuntimeError(
                "Invalid calibrated probability."
            )


        if probabilities != sorted(
            probabilities,
            reverse=True,
        ):

            raise RuntimeError(
                "Top-3 predictions are "
                "not sorted correctly."
            )


        outputs.append(
            {
                "source":
                    sample[
                        "source"
                    ],

                "actual":
                    sample[
                        "actual"
                    ],

                "image_path":
                    sample[
                        "image_path"
                    ],

                "prediction":
                    prediction,
            }
        )


    result = {

        "status":
            "PASS",

        "samples_tested":
            len(
                outputs
            ),

        "top_k":
            3,

        "outputs":
            outputs,
    }


    with OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
        )


    for item in outputs:

        print()
        print(
            item[
                "source"
            ],
            "| actual:",
            item[
                "actual"
            ]
        )

        print(
            "Decision:",
            item[
                "prediction"
            ][
                "status"
            ]
        )

        for candidate in (
            item[
                "prediction"
            ][
                "top3"
            ]
        ):

            print(
                f"  #{candidate['rank']} "
                f"{candidate['breed']} "
                f"({candidate['calibrated_probability']:.4f})"
            )


    print()
    print("=" * 90)
    print(
        "PHASE 7 TOP-3 PREDICTOR: PASS"
    )
    print("=" * 90)


if __name__ == "__main__":
    main()