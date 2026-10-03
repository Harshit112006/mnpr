import argparse
import csv
import json
import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torchvision import models
from tqdm import tqdm


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from training.dataset_v2 import create_v2_dataloaders


CONFIG_PATH = (
    PROJECT_ROOT
    / "configs"
    / "training_config_v2.json"
)

CHECKPOINT_DIR = (
    PROJECT_ROOT
    / "checkpoints"
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


def calculate_metrics(
    targets,
    predictions,
):

    return {
        "accuracy":
            accuracy_score(
                targets,
                predictions,
            ),

        "macro_precision":
            precision_score(
                targets,
                predictions,
                average="macro",
                zero_division=0,
            ),

        "macro_recall":
            recall_score(
                targets,
                predictions,
                average="macro",
                zero_division=0,
            ),

        "macro_f1":
            f1_score(
                targets,
                predictions,
                average="macro",
                zero_division=0,
            ),

        "weighted_f1":
            f1_score(
                targets,
                predictions,
                average="weighted",
                zero_division=0,
            ),
    }


def create_model(
    num_classes,
):

    model = models.resnet18(
        weights=models.ResNet18_Weights.DEFAULT
    )

    in_features = (
        model.fc.in_features
    )

    model.fc = nn.Linear(
        in_features,
        num_classes,
    )

    return model


def freeze_stage1(
    model,
):

    for parameter in model.parameters():
        parameter.requires_grad = False

    for parameter in model.fc.parameters():
        parameter.requires_grad = True


def configure_stage2(
    model,
):

    for parameter in model.parameters():
        parameter.requires_grad = False

    for parameter in model.layer4.parameters():
        parameter.requires_grad = True

    for parameter in model.fc.parameters():
        parameter.requires_grad = True


def set_training_mode(
    model,
):

    model.train()

    for module in model.modules():

        if isinstance(
            module,
            nn.modules.batchnorm._BatchNorm,
        ):

            parameters = list(
                module.parameters(
                    recurse=False
                )
            )

            if (
                parameters
                and
                not any(
                    parameter.requires_grad
                    for parameter
                    in parameters
                )
            ):
                module.eval()


def run_epoch(
    model,
    loader,
    criterion,
    optimizer,
    device,
    training,
    max_batches=None,
):

    if training:
        set_training_mode(model)
    else:
        model.eval()

    total_loss = 0.0
    total_samples = 0

    targets_all = []
    predictions_all = []

    progress = tqdm(
        loader,
        desc=(
            "Training"
            if training
            else
            "Validation"
        ),
        leave=False,
    )

    for batch_index, batch in enumerate(
        progress
    ):

        if (
            max_batches is not None
            and
            batch_index >= max_batches
        ):
            break

        images = (
            batch["image"]
            .to(device)
        )

        targets = (
            batch["label"]
            .to(device)
        )

        if training:
            optimizer.zero_grad(
                set_to_none=True
            )

        with torch.set_grad_enabled(
            training
        ):

            logits = model(
                images
            )

            loss = criterion(
                logits,
                targets,
            )

            if training:
                loss.backward()
                optimizer.step()

        predictions = (
            logits
            .argmax(dim=1)
        )

        batch_size = (
            images.size(0)
        )

        total_loss += (
            loss.item()
            *
            batch_size
        )

        total_samples += (
            batch_size
        )

        targets_all.extend(
            targets
            .detach()
            .cpu()
            .tolist()
        )

        predictions_all.extend(
            predictions
            .detach()
            .cpu()
            .tolist()
        )

    metrics = calculate_metrics(
        targets_all,
        predictions_all,
    )

    metrics["loss"] = (
        total_loss
        /
        max(total_samples, 1)
    )

    return metrics


def save_checkpoint(
    path,
    model,
    class_to_index,
    stage,
    epoch,
    validation_macro_f1,
):

    torch.save(
        {
            "architecture":
                "resnet18",

            "classifier_version":
                "v2",

            "model_state_dict":
                model.state_dict(),

            "class_to_index":
                class_to_index,

            "stage":
                stage,

            "epoch":
                epoch,

            "validation_macro_f1":
                validation_macro_f1,
        },
        path,
    )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--stage1-epochs",
        type=int,
        default=3,
    )

    parser.add_argument(
        "--stage2-epochs",
        type=int,
        default=1,
    )

    parser.add_argument(
        "--run-name",
        default="classifier_v2",
    )

    parser.add_argument(
        "--max-train-batches",
        type=int,
        default=None,
    )

    parser.add_argument(
        "--max-val-batches",
        type=int,
        default=None,
    )

    args = parser.parse_args()

    config = load_json(
        CONFIG_PATH
    )

    torch.manual_seed(
        int(
            config[
                "training"
            ][
                "random_seed"
            ]
        )
    )

    device = (
        torch.device("cuda")
        if torch.cuda.is_available()
        else torch.device("cpu")
    )

    print("=" * 88)
    print(
        "BREEDVISION AI - CLASSIFIER V2 TRAINING"
    )
    print("=" * 88)

    print()
    print("Device:", device)

    data = create_v2_dataloaders()

    train_loader = (
        data[
            "train_loader"
        ]
    )

    validation_loader = (
        data[
            "validation_loader"
        ]
    )

    class_weights = (
        data[
            "class_weights"
        ].to(device)
    )

    class_to_index = (
        data[
            "class_to_index"
        ]
    )

    num_classes = (
        data[
            "num_classes"
        ]
    )

    print(
        "Train:",
        len(
            train_loader.dataset
        )
    )

    print(
        "Validation:",
        len(
            validation_loader.dataset
        )
    )

    print(
        "Classes:",
        num_classes
    )

    model = create_model(
        num_classes
    )

    model = model.to(
        device
    )

    criterion = nn.CrossEntropyLoss(
        weight=class_weights,
        label_smoothing=float(
            config[
                "training"
            ][
                "label_smoothing"
            ]
        ),
    )

    CHECKPOINT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    checkpoint_path = (
        CHECKPOINT_DIR
        /
        f"{args.run_name}_best.pth"
    )

    history_csv = (
        REPORTS_DIR
        /
        f"{args.run_name}_history.csv"
    )

    history_json = (
        REPORTS_DIR
        /
        f"{args.run_name}_history.json"
    )

    summary_json = (
        REPORTS_DIR
        /
        f"{args.run_name}_summary.json"
    )

    history = []

    best_f1 = -1.0
    best_stage = None
    best_epoch = None

    total_start = time.time()

    # =====================================================
    # STAGE 1
    # =====================================================

    if args.stage1_epochs > 0:

        freeze_stage1(
            model
        )

        optimizer = AdamW(
            [
                parameter
                for parameter
                in model.parameters()
                if parameter.requires_grad
            ],
            lr=0.0003,
            weight_decay=0.0001,
        )

        scheduler = CosineAnnealingLR(
            optimizer,
            T_max=max(
                args.stage1_epochs,
                1,
            ),
        )

        for epoch in range(
            1,
            args.stage1_epochs + 1,
        ):

            start = time.time()

            print()
            print(
                f"Stage 1 Epoch "
                f"{epoch}/{args.stage1_epochs}"
            )

            train_metrics = run_epoch(
                model,
                train_loader,
                criterion,
                optimizer,
                device,
                True,
                args.max_train_batches,
            )

            val_metrics = run_epoch(
                model,
                validation_loader,
                criterion,
                optimizer,
                device,
                False,
                args.max_val_batches,
            )

            scheduler.step()

            elapsed = (
                time.time()
                -
                start
            )

            print(
                "Train Macro F1:",
                f"{train_metrics['macro_f1']:.4f}"
            )

            print(
                "Val Macro F1  :",
                f"{val_metrics['macro_f1']:.4f}"
            )

            print(
                "Time          :",
                f"{elapsed:.1f}s"
            )

            history.append(
                {
                    "stage": 1,
                    "epoch": epoch,
                    "train_loss":
                        train_metrics["loss"],
                    "train_accuracy":
                        train_metrics["accuracy"],
                    "train_macro_f1":
                        train_metrics["macro_f1"],
                    "validation_loss":
                        val_metrics["loss"],
                    "validation_accuracy":
                        val_metrics["accuracy"],
                    "validation_macro_f1":
                        val_metrics["macro_f1"],
                    "seconds":
                        elapsed,
                }
            )

            if (
                val_metrics[
                    "macro_f1"
                ]
                >
                best_f1
            ):

                best_f1 = (
                    val_metrics[
                        "macro_f1"
                    ]
                )

                best_stage = 1
                best_epoch = epoch

                save_checkpoint(
                    checkpoint_path,
                    model,
                    class_to_index,
                    1,
                    epoch,
                    best_f1,
                )

                print(
                    "★ Best checkpoint saved"
                )

    # =====================================================
    # STAGE 2
    # =====================================================

    if args.stage2_epochs > 0:

        configure_stage2(
            model
        )

        optimizer = AdamW(
            [
                parameter
                for parameter
                in model.parameters()
                if parameter.requires_grad
            ],
            lr=0.00005,
            weight_decay=0.0001,
        )

        scheduler = CosineAnnealingLR(
            optimizer,
            T_max=max(
                args.stage2_epochs,
                1,
            ),
        )

        for epoch in range(
            1,
            args.stage2_epochs + 1,
        ):

            start = time.time()

            print()
            print(
                f"Stage 2 Epoch "
                f"{epoch}/{args.stage2_epochs}"
            )

            train_metrics = run_epoch(
                model,
                train_loader,
                criterion,
                optimizer,
                device,
                True,
                args.max_train_batches,
            )

            val_metrics = run_epoch(
                model,
                validation_loader,
                criterion,
                optimizer,
                device,
                False,
                args.max_val_batches,
            )

            scheduler.step()

            elapsed = (
                time.time()
                -
                start
            )

            print(
                "Train Macro F1:",
                f"{train_metrics['macro_f1']:.4f}"
            )

            print(
                "Val Macro F1  :",
                f"{val_metrics['macro_f1']:.4f}"
            )

            print(
                "Time          :",
                f"{elapsed:.1f}s"
            )

            history.append(
                {
                    "stage": 2,
                    "epoch": epoch,
                    "train_loss":
                        train_metrics["loss"],
                    "train_accuracy":
                        train_metrics["accuracy"],
                    "train_macro_f1":
                        train_metrics["macro_f1"],
                    "validation_loss":
                        val_metrics["loss"],
                    "validation_accuracy":
                        val_metrics["accuracy"],
                    "validation_macro_f1":
                        val_metrics["macro_f1"],
                    "seconds":
                        elapsed,
                }
            )

            if (
                val_metrics[
                    "macro_f1"
                ]
                >
                best_f1
            ):

                best_f1 = (
                    val_metrics[
                        "macro_f1"
                    ]
                )

                best_stage = 2
                best_epoch = epoch

                save_checkpoint(
                    checkpoint_path,
                    model,
                    class_to_index,
                    2,
                    epoch,
                    best_f1,
                )

                print(
                    "★ Best checkpoint saved"
                )

    fieldnames = [
        "stage",
        "epoch",
        "train_loss",
        "train_accuracy",
        "train_macro_f1",
        "validation_loss",
        "validation_accuracy",
        "validation_macro_f1",
        "seconds",
    ]

    with history_csv.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(history)

    with history_json.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            history,
            file,
            indent=4,
        )

    summary = {
        "classifier_version":
            "v2",

        "architecture":
            "resnet18",

        "num_classes":
            num_classes,

        "stage1_epochs":
            args.stage1_epochs,

        "stage2_epochs":
            args.stage2_epochs,

        "best_stage":
            best_stage,

        "best_epoch":
            best_epoch,

        "best_validation_macro_f1":
            best_f1,

        "checkpoint":
            str(
                checkpoint_path
            ),

        "total_seconds":
            time.time()
            -
            total_start,
    }

    with summary_json.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
        )

    print()
    print("=" * 88)
    print(
        "CLASSIFIER V2 TRAINING: COMPLETE"
    )
    print("=" * 88)

    print(
        "Best validation Macro F1:",
        round(
            best_f1,
            4,
        )
    )


if __name__ == "__main__":
    main()