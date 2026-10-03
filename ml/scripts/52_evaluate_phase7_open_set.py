import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

from PIL import Image
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    roc_auc_score,
)
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
    build_eval_transform,
    create_v2_dataloaders,
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

THRESHOLD_CONFIG = (
    PROJECT_ROOT
    / "configs"
    / "phase7_unknown_threshold.json"
)

OOD_MANIFEST = (
    PROJECT_ROOT
    / "reports"
    / "phase7_ood_manifest.csv"
)

OUTPUT_JSON = (
    PROJECT_ROOT
    / "reports"
    / "phase7_open_set_evaluation.json"
)

OUTPUT_CSV = (
    PROJECT_ROOT
    / "reports"
    / "phase7_open_set_predictions.csv"
)


def load_json(path):

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def expected_calibration_error(
    probabilities,
    labels,
    bins=15,
):

    confidences = np.max(
        probabilities,
        axis=1,
    )

    predictions = np.argmax(
        probabilities,
        axis=1,
    )

    correctness = (
        predictions
        ==
        labels
    ).astype(
        np.float64
    )

    boundaries = np.linspace(
        0,
        1,
        bins + 1,
    )

    ece = 0.0


    for index in range(
        bins
    ):

        lower = boundaries[
            index
        ]

        upper = boundaries[
            index + 1
        ]


        if index == 0:

            mask = (
                confidences
                >=
                lower
            ) & (
                confidences
                <=
                upper
            )

        else:

            mask = (
                confidences
                >
                lower
            ) & (
                confidences
                <=
                upper
            )


        count = int(
            np.sum(
                mask
            )
        )


        if count == 0:
            continue


        accuracy = float(
            np.mean(
                correctness[
                    mask
                ]
            )
        )


        confidence = float(
            np.mean(
                confidences[
                    mask
                ]
            )
        )


        ece += (
            count
            /
            len(
                labels
            )
        ) * abs(
            accuracy
            -
            confidence
        )


    return float(
        ece
    )


def build_model(
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

    index_to_class = {
        index: breed

        for breed, index
        in class_to_index.items()
    }


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
        index_to_class,
    )


