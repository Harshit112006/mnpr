import argparse
import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import torch
from torch.utils.tensorboard import SummaryWriter
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

RUNS_DIR = (
    PROJECT_ROOT
    / "runs"
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


def train_epoch(
    model,
    dataloader,
    criterion,
    optimizer,
    device,
    scaler,
    use_amp,
):

    model.train()

    running_loss = 0.0

    all_targets = []
    all_predictions = []


    progress = tqdm(
        dataloader,
        desc="Training",
        leave=False,
    )


    for batch in progress:

        images = (
            batch["image"]
            .to(
                device,
                non_blocking=True,
            )
        )

        targets = (
            batch["label"]
            .to(
                device,
                non_blocking=True,
            )
        )


        optimizer.zero_grad(
            set_to_none=True
        )


        with torch.amp.autocast(
            device_type=device.type,
            enabled=use_amp,
        ):

            logits = model(
                images
            )

            loss = criterion(
                logits,
                targets,
            )


        if use_amp:

            scaler.scale(
                loss
            ).backward()

            scaler.step(
                optimizer
            )

            scaler.update()

        else:

            loss.backward()

            optimizer.step()


        running_loss += (
            loss.item()
            *
            images.size(0)
        )


        predictions = (
            logits
            .argmax(
                dim=1
            )
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
        len(
            dataloader.dataset
        )
    )


    return metrics


@torch.no_grad()
def validate_epoch(
    model,
    dataloader,
    criterion,
    device,
    use_amp,
):

    model.eval()

    running_loss = 0.0

    all_targets = []
    all_predictions = []


    progress = tqdm(
        dataloader,
        desc="Validation",
        leave=False,
    )


    for batch in progress:

        images = (
            batch["image"]
            .to(
                device,
                non_blocking=True,
            )
        )

        targets = (
            batch["label"]
            .to(
                device,
                non_blocking=True,
            )
        )


        with torch.amp.autocast(
            device_type=device.type,
            enabled=use_amp,
        ):

            logits = model(
                images
            )

            loss = criterion(
                logits,
                targets,
            )


        running_loss += (
            loss.item()
            *
            images.size(0)
        )


        predictions = (
            logits
            .argmax(
                dim=1
            )
        )


        all_targets.extend(
            targets
            .cpu()
            .tolist()
        )

        all_predictions.extend(
            predictions
            .cpu()
            .tolist()
        )


    metrics = calculate_metrics(
        all_targets,
        all_predictions,
    )


    metrics["loss"] = (
        running_loss
        /
        len(
            dataloader.dataset
        )
    )


    return metrics


def save_history_csv(
    path,
    history,
):

    fieldnames = [
        "epoch",
        "learning_rate",
        "train_loss",
        "train_accuracy",
        "train_macro_f1",
        "train_weighted_f1",
        "validation_loss",
        "validation_accuracy",
        "validation_macro_f1",
        "validation_weighted_f1",
        "epoch_seconds",
    ]


    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            history
        )


