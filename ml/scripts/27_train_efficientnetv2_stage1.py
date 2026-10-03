import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import torch
from tqdm import tqdm


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
from training.engine import (
    set_seed,
    get_device,
    create_loss_function,
    create_optimizer,
    create_scheduler,
    calculate_metrics,
    save_checkpoint,
)


# =========================================================
# PATHS
# =========================================================

CONFIG_PATH = (
    PROJECT_ROOT
    / "configs"
    / "training_config.json"
)

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)

CHECKPOINTS_DIR = (
    PROJECT_ROOT
    / "checkpoints"
)


# =========================================================
# HELPERS
# =========================================================


def load_json(path):

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def count_parameters(model):

    total = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    trainable = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    return total, trainable


def run_epoch(
    model,
    dataloader,
    criterion,
    optimizer,
    device,
    training=True,
    max_batches=None,
):

    if training:
        model.train()
    else:
        model.eval()


    running_loss = 0.0
    processed_samples = 0

    all_targets = []
    all_predictions = []


    description = (
        "Training"
        if training
        else "Validation"
    )


    progress = tqdm(
        dataloader,
        desc=description,
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
                targets
            )


            if training:

                loss.backward()

                optimizer.step()


        batch_size = (
            images.size(0)
        )


        running_loss += (
            loss.item()
            *
            batch_size
        )

        processed_samples += (
            batch_size
        )


        predictions = (
            logits
            .argmax(dim=1)
        )


        all_targets.extend(
            targets
            .detach()
            .cpu()
            .tolist()
        )

        all_predictions.extend(
            predictions
            .detach()
            .cpu()
            .tolist()
        )


        progress.set_postfix(
            loss=f"{loss.item():.4f}"
        )


    metrics = calculate_metrics(
        all_targets,
        all_predictions,
    )


    metrics["loss"] = (
        running_loss
        /
        max(
            processed_samples,
            1
        )
    )


    metrics["processed_samples"] = (
        processed_samples
    )


    return metrics


# =========================================================
# MAIN
# =========================================================


