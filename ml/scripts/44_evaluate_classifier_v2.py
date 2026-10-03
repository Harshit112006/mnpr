import csv
import json
import shutil
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from torchvision import models
import torch.nn as nn


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from training.dataset_v2 import create_v2_dataloaders


CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "checkpoints"
    / "classifier_v2_best.pth"
)

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)

CONFIGS_DIR = (
    PROJECT_ROOT
    / "configs"
)

WEIGHTS_DIR = (
    PROJECT_ROOT
    / "weights"
)


def main():

    print("=" * 88)
    print(
        "BREEDVISION AI - CLASSIFIER V2 FINAL TEST"
    )
    print("=" * 88)

    device = (
        torch.device("cuda")
        if torch.cuda.is_available()
        else torch.device("cpu")
    )

    data = create_v2_dataloaders()

    test_loader = (
        data[
            "test_loader"
        ]
    )

    checkpoint = torch.load(
        CHECKPOINT_PATH,
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

    class_names = [
        index_to_class[index]
        for index in range(
            len(
                index_to_class
            )
        )
    ]

    model = models.resnet18(
        weights=None
    )

    model.fc = nn.Linear(
        model.fc.in_features,
        len(
            class_names
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

    targets_all = []
    predictions_all = []
    prediction_rows = []

    print()
    print(
        "Running held-out test inference..."
    )

    with torch.no_grad():

        for batch in test_loader:

            images = (
                batch[
                    "image"
                ]
                .to(device)
            )

            targets = (
                batch[
                    "label"
                ]
            )

            logits = model(
                images
            )

            probabilities = torch.softmax(
                logits,
                dim=1,
            )

            scores, predictions = (
                probabilities.max(
                    dim=1
                )
            )

            predictions = (
                predictions.cpu()
            )

            scores = (
                scores.cpu()
            )

            targets_all.extend(
                targets.tolist()
            )

            predictions_all.extend(
                predictions.tolist()
            )

            for (
                image_path,
                actual,
                predicted,
                score,
                species,
            ) in zip(
                batch["image_path"],
                targets.tolist(),
                predictions.tolist(),
                scores.tolist(),
                batch["species"],
            ):

                prediction_rows.append(
                    {
                        "image_path":
                            image_path,

                        "actual_breed":
                            index_to_class[
                                actual
                            ],

                        "predicted_breed":
                            index_to_class[
                                predicted
                            ],

                        "species":
                            species,

                        "softmax_score":
                            score,

                        "correct":
                            actual
                            ==
                            predicted,
                    }
                )

    labels = list(
        range(
            len(
                class_names
            )
        )
    )

    accuracy = accuracy_score(
        targets_all,
        predictions_all,
    )

    macro_precision = precision_score(
        targets_all,
        predictions_all,
        labels=labels,
        average="macro",
        zero_division=0,
    )

    macro_recall = recall_score(
        targets_all,
        predictions_all,
        labels=labels,
        average="macro",
        zero_division=0,
    )

    macro_f1 = f1_score(
        targets_all,
        predictions_all,
        labels=labels,
        average="macro",
        zero_division=0,
    )

    weighted_f1 = f1_score(
        targets_all,
        predictions_all,
        labels=labels,
        average="weighted",
        zero_division=0,
    )

    report = classification_report(
        targets_all,
        predictions_all,
        labels=labels,
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )

    matrix = confusion_matrix(
        targets_all,
        predictions_all,
        labels=labels,
    )

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Predictions

    predictions_csv = (
        REPORTS_DIR
        / "classifier_v2_test_predictions.csv"
    )

    with predictions_csv.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "image_path",
                "actual_breed",
                "predicted_breed",
                "species",
                "softmax_score",
                "correct",
            ],
        )

        writer.writeheader()
        writer.writerows(
            prediction_rows
        )

    # Per class

    per_class_csv = (
        REPORTS_DIR
        / "classifier_v2_per_class_metrics.csv"
    )

    with per_class_csv.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "breed",
                "precision",
                "recall",
                "f1",
                "support",
            ]
        )

        for breed in class_names:

            metrics = report[
                breed
            ]

            writer.writerow(
                [
                    breed,
                    metrics[
                        "precision"
                    ],
                    metrics[
                        "recall"
                    ],
                    metrics[
                        "f1-score"
                    ],
                    int(
                        metrics[
                            "support"
                        ]
                    ),
                ]
            )

    # Matrix CSV

    matrix_csv = (
        REPORTS_DIR
        / "classifier_v2_confusion_matrix.csv"
    )

    with matrix_csv.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "Actual / Predicted",
                *class_names,
            ]
        )

        for index, row in enumerate(
            matrix
        ):

            writer.writerow(
                [
                    class_names[
                        index
                    ],
                    *row.tolist(),
                ]
            )

    # Matrix PNG

    matrix_png = (
        REPORTS_DIR
        / "classifier_v2_confusion_matrix.png"
    )

    plt.figure(
        figsize=(11, 10)
    )

    plt.imshow(
        matrix,
        interpolation="nearest",
    )

    plt.title(
        "BreedVision AI - Classifier V2 Confusion Matrix"
    )

    plt.colorbar()

    ticks = np.arange(
        len(
            class_names
        )
    )

    plt.xticks(
        ticks,
        class_names,
        rotation=45,
        ha="right",
    )

    plt.yticks(
        ticks,
        class_names,
    )

    for i in range(
        matrix.shape[0]
    ):
        for j in range(
            matrix.shape[1]
        ):
            plt.text(
                j,
                i,
                str(
                    matrix[
                        i,
                        j
                    ]
                ),
                ha="center",
                va="center",
            )

    plt.xlabel(
        "Predicted Breed"
    )

    plt.ylabel(
        "Actual Breed"
    )

    plt.tight_layout()

    plt.savefig(
        matrix_png,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    result = {
        "classifier_version":
            "v2",

        "architecture":
            "resnet18",

        "checkpoint_validation_macro_f1":
            checkpoint[
                "validation_macro_f1"
            ],

        "test_images":
            len(
                targets_all
            ),

        "accuracy":
            accuracy,

        "macro_precision":
            macro_precision,

        "macro_recall":
            macro_recall,

        "macro_f1":
            macro_f1,

        "weighted_f1":
            weighted_f1,

        "classification_report":
            report,

        "class_to_index":
            class_to_index,
    }

    metrics_json = (
        REPORTS_DIR
        / "classifier_v2_test_metrics.json"
    )

    with metrics_json.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
        )

    # Production candidate weight

    WEIGHTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    final_weight = (
        WEIGHTS_DIR
        / "breed_classifier_v2.pth"
    )

    shutil.copy2(
        CHECKPOINT_PATH,
        final_weight,
    )

    classifier_config = {
        "model_version":
            "breed-classifier-v2",

        "architecture":
            "resnet18",

        "weights":
            "weights/breed_classifier_v2.pth",

        "num_classes":
            len(
                class_names
            ),

        "class_to_index":
            class_to_index,

        "image_size":
            224,

        "normalization": {
            "mean": [
                0.485,
                0.456,
                0.406
            ],

            "std": [
                0.229,
                0.224,
                0.225
            ]
        },

        "validation_macro_f1":
            checkpoint[
                "validation_macro_f1"
            ],

        "test_macro_f1":
            macro_f1,

        "test_accuracy":
            accuracy,

        "softmax_note":
            (
                "Softmax scores are not yet calibrated "
                "confidence values. Calibration is Phase 7."
            ),
    }

    with (
        CONFIGS_DIR
        / "breed_classifier_v2.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            classifier_config,
            file,
            indent=4,
        )

    print()
    print(
        "Test Accuracy :",
        f"{accuracy:.4f}"
    )

    print(
        "Test Macro F1 :",
        f"{macro_f1:.4f}"
    )

    print()
    print("=" * 88)
    print(
        "CLASSIFIER V2 FINAL TEST: COMPLETE"
    )
    print("=" * 88)


if __name__ == "__main__":
    main()