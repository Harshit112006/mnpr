import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from PIL import Image
from sklearn.metrics import roc_auc_score
from torchvision import models


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


from training.dataset_v2 import (
    build_eval_transform
)


WEIGHTS_PATH = (
    PROJECT_ROOT
    / "weights"
    / "breed_classifier_v2.pth"
)

CALIBRATION_CONFIG = (
    PROJECT_ROOT
    / "configs"
    / "phase7_calibration.json"
)

PHASE7_CONFIG = (
    PROJECT_ROOT
    / "configs"
    / "phase7_config.json"
)

KNOWN_CACHE = (
    PROJECT_ROOT
    / "phase7"
    / "cache"
    / "validation_calibrated.npz"
)

OOD_MANIFEST = (
    PROJECT_ROOT
    / "reports"
    / "phase7_ood_manifest.csv"
)

OUTPUT_CONFIG = (
    PROJECT_ROOT
    / "configs"
    / "phase7_unknown_threshold.json"
)

OUTPUT_REPORT = (
    PROJECT_ROOT
    / "reports"
    / "phase7_unknown_threshold_selection.json"
)

OUTPUT_CSV = (
    PROJECT_ROOT
    / "reports"
    / "phase7_ood_tuning_scores.csv"
)


def load_json(path):

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def load_model(
    device,
):

    checkpoint = torch.load(
        WEIGHTS_PATH,
        map_location=device,
        weights_only=False,
    )

    class_to_index = (
        checkpoint[
            "class_to_index"
        ]
    )

    model = models.resnet18(
        weights=None
    )

    model.fc = nn.Linear(
        model.fc.in_features,
        len(
            class_to_index
        ),
    )

    model.load_state_dict(
        checkpoint[
            "model_state_dict"
        ]
    )

    model = model.to(
        device
    )

    model.eval()

    return (
        model,
        class_to_index,
    )


def collect_ood_scores(
    model,
    dataframe,
    transform,
    temperature,
    device,
):

    rows = []
    scores = []


    with torch.no_grad():

        for index, row in dataframe.iterrows():

            image_path = Path(
                row[
                    "image_path"
                ]
            )

            with Image.open(
                image_path
            ) as image:

                image = image.convert(
                    "RGB"
                )

                tensor = (
                    transform(
                        image
                    )
                    .unsqueeze(0)
                    .to(device)
                )


            logits = model(
                tensor
            )


            calibrated_logits = (
                logits
                /
                temperature
            )


            probabilities = torch.softmax(
                calibrated_logits,
                dim=1,
            )


            score, predicted = (
                probabilities.max(
                    dim=1
                )
            )


            max_probability = float(
                score.item()
            )


            predicted_index = int(
                predicted.item()
            )


            scores.append(
                max_probability
            )


            rows.append(
                {
                    "image_path":
                        str(
                            image_path
                        ),

                    "actual_ood_breed":
                        row[
                            "breed"
                        ],

                    "predicted_class_index":
                        predicted_index,

                    "max_calibrated_probability":
                        max_probability,
                }
            )


            current = (
                index + 1
            )


            if (
                current % 20 == 0
                or
                current
                ==
                len(
                    dataframe
                )
            ):

                print(
                    f"OOD tuning inference "
                    f"{current}/"
                    f"{len(dataframe)}"
                )


    return (
        np.array(
            scores,
            dtype=np.float64,
        ),
        rows,
    )


def evaluate_threshold(
    threshold,
    known_scores,
    ood_scores,
):

    known_acceptance = float(
        np.mean(
            known_scores
            >=
            threshold
        )
    )


    ood_rejection = float(
        np.mean(
            ood_scores
            <
            threshold
        )
    )


    balanced_accuracy = (
        known_acceptance
        +
        ood_rejection
    ) / 2.0


    minimum_side = min(
        known_acceptance,
        ood_rejection,
    )


    return {
        "threshold":
            float(
                threshold
            ),

        "known_acceptance_rate":
            known_acceptance,

        "ood_rejection_rate":
            ood_rejection,

        "balanced_accuracy":
            balanced_accuracy,

        "minimum_class_rate":
            minimum_side,
    }


