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


# =========================================================
# PATH SETUP
# =========================================================

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


CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "checkpoints"
    / "resnet18_baseline_best.pth"
)

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 84)
    print("BREEDVISION AI - RESNET18 TEST EVALUATION")
    print("=" * 84)


    if not CHECKPOINT_PATH.exists():
        raise FileNotFoundError(
            f"Checkpoint not found:\n{CHECKPOINT_PATH}"
        )


    # =====================================================
    # DEVICE
    # =====================================================

    device = get_device()

    print()
    print("Device      :", device)


    # =====================================================
    # DATA
    # =====================================================

    data = create_dataloaders()

    test_loader = (
        data[
            "test_loader"
        ]
    )

    print(
        "Test images :",
        len(
            test_loader.dataset
        )
    )


    # =====================================================
    # CHECKPOINT
    # =====================================================

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


    # =====================================================
    # MODEL
    # =====================================================

    model = create_model(
        model_name="resnet18",
        num_classes=len(
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


    # =====================================================
    # TEST INFERENCE
    # =====================================================

    all_targets = []
    all_predictions = []


    print()
    print("Running test inference...")


    with torch.no_grad():

        for batch in test_loader:

            images = (
                batch[
                    "image"
                ]
                .to(
                    device
                )
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


            all_targets.extend(
                targets.tolist()
            )

            all_predictions.extend(
                predictions.tolist()
            )


    # =====================================================
    # METRICS
    # =====================================================

    accuracy = accuracy_score(
        all_targets,
        all_predictions,
    )


    macro_precision = precision_score(
        all_targets,
        all_predictions,
        average="macro",
        zero_division=0,
    )


    macro_recall = recall_score(
        all_targets,
        all_predictions,
        average="macro",
        zero_division=0,
    )


    macro_f1 = f1_score(
        all_targets,
        all_predictions,
        average="macro",
        zero_division=0,
    )


    weighted_f1 = f1_score(
        all_targets,
        all_predictions,
        average="weighted",
        zero_division=0,
    )


    # =====================================================
    # CLASSIFICATION REPORT
    # =====================================================

    report = classification_report(
        all_targets,
        all_predictions,
        labels=list(
            range(
                len(
                    class_names
                )
            )
        ),
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )


    # =====================================================
    # CONFUSION MATRIX
    # =====================================================

    matrix = confusion_matrix(
        all_targets,
        all_predictions,
        labels=list(
            range(
                len(
                    class_names
                )
            )
        ),
    )


    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    matrix_csv = (
        REPORTS_DIR
        / "resnet18_confusion_matrix.csv"
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

    figure_path = (
        REPORTS_DIR
        / "resnet18_confusion_matrix.png"
    )


    plt.figure(
        figsize=(
            9,
            8,
        )
    )


    plt.imshow(
        matrix,
        interpolation="nearest",
    )


    plt.title(
        "BreedVision AI - ResNet18 Confusion Matrix"
    )


    plt.colorbar()


    tick_marks = np.arange(
        len(
            class_names
        )
    )


    plt.xticks(
        tick_marks,
        class_names,
        rotation=45,
        ha="right",
    )


    plt.yticks(
        tick_marks,
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


    plt.ylabel(
        "Actual Breed"
    )

    plt.xlabel(
        "Predicted Breed"
    )


    plt.tight_layout()


    plt.savefig(
        figure_path,
        dpi=200,
        bbox_inches="tight",
    )


    plt.close()


    # =====================================================
    # JSON RESULT
    # =====================================================

    result = {

        "model":
            "resnet18",

        "checkpoint_epoch":
            checkpoint[
                "epoch"
            ],

        "validation_macro_f1":
            checkpoint[
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


    output_json = (
        REPORTS_DIR
        / "resnet18_test_metrics.json"
    )


    with output_json.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
        )


    # =====================================================
    # DISPLAY
    # =====================================================

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
    print("-" * 84)
    print("PER-CLASS PERFORMANCE")
    print("-" * 84)


    for breed in class_names:

        metrics = (
            report[
                breed
            ]
        )

        print()

        print(
            breed
        )

        print(
            " Precision:",
            f"{metrics['precision']:.4f}"
        )

        print(
            " Recall   :",
            f"{metrics['recall']:.4f}"
        )

        print(
            " F1       :",
            f"{metrics['f1-score']:.4f}"
        )

        print(
            " Support  :",
            int(
                metrics[
                    "support"
                ]
            )
        )


    print()
    print("=" * 84)
    print("RESNET18 TEST EVALUATION: COMPLETE")
    print("=" * 84)


    print()
    print("Metrics:")
    print(output_json)

    print()
    print("Confusion matrix CSV:")
    print(matrix_csv)

    print()
    print("Confusion matrix image:")
    print(figure_path)


if __name__ == "__main__":

    main()