# =========================================================
# MAIN TRAINING
# =========================================================


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--epochs",
        type=int,
        default=None,
        help="Override epochs from training_config.json",
    )

    parser.add_argument(
        "--run-name",
        type=str,
        default="resnet18_baseline",
    )

    args = parser.parse_args()


    print("=" * 84)
    print("BREEDVISION AI - RESNET18 BASELINE TRAINING")
    print("=" * 84)


    # =====================================================
    # CONFIG
    # =====================================================

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


    configured_epochs = int(
        config[
            "training"
        ][
            "epochs"
        ]
    )


    epochs = (
        args.epochs
        if args.epochs is not None
        else configured_epochs
    )


    learning_rate = float(
        config[
            "training"
        ][
            "learning_rate"
        ]
    )


    weight_decay = float(
        config[
            "training"
        ][
            "weight_decay"
        ]
    )


    label_smoothing = float(
        config[
            "training"
        ][
            "label_smoothing"
        ]
    )


    patience = int(
        config[
            "training"
        ][
            "early_stopping_patience"
        ]
    )


    # =====================================================
    # DEVICE
    # =====================================================

    device = get_device()


    use_amp = (
        device.type == "cuda"
        and
        bool(
            config[
                "device"
            ][
                "mixed_precision_on_cuda"
            ]
        )
    )


    print()
    print("Device            :", device)
    print("Mixed Precision   :", use_amp)
    print("Epochs            :", epochs)
    print("Learning Rate     :", learning_rate)
    print("Weight Decay      :", weight_decay)
    print("Label Smoothing   :", label_smoothing)
    print("Early Stop        :", patience)


    # =====================================================
    # DATA
    # =====================================================

    print()
    print("Loading dataset...")


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


    print("Train images      :", len(train_loader.dataset))
    print("Validation images :", len(validation_loader.dataset))
    print("Classes           :", len(class_to_index))


    # =====================================================
    # MODEL
    # =====================================================

    print()
    print("Creating pretrained ResNet18...")


    model = create_model(
    model_name="resnet18",
    num_classes=len(
        class_to_index
    ),
    pretrained=True,
    freeze_backbone=True,
)


    model = model.to(
        device
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
            label_smoothing,
    )


    # =====================================================
    # OPTIMIZER
    # =====================================================

    optimizer = create_optimizer(
        model=
            model,

        learning_rate=
            learning_rate,

        weight_decay=
            weight_decay,
    )


    # =====================================================
    # SCHEDULER
    # =====================================================

    scheduler = create_scheduler(
        optimizer=
            optimizer,

        epochs=
            epochs,
    )


    # =====================================================
    # AMP
    # =====================================================

    scaler = torch.amp.GradScaler(
        "cuda",
        enabled=use_amp,
    )


    # =====================================================
    # OUTPUT PATHS
    # =====================================================

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    CHECKPOINTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    RUNS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    run_name = args.run_name


    checkpoint_path = (
        CHECKPOINTS_DIR
        /
        f"{run_name}_best.pth"
    )


    history_csv_path = (
        REPORTS_DIR
        /
        f"{run_name}_history.csv"
    )


    history_json_path = (
        REPORTS_DIR
        /
        f"{run_name}_history.json"
    )


    summary_path = (
        REPORTS_DIR
        /
        f"{run_name}_summary.json"
    )


    tensorboard_path = (
        RUNS_DIR
        /
        run_name
    )


    writer = SummaryWriter(
        log_dir=
            tensorboard_path
    )


    # =====================================================
    # TRAINING
    # =====================================================

    best_validation_f1 = -1.0

    best_epoch = 0

    epochs_without_improvement = 0

    history = []

    training_start = time.time()


    print()
    print("=" * 84)
    print("TRAINING STARTED")
    print("=" * 84)


    for epoch in range(
        1,
        epochs + 1,
    ):

        epoch_start = time.time()


        print()
        print(
            f"Epoch {epoch}/{epochs}"
        )

        print("-" * 84)


        current_lr = (
            optimizer
            .param_groups[0]["lr"]
        )


        # =================================================
        # TRAIN
        # =================================================

        train_metrics = train_epoch(
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

            scaler=
                scaler,

            use_amp=
                use_amp,
        )


        # =================================================
        # VALIDATION
        # =================================================

        validation_metrics = validate_epoch(
            model=
                model,

            dataloader=
                validation_loader,

            criterion=
                criterion,

            device=
                device,

            use_amp=
                use_amp,
        )


        scheduler.step()


        epoch_seconds = (
            time.time()
            -
            epoch_start
        )


        # =================================================
        # HISTORY
        # =================================================

        history_row = {

            "epoch":
                epoch,

            "learning_rate":
                current_lr,

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

            "train_weighted_f1":
                train_metrics[
                    "weighted_f1"
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

            "validation_weighted_f1":
                validation_metrics[
                    "weighted_f1"
                ],

            "epoch_seconds":
                epoch_seconds,
        }


        history.append(
            history_row
        )


        # =================================================
        # TENSORBOARD
        # =================================================

        writer.add_scalar(
            "Loss/Train",
            train_metrics[
                "loss"
            ],
            epoch,
        )


        writer.add_scalar(
            "Loss/Validation",
            validation_metrics[
                "loss"
            ],
            epoch,
        )


        writer.add_scalar(
            "MacroF1/Train",
            train_metrics[
                "macro_f1"
            ],
            epoch,
        )


        writer.add_scalar(
            "MacroF1/Validation",
            validation_metrics[
                "macro_f1"
            ],
            epoch,
        )


        writer.add_scalar(
            "Accuracy/Train",
            train_metrics[
                "accuracy"
            ],
            epoch,
        )


        writer.add_scalar(
            "Accuracy/Validation",
            validation_metrics[
                "accuracy"
            ],
            epoch,
        )


        writer.add_scalar(
            "LearningRate",
            current_lr,
            epoch,
        )


        # =================================================
        # DISPLAY
        # =================================================

        print()

        print(
            f"Train Loss       : "
            f"{train_metrics['loss']:.4f}"
        )

        print(
            f"Train Accuracy   : "
            f"{train_metrics['accuracy']:.4f}"
        )

        print(
            f"Train Macro F1   : "
            f"{train_metrics['macro_f1']:.4f}"
        )


        print()

        print(
            f"Val Loss         : "
            f"{validation_metrics['loss']:.4f}"
        )

        print(
            f"Val Accuracy     : "
            f"{validation_metrics['accuracy']:.4f}"
        )

        print(
            f"Val Macro F1     : "
            f"{validation_metrics['macro_f1']:.4f}"
        )


        print(
            f"Epoch Time       : "
            f"{epoch_seconds:.1f} sec"
        )


        # =================================================
        # BEST CHECKPOINT
        # =================================================

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

            best_epoch = epoch

            epochs_without_improvement = 0


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
                    best_validation_f1,

                model_name=
                    "resnet18",

                class_to_index=
                    class_to_index,
            )


            print()

            print(
                "★ New best checkpoint saved."
            )

            print(
                f"Best Macro F1: "
                f"{best_validation_f1:.4f}"
            )


        else:

            epochs_without_improvement += 1


            print()

            print(
                "No validation improvement."
            )

            print(
                "Patience:",
                f"{epochs_without_improvement}/{patience}"
            )


        # =================================================
        # SAVE HISTORY EVERY EPOCH
        # =================================================

        save_history_csv(
            history_csv_path,
            history,
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


        # =================================================
        # EARLY STOPPING
        # =================================================

        if (
            epochs_without_improvement
            >=
            patience
        ):

            print()
            print("=" * 84)

            print(
                "EARLY STOPPING TRIGGERED"
            )

            print("=" * 84)

            break


    # =====================================================
    # FINISH
    # =====================================================

    writer.close()


    total_seconds = (
        time.time()
        -
        training_start
    )


    completed_epochs = len(
        history
    )


    summary = {

        "model":
            "resnet18",

        "run_name":
            run_name,

        "timestamp":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "device":
            str(
                device
            ),

        "mixed_precision":
            use_amp,

        "requested_epochs":
            epochs,

        "completed_epochs":
            completed_epochs,

        "best_epoch":
            best_epoch,

        "best_validation_macro_f1":
            best_validation_f1,

        "total_training_seconds":
            total_seconds,

        "checkpoint":
            str(
                checkpoint_path
            ),

        "training_images":
            len(
                train_loader.dataset
            ),

        "validation_images":
            len(
                validation_loader.dataset
            ),

        "num_classes":
            len(
                class_to_index
            ),

        "class_to_index":
            class_to_index,
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
    print("TRAINING COMPLETE")
    print("=" * 84)


    print()
    print(
        "Completed epochs :",
        completed_epochs
    )

    print(
        "Best epoch       :",
        best_epoch
    )

    print(
        "Best Val Macro F1:",
        round(
            best_validation_f1,
            4,
        )
    )

    print(
        "Total time       :",
        round(
            total_seconds
            /
            60,
            2,
        ),
        "minutes",
    )


    print()
    print(
        "Best checkpoint:"
    )

    print(
        checkpoint_path
    )


    print()
    print(
        "Training history:"
    )

    print(
        history_csv_path
    )


    print()
    print(
        "Summary:"
    )

    print(
        summary_path
    )


if __name__ == "__main__":

    main()