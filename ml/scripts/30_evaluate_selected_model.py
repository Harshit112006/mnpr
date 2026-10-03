import csv
import json
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


from training.dataset import create_dataloaders
from training.model_factory import create_model
from training.engine import get_device


SELECTED_CONFIG = (
    PROJECT_ROOT
    / "configs"
    / "selected_model.json"
)

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)


def load_json(path):

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def main():

    print("=" * 84)
    print(
        "BREEDVISION AI - SELECTED MODEL FINAL TEST"
    )
    print("=" * 84)


    selected = load_json(
        SELECTED_CONFIG
    )


    checkpoint_path = Path(
        selected[
            "checkpoint"
        ]
    )


    if not checkpoint_path.exists():

        raise FileNotFoundError(
            f"Checkpoint missing:\n"
            f"{checkpoint_path}"
        )


    device = get_device()


    print()
    print(
        "Selected run :",
        selected[
            "selected_run"
        ]
    )

    print(
        "Architecture :",
        selected[
            "architecture"
        ]
    )

    print(
        "Device       :",
        device
    )


    data = create_dataloaders()


    test_loader = (
        data[
            "test_loader"
        ]
    )


    checkpoint = torch.load(
        checkpoint_path,
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
                class_to_index
            )
        )
    ]


    model = create_model(
        model_name=
            selected[
                "architecture"
            ],

        num_classes=
            len(
                class_to_index
            ),

        pretrained=False,

        freeze_backbone=False,
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


    all_targets = []
    all_predictions = []

    prediction_rows = []


    print()
    print(
        "Running test inference..."
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


            predictions = (
                logits
                .argmax(
                    dim=1
                )
                .cpu()
            )


            target_list = (
                targets.tolist()
            )

            prediction_list = (
                predictions.tolist()
            )


            all_targets.extend(
                target_list
            )

            all_predictions.extend(
                prediction_list
            )


            for (
                image_path,
                actual,
                predicted,
            ) in zip(
                batch[
                    "image_path"
                ],
                target_list,
                prediction_list,
            ):

                prediction_rows.append(
                    {
                        "image_path":
                            image_path,

                        "actual_index":
                            actual,

                        "actual_breed":
                            index_to_class[
                                actual
                            ],

                        "predicted_index":
                            predicted,

                        "predicted_breed":
                            index_to_class[
                                predicted
                            ],

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
        all_targets,
        all_predictions,
    )


    macro_precision = precision_score(
        all_targets,
        all_predictions,
        labels=labels,
        average="macro",
        zero_division=0,
    )


    macro_recall = recall_score(
        all_targets,
        all_predictions,
        labels=labels,
        average="macro",
        zero_division=0,
    )


    macro_f1 = f1_score(
        all_targets,
        all_predictions,
        labels=labels,
        average="macro",
        zero_division=0,
    )


    weighted_f1 = f1_score(
        all_targets,
        all_predictions,
        labels=labels,
        average="weighted",
        zero_division=0,
    )


    report = classification_report(
        all_targets,
        all_predictions,
        labels=labels,
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )


    matrix = confusion_matrix(
        all_targets,
        all_predictions,
        labels=labels,
    )


    # =====================================================
    # SAVE PREDICTIONS
    # =====================================================

    predictions_path = (
        REPORTS_DIR
        / "selected_model_test_predictions.csv"
    )


    with predictions_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "image_path",
                "actual_index",
                "actual_breed",
                "predicted_index",
                "predicted_breed",
                "correct",
            ],
        )

        writer.writeheader()

        writer.writerows(
            prediction_rows
        )


    # =====================================================
    # PER-CLASS CSV
    # =====================================================

    class_metrics_path = (
        REPORTS_DIR
        / "selected_model_per_class_metrics.csv"
    )


    with class_metrics_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(
            file
        )

        writer.writerow(
            [
                "breed",
                "precision",
                "recall",
                "f1_score",
                "support",
            ]
        )


        for breed in class_names:

            metrics = (
                report[
                    breed
                ]
            )


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


    # =====================================================
    # CONFUSION MATRIX CSV
    # =====================================================

    matrix_csv = (
        REPORTS_DIR
        / "selected_model_confusion_matrix.csv"
    )


    with matrix_csv.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(
            file
        )

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


    # =====================================================
    # CONFUSION MATRIX IMAGE
    # =====================================================

    image_path = (
        REPORTS_DIR
        / "selected_model_confusion_matrix.png"
    )


    plt.figure(
        figsize=(
            9,
            8
        )
    )


    plt.imshow(
        matrix,
        interpolation="nearest",
    )


    plt.title(
        "BreedVision AI - Selected Classifier Confusion Matrix"
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
                horizontalalignment="center",
                verticalalignment="center",
            )


    plt.xlabel(
        "Predicted Breed"
    )

    plt.ylabel(
        "Actual Breed"
    )


    plt.tight_layout()


    plt.savefig(
        image_path,
        dpi=200,
        bbox_inches="tight",
    )


    plt.close()


    result = {

        "model_version":
            "breed-classifier-v1",

        "selected_run":
            selected[
                "selected_run"
            ],

        "architecture":
            selected[
                "architecture"
            ],

        "selection_validation_macro_f1":
            selected[
                "validation_macro_f1"
            ],

        "test_images":
            len(
                all_targets
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


    result_path = (
        REPORTS_DIR
        / "selected_model_test_metrics.json"
    )


    with result_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
        )


    print()
    print("-" * 84)

    print(
        "Test Accuracy   :",
        f"{accuracy:.4f}"
    )

    print(
        "Macro Precision :",
        f"{macro_precision:.4f}"
    )

    print(
        "Macro Recall    :",
        f"{macro_recall:.4f}"
    )

    print(
        "Macro F1        :",
        f"{macro_f1:.4f}"
    )

    print(
        "Weighted F1     :",
        f"{weighted_f1:.4f}"
    )


    print()
    print("=" * 84)
    print(
        "FINAL TEST STATUS: COMPLETE"
    )
    print("=" * 84)


if __name__ == "__main__":

    main()