def main():

    print("=" * 94)
    print(
        "BREEDVISION AI - PHASE 7 FINAL OPEN-SET EVALUATION"
    )
    print("=" * 94)


    calibration = load_json(
        CALIBRATION_CONFIG
    )

    threshold_config = load_json(
        THRESHOLD_CONFIG
    )


    temperature = float(
        calibration[
            "temperature"
        ]
    )

    threshold = float(
        threshold_config[
            "threshold"
        ]
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
        "Frozen unknown threshold:",
        threshold
    )


    model, class_to_index, index_to_class = (
        build_model(
            device
        )
    )


    num_classes = len(
        class_to_index
    )


    transform = build_eval_transform(
        224
    )


    # =====================================================
    # KNOWN TEST
    # =====================================================


    data = create_v2_dataloaders()

    test_loader = (
        data[
            "test_loader"
        ]
    )


    known_logits = []
    known_labels = []
    known_rows = []


    print()
    print(
        "Running known test inference..."
    )


    with torch.no_grad():

        for batch_index, batch in enumerate(
            test_loader,
            start=1,
        ):

            images = (
                batch[
                    "image"
                ]
                .to(device)
            )

            labels = (
                batch[
                    "label"
                ]
                .to(device)
            )


            logits = model(
                images
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


            top_scores, top_indices = (
                probabilities.topk(
                    k=min(
                        3,
                        num_classes,
                    ),
                    dim=1,
                )
            )


            known_logits.append(
                logits
                .cpu()
                .numpy()
            )

            known_labels.append(
                labels
                .cpu()
                .numpy()
            )


            for sample_index in range(
                images.size(0)
            ):

                actual = int(
                    labels[
                        sample_index
                    ].item()
                )


                scores = (
                    top_scores[
                        sample_index
                    ]
                    .cpu()
                    .tolist()
                )

                indices = (
                    top_indices[
                        sample_index
                    ]
                    .cpu()
                    .tolist()
                )


                max_probability = float(
                    scores[
                        0
                    ]
                )


                rejected = (
                    max_probability
                    <
                    threshold
                )


                known_rows.append(
                    {
                        "dataset_type":
                            "known_test",

                        "image_path":
                            batch[
                                "image_path"
                            ][
                                sample_index
                            ],

                        "actual_label":
                            index_to_class[
                                actual
                            ],

                        "actual_ood_breed":
                            "",

                        "decision":
                            (
                                "unknown"
                                if rejected
                                else
                                "known"
                            ),

                        "top1_breed":
                            index_to_class[
                                indices[
                                    0
                                ]
                            ],

                        "top1_probability":
                            scores[
                                0
                            ],

                        "top2_breed":
                            index_to_class[
                                indices[
                                    1
                                ]
                            ],

                        "top2_probability":
                            scores[
                                1
                            ],

                        "top3_breed":
                            index_to_class[
                                indices[
                                    2
                                ]
                            ],

                        "top3_probability":
                            scores[
                                2
                            ],

                        "correct_top1":
                            indices[
                                0
                            ]
                            ==
                            actual,

                        "correct_top3":
                            actual
                            in
                            indices,
                    }
                )


            if (
                batch_index % 20 == 0
                or
                batch_index
                ==
                len(
                    test_loader
                )
            ):

                print(
                    f"Known test batches "
                    f"{batch_index}/"
                    f"{len(test_loader)}"
                )


    known_logits = np.concatenate(
        known_logits,
        axis=0,
    )


    known_labels = np.concatenate(
        known_labels,
        axis=0,
    )


    raw_logits_tensor = torch.tensor(
        known_logits,
        dtype=torch.float64,
    )


    labels_tensor = torch.tensor(
        known_labels,
        dtype=torch.long,
    )


    raw_nll = float(
        F.cross_entropy(
            raw_logits_tensor,
            labels_tensor,
        ).item()
    )


    calibrated_nll = float(
        F.cross_entropy(
            raw_logits_tensor
            /
            temperature,
            labels_tensor,
        ).item()
    )


    raw_probabilities = torch.softmax(
        raw_logits_tensor,
        dim=1,
    ).numpy()


    calibrated_probabilities = torch.softmax(
        raw_logits_tensor
        /
        temperature,
        dim=1,
    ).numpy()


    raw_ece = (
        expected_calibration_error(
            raw_probabilities,
            known_labels,
        )
    )


    calibrated_ece = (
        expected_calibration_error(
            calibrated_probabilities,
            known_labels,
        )
    )


    known_scores = np.max(
        calibrated_probabilities,
        axis=1,
    )


    known_acceptance_rate = float(
        np.mean(
            known_scores
            >=
            threshold
        )
    )


    known_rejection_rate = (
        1.0
        -
        known_acceptance_rate
    )


    top1_accuracy = float(
        np.mean(
            [
                row[
                    "correct_top1"
                ]

                for row in known_rows
            ]
        )
    )


    top3_accuracy = float(
        np.mean(
            [
                row[
                    "correct_top3"
                ]

                for row in known_rows
            ]
        )
    )


    accepted_known = [
        row

        for row in known_rows

        if (
            row[
                "decision"
            ]
            ==
            "known"
        )
    ]


    selective_accuracy = (

        float(
            np.mean(
                [
                    row[
                        "correct_top1"
                    ]

                    for row
                    in accepted_known
                ]
            )
        )

        if accepted_known

        else None
    )


    # =====================================================
    # FINAL OOD EVALUATION
    # =====================================================


    ood_dataframe = pd.read_csv(
        OOD_MANIFEST
    )


    ood_dataframe = (
        ood_dataframe[
            ood_dataframe[
                "ood_split"
            ]
            ==
            "evaluation"
        ]
        .reset_index(
            drop=True
        )
    )


    if len(
        ood_dataframe
    ) == 0:

        raise RuntimeError(
            "Final OOD evaluation split is empty."
        )


    print()
    print(
        "Running held-out OOD inference..."
    )


    ood_rows = []
    ood_scores = []


    with torch.no_grad():

        for index, row in (
            ood_dataframe.iterrows()
        ):

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


            probabilities = torch.softmax(
                logits
                /
                temperature,
                dim=1,
            )


            top_scores, top_indices = (
                probabilities.topk(
                    k=min(
                        3,
                        num_classes,
                    ),
                    dim=1,
                )
            )


            scores = (
                top_scores[
                    0
                ]
                .cpu()
                .tolist()
            )

            indices = (
                top_indices[
                    0
                ]
                .cpu()
                .tolist()
            )


            max_probability = float(
                scores[
                    0
                ]
            )


            rejected = (
                max_probability
                <
                threshold
            )


            ood_scores.append(
                max_probability
            )


            ood_rows.append(
                {
                    "dataset_type":
                        "ood_evaluation",

                    "image_path":
                        str(
                            image_path
                        ),

                    "actual_label":
                        "unknown",

                    "actual_ood_breed":
                        row[
                            "breed"
                        ],

                    "decision":
                        (
                            "unknown"
                            if rejected
                            else
                            "known"
                        ),

                    "top1_breed":
                        index_to_class[
                            indices[
                                0
                            ]
                        ],

                    "top1_probability":
                        scores[
                            0
                        ],

                    "top2_breed":
                        index_to_class[
                            indices[
                                1
                            ]
                        ],

                    "top2_probability":
                        scores[
                            1
                        ],

                    "top3_breed":
                        index_to_class[
                            indices[
                                2
                            ]
                        ],

                    "top3_probability":
                        scores[
                            2
                        ],

                    "correct_top1":
                        "",

                    "correct_top3":
                        "",
                }
            )


            current = index + 1


            if (
                current % 20 == 0
                or
                current
                ==
                len(
                    ood_dataframe
                )
            ):

                print(
                    f"OOD evaluation "
                    f"{current}/"
                    f"{len(ood_dataframe)}"
                )


    ood_scores = np.array(
        ood_scores,
        dtype=np.float64,
    )


    ood_rejection_rate = float(
        np.mean(
            ood_scores
            <
            threshold
        )
    )


    ood_false_acceptance_rate = (
        1.0
        -
        ood_rejection_rate
    )


    # =====================================================
    # OPEN-SET METRICS
    # =====================================================


    y_true = np.concatenate(
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


    open_set_auroc = float(
        roc_auc_score(
            y_true,
            anomaly_scores,
        )
    )


    open_set_aupr = float(
        average_precision_score(
            y_true,
            anomaly_scores,
        )
    )


    y_pred_unknown = np.concatenate(
        [
            (
                known_scores
                <
                threshold
            ).astype(int),

            (
                ood_scores
                <
                threshold
            ).astype(int),
        ]
    )


    unknown_f1 = float(
        f1_score(
            y_true,
            y_pred_unknown,
            zero_division=0,
        )
    )


    open_set_balanced_accuracy = (
        known_acceptance_rate
        +
        ood_rejection_rate
    ) / 2.0


    # =====================================================
    # SAVE PREDICTIONS
    # =====================================================


    all_rows = (
        known_rows
        +
        ood_rows
    )


    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "dataset_type",
                "image_path",
                "actual_label",
                "actual_ood_breed",
                "decision",
                "top1_breed",
                "top1_probability",
                "top2_breed",
                "top2_probability",
                "top3_breed",
                "top3_probability",
                "correct_top1",
                "correct_top3",
            ],
        )

        writer.writeheader()

        writer.writerows(
            all_rows
        )


    # =====================================================
    # FINAL REPORT
    # =====================================================


    report = {

        "project":
            "BreedVision AI",

        "phase":
            7,

        "classifier_version":
            "v2",

        "evaluation_protocol": {
            "known_split":
                "test",

            "ood_split":
                "evaluation",

            "threshold_frozen_before_test":
                True,

            "test_used_for_tuning":
                False,
        },

        "temperature":
            temperature,

        "unknown_threshold":
            threshold,

        "known_test": {
            "samples":
                len(
                    known_scores
                ),

            "top1_accuracy":
                top1_accuracy,

            "top3_accuracy":
                top3_accuracy,

            "known_acceptance_rate":
                known_acceptance_rate,

            "known_rejection_rate":
                known_rejection_rate,

            "selective_top1_accuracy":
                selective_accuracy,

            "raw_nll":
                raw_nll,

            "calibrated_nll":
                calibrated_nll,

            "raw_ece":
                raw_ece,

            "calibrated_ece":
                calibrated_ece,
        },

        "ood_evaluation": {
            "samples":
                len(
                    ood_scores
                ),

            "ood_rejection_rate":
                ood_rejection_rate,

            "ood_false_acceptance_rate":
                ood_false_acceptance_rate,

            "mean_max_calibrated_probability":
                float(
                    np.mean(
                        ood_scores
                    )
                ),
        },

        "open_set": {
            "balanced_accuracy":
                open_set_balanced_accuracy,

            "auroc":
                open_set_auroc,

            "aupr_ood":
                open_set_aupr,

            "unknown_f1":
                unknown_f1,
        },

        "probability_note":
            (
                "Calibrated probabilities improve "
                "probability calibration on known classes, "
                "but they are not guarantees of correctness."
            ),
    }


    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
        )


    print()
    print("-" * 94)

    print(
        "Known Top-1 accuracy:",
        round(
            top1_accuracy,
            6,
        )
    )

    print(
        "Known Top-3 accuracy:",
        round(
            top3_accuracy,
            6,
        )
    )

    print(
        "Known acceptance:",
        round(
            known_acceptance_rate,
            6,
        )
    )

    print(
        "OOD rejection:",
        round(
            ood_rejection_rate,
            6,
        )
    )

    print(
        "Open-set balanced accuracy:",
        round(
            open_set_balanced_accuracy,
            6,
        )
    )

    print(
        "Open-set AUROC:",
        round(
            open_set_auroc,
            6,
        )
    )

    print(
        "Unknown F1:",
        round(
            unknown_f1,
            6,
        )
    )

    print()
    print(
        "Test NLL:",
        round(
            raw_nll,
            6,
        ),
        "->",
        round(
            calibrated_nll,
            6,
        )
    )

    print(
        "Test ECE:",
        round(
            raw_ece,
            6,
        ),
        "->",
        round(
            calibrated_ece,
            6,
        )
    )


    print()
    print("=" * 94)
    print(
        "PHASE 7 OPEN-SET EVALUATION: PASS"
    )
    print("=" * 94)


if __name__ == "__main__":
    main()