def main():

    print("=" * 94)
    print(
        "BREEDVISION AI - PHASE 7 UNKNOWN THRESHOLD SELECTION"
    )
    print("=" * 94)


    calibration = load_json(
        CALIBRATION_CONFIG
    )

    temperature = float(
        calibration[
            "temperature"
        ]
    )


    cache = np.load(
        KNOWN_CACHE
    )


    known_probabilities = (
        cache[
            "calibrated_probabilities"
        ]
    )


    known_scores = np.max(
        known_probabilities,
        axis=1,
    )


    ood_dataframe = pd.read_csv(
        OOD_MANIFEST
    )


    tuning_dataframe = (
        ood_dataframe[
            ood_dataframe[
                "ood_split"
            ]
            ==
            "threshold_tuning"
        ]
        .reset_index(
            drop=True
        )
    )


    if len(
        tuning_dataframe
    ) == 0:

        raise RuntimeError(
            "OOD threshold tuning set is empty."
        )


    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else
        "cpu"
    )


    print()
    print(
        "Device:",
        device
    )

    print(
        "Temperature:",
        temperature
    )

    print(
        "Known validation samples:",
        len(
            known_scores
        )
    )

    print(
        "OOD tuning samples:",
        len(
            tuning_dataframe
        )
    )


    model, class_to_index = (
        load_model(
            device
        )
    )


    transform = (
        build_eval_transform(
            224
        )
    )


    ood_scores, ood_rows = (
        collect_ood_scores(
            model=
                model,

            dataframe=
                tuning_dataframe,

            transform=
                transform,

            temperature=
                temperature,

            device=
                device,
        )
    )


    # =====================================================
    # THRESHOLD CANDIDATES
    # =====================================================


    combined_scores = np.concatenate(
        [
            known_scores,
            ood_scores,
        ]
    )


    unique_scores = np.unique(
        combined_scores
    )


    candidates = [
        0.0,
        1.0,
    ]


    candidates.extend(
        unique_scores.tolist()
    )


    if len(
        unique_scores
    ) >= 2:

        midpoints = (
            unique_scores[:-1]
            +
            unique_scores[1:]
        ) / 2.0

        candidates.extend(
            midpoints.tolist()
        )


    candidates = sorted(
        set(
            float(
                value
            )
            for value in candidates
            if (
                0.0
                <=
                value
                <=
                1.0
            )
        )
    )


    results = [
        evaluate_threshold(
            threshold=
                threshold,

            known_scores=
                known_scores,

            ood_scores=
                ood_scores,
        )

        for threshold in candidates
    ]


    # Priority:
    # 1. Balanced accuracy
    # 2. Strongest weaker side
    # 3. Known acceptance
    # 4. Lower threshold if still tied

    best = max(
        results,
        key=lambda item: (
            item[
                "balanced_accuracy"
            ],

            item[
                "minimum_class_rate"
            ],

            item[
                "known_acceptance_rate"
            ],

            -item[
                "threshold"
            ],
        ),
    )


    threshold = float(
        best[
            "threshold"
        ]
    )


    if not (
        0.0
        <
        threshold
        <
        1.0
    ):

        raise RuntimeError(
            "Selected threshold is at an "
            "invalid extreme value."
        )


    # =====================================================
    # OOD SEPARABILITY DIAGNOSTIC
    # =====================================================


    binary_labels = np.concatenate(
        [
            np.zeros(
                len(
                    known_scores
                )
            ),

            np.ones(
                len(
                    ood_scores
                )
            ),
        ]
    )


    anomaly_scores = np.concatenate(
        [
            1.0
            -
            known_scores,

            1.0
            -
            ood_scores,
        ]
    )


    auroc = float(
        roc_auc_score(
            binary_labels,
            anomaly_scores,
        )
    )


    # =====================================================
    # SAVE OOD SCORES
    # =====================================================


    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "image_path",
                "actual_ood_breed",
                "predicted_class_index",
                "max_calibrated_probability",
            ],
        )

        writer.writeheader()

        writer.writerows(
            ood_rows
        )


    # =====================================================
    # THRESHOLD CONFIG
    # =====================================================


    threshold_config = {

        "project":
            "BreedVision AI",

        "phase":
            7,

        "classifier_version":
            "v2",

        "unknown_policy":
            (
                "max_calibrated_probability"
            ),

        "decision_rule":
            (
                "If maximum calibrated probability "
                "is below threshold, return unknown."
            ),

        "threshold":
            threshold,

        "temperature":
            temperature,

        "selection_metric":
            "known_ood_balanced_accuracy",

        "fit_known_split":
            "validation",

        "fit_ood_split":
            "threshold_tuning",

        "known_validation_acceptance_rate":
            best[
                "known_acceptance_rate"
            ],

        "ood_tuning_rejection_rate":
            best[
                "ood_rejection_rate"
            ],

        "tuning_balanced_accuracy":
            best[
                "balanced_accuracy"
            ],

        "tuning_auroc":
            auroc,

        "test_data_used_for_selection":
            False,
    }


    with OUTPUT_CONFIG.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            threshold_config,
            file,
            indent=4,
        )


    # =====================================================
    # SELECTION REPORT
    # =====================================================


    ranked_results = sorted(
        results,
        key=lambda item:
            item[
                "balanced_accuracy"
            ],
        reverse=True,
    )


    report = {

        "selected":
            best,

        "temperature":
            temperature,

        "known_samples":
            len(
                known_scores
            ),

        "ood_tuning_samples":
            len(
                ood_scores
            ),

        "known_score_mean":
            float(
                np.mean(
                    known_scores
                )
            ),

        "ood_score_mean":
            float(
                np.mean(
                    ood_scores
                )
            ),

        "tuning_auroc":
            auroc,

        "top_candidate_thresholds":
            ranked_results[
                :20
            ],

        "test_data_used":
            False,
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


    # =====================================================
    # UPDATE MAIN PHASE 7 CONFIG
    # =====================================================


    phase7_config = load_json(
        PHASE7_CONFIG
    )


    phase7_config[
        "unknown_handling"
    ][
        "threshold_status"
    ] = (
        "selected"
    )


    phase7_config[
        "unknown_handling"
    ][
        "threshold"
    ] = (
        threshold
    )


    phase7_config[
        "unknown_handling"
    ][
        "threshold_config"
    ] = (
        "configs/phase7_unknown_threshold.json"
    )


    with PHASE7_CONFIG.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            phase7_config,
            file,
            indent=4,
        )


    print()
    print("-" * 94)

    print(
        "Selected threshold:",
        round(
            threshold,
            6,
        )
    )

    print(
        "Known acceptance:",
        round(
            best[
                "known_acceptance_rate"
            ],
            6,
        )
    )

    print(
        "OOD rejection:",
        round(
            best[
                "ood_rejection_rate"
            ],
            6,
        )
    )

    print(
        "Balanced accuracy:",
        round(
            best[
                "balanced_accuracy"
            ],
            6,
        )
    )

    print(
        "Tuning AUROC:",
        round(
            auroc,
            6,
        )
    )


    print()
    print("=" * 94)
    print(
        "PHASE 7 UNKNOWN THRESHOLD: PASS"
    )
    print("=" * 94)


if __name__ == "__main__":
    main()