def main():

    parser = argparse.ArgumentParser()


    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
    )


    parser.add_argument(
        "--run-name",
        type=str,
        default="efficientnetv2s_stage1",
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


    print("=" * 84)
    print(
        "BREEDVISION AI - EFFICIENTNETV2-S STAGE 1"
    )
    print("=" * 84)


    config = load_json(
        CONFIG_PATH
    )


    seed = int(
        config[
            "training"
        ][
            "random_seed"
        ]
    )


    set_seed(
        seed
    )


    # =====================================================
    # CPU SETTINGS
    # =====================================================

    cpu_count = (
        os.cpu_count()
        or 1
    )


    torch.set_num_threads(
        max(
            1,
            cpu_count - 1
        )
    )


    # =====================================================
    # DEVICE
    # =====================================================

    device = get_device()


    print()
    print(
        "Device               :",
        device
    )

    print(
        "CPU threads          :",
        torch.get_num_threads()
    )

    print(
        "Epochs               :",
        args.epochs
    )


    # =====================================================
    # DATA
    # =====================================================

    print()
    print(
        "Loading dataset..."
    )


    data = create_dataloaders()


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
        ]
    )


    class_to_index = (
        data[
            "class_to_index"
        ]
    )


    print(
        "Train images         :",
        len(
            train_loader.dataset
        )
    )

    print(
        "Validation images    :",
        len(
            validation_loader.dataset
        )
    )

    print(
        "Classes              :",
        len(
            class_to_index
        )
    )


    # =====================================================
    # MODEL
    # =====================================================

    print()
    print(
        "Creating pretrained EfficientNetV2-S..."
    )


    print(
        "Stage 1 policy       : Frozen backbone"
    )


    model = create_model(
        model_name=
            "tf_efficientnetv2_s.in21k_ft_in1k",

        num_classes=
            len(
                class_to_index
            ),

        pretrained=
            True,

        freeze_backbone=
            True,
    )


    model = model.to(
        device
    )


    total_parameters, trainable_parameters = (
        count_parameters(
            model
        )
    )


    trainable_percentage = (
        trainable_parameters
        /
        total_parameters
        *
        100
    )


    print()
    print(
        "Total parameters     :",
        total_parameters
    )

    print(
        "Trainable parameters :",
        trainable_parameters
    )

    print(
        "Trainable %          :",
        round(
            trainable_percentage,
            4
        )
    )


    # =====================================================
    # LOSS
    # =====================================================

    criterion = create_loss_function(
        class_weights=
            class_weights,

        device=
            device,

        label_smoothing=
            config[
                "training"
            ][
                "label_smoothing"
            ],
    )


    # =====================================================
    # OPTIMIZER
    # =====================================================

    optimizer = create_optimizer(
        model=
            model,

        learning_rate=
            config[
                "training"
            ][
                "learning_rate"
            ],

        weight_decay=
            config[
                "training"
            ][
                "weight_decay"
            ],
    )


    scheduler = create_scheduler(
        optimizer=
            optimizer,

        epochs=
            args.epochs,
    )


    # =====================================================
    # OUTPUTS
    # =====================================================

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    CHECKPOINTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    checkpoint_path = (
        CHECKPOINTS_DIR
        /
        f"{args.run_name}_best.pth"
    )


    history_csv_path = (
        REPORTS_DIR
        /
        f"{args.run_name}_history.csv"
    )


    history_json_path = (
        REPORTS_DIR
        /
        f"{args.run_name}_history.json"
    )


    summary_path = (
        REPORTS_DIR
        /
        f"{args.run_name}_summary.json"
    )


    history = []

    best_validation_f1 = -1.0

    best_epoch = 0


    training_start = (
        time.time()
    )


    print()
    print("=" * 84)
    print("STAGE 1 TRAINING STARTED")
    print("=" * 84)


    # =====================================================
    # TRAINING LOOP
    # =====================================================

    for epoch in range(
        1,
        args.epochs + 1,
    ):

        epoch_start = (
            time.time()
        )


        print()
        print(
            f"Epoch {epoch}/{args.epochs}"
        )

        print("-" * 84)


        train_metrics = run_epoch(
            model=
                model,

            dataloader=
                train_loader,

            criterion=
                criterion,

            optimizer=
                optimizer,

            device=
                device,

            training=
                True,

            max_batches=
                args.max_train_batches,
        )


        validation_metrics = run_epoch(
            model=
                model,

            dataloader=
                validation_loader,

            criterion=
                criterion,

            optimizer=
                optimizer,

            device=
                device,

            training=
                False,

            max_batches=
                args.max_val_batches,
        )


        scheduler.step()


        epoch_seconds = (
            time.time()
            -
            epoch_start
        )


        print()

        print(
            "Train Loss       :",
            f"{train_metrics['loss']:.4f}"
        )

        print(
            "Train Accuracy   :",
            f"{train_metrics['accuracy']:.4f}"
        )

        print(
            "Train Macro F1   :",
            f"{train_metrics['macro_f1']:.4f}"
        )


        print()

        print(
            "Val Loss         :",
            f"{validation_metrics['loss']:.4f}"
        )

        print(
            "Val Accuracy     :",
            f"{validation_metrics['accuracy']:.4f}"
        )

        print(
            "Val Macro F1     :",
            f"{validation_metrics['macro_f1']:.4f}"
        )


        print(
            "Epoch Time       :",
            f"{epoch_seconds:.1f} sec"
        )


        row = {

            "epoch":
                epoch,

            "train_loss":
                train_metrics[
                    "loss"
                ],

            "train_accuracy":
                train_metrics[
                    "accuracy"
                ],

            "train_macro_f1":
                train_metrics[
                    "macro_f1"
                ],

            "validation_loss":
                validation_metrics[
                    "loss"
                ],

            "validation_accuracy":
                validation_metrics[
                    "accuracy"
                ],

            "validation_macro_f1":
                validation_metrics[
                    "macro_f1"
                ],

            "epoch_seconds":
                epoch_seconds,
        }


        history.append(
            row
        )


        current_f1 = (
            validation_metrics[
                "macro_f1"
            ]
        )


        if (
            current_f1
            >
            best_validation_f1
        ):

            best_validation_f1 = (
                current_f1
            )

            best_epoch = (
                epoch
            )


            save_checkpoint(
                path=
                    checkpoint_path,

                model=
                    model,

                optimizer=
                    optimizer,

                scheduler=
                    scheduler,

                epoch=
                    epoch,

                validation_macro_f1=
                    current_f1,

                model_name=
                    "tf_efficientnetv2_s.in21k_ft_in1k",

                class_to_index=
                    class_to_index,
            )


            print()

            print(
                "★ New best EfficientNet checkpoint saved."
            )


    # =====================================================
    # HISTORY SAVE
    # =====================================================

    fieldnames = [
        "epoch",
        "train_loss",
        "train_accuracy",
        "train_macro_f1",
        "validation_loss",
        "validation_accuracy",
        "validation_macro_f1",
        "epoch_seconds",
    ]


    with history_csv_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=
                fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            history
        )


    with history_json_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            history,
            file,
            indent=4,
        )


    total_seconds = (
        time.time()
        -
        training_start
    )


    summary = {

        "model":
            "tf_efficientnetv2_s.in21k_ft_in1k",

        "stage":
            1,

        "training_policy":
            "frozen_backbone_classifier_head_only",

        "device":
            str(
                device
            ),

        "requested_epochs":
            args.epochs,

        "completed_epochs":
            len(
                history
            ),

        "best_epoch":
            best_epoch,

        "best_validation_macro_f1":
            best_validation_f1,

        "total_parameters":
            total_parameters,

        "trainable_parameters":
            trainable_parameters,

        "trainable_percentage":
            trainable_percentage,

        "total_training_seconds":
            total_seconds,

        "checkpoint":
            str(
                checkpoint_path
            ),

        "timestamp":
            datetime.now().isoformat(
                timespec="seconds"
            ),
    }


    with summary_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
        )


    print()
    print("=" * 84)
    print("EFFICIENTNETV2-S STAGE 1 COMPLETE")
    print("=" * 84)


    print()
    print(
        "Best epoch       :",
        best_epoch
    )

    print(
        "Best Val Macro F1:",
        round(
            best_validation_f1,
            4
        )
    )

    print(
        "Total time       :",
        round(
            total_seconds
            /
            60,
            2
        ),
        "minutes"
    )


    print()
    print(
        "Checkpoint:"
    )

    print(
        checkpoint_path
    )


if __name__ == "__main__":

    main()