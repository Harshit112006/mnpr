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
    calculate_metrics,
    save_checkpoint,
)


CONFIG_PATH = (
    PROJECT_ROOT
    / "configs"
    / "training_config.json"
)

STAGE1_CHECKPOINT = (
    PROJECT_ROOT
    / "checkpoints"
    / "efficientnetv2s_stage1_best.pth"
)

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)

CHECKPOINTS_DIR = (
    PROJECT_ROOT
    / "checkpoints"
)


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


def configure_stage2(model):

    # Freeze everything first
    for parameter in model.parameters():
        parameter.requires_grad = False


    # Unfreeze final EfficientNet block
    for parameter in model.blocks[-1].parameters():
        parameter.requires_grad = True


    # Unfreeze final head
    for parameter in model.conv_head.parameters():
        parameter.requires_grad = True


    for parameter in model.bn2.parameters():
        parameter.requires_grad = True


    for parameter in model.classifier.parameters():
        parameter.requires_grad = True


def set_finetune_train_mode(model):

    model.train()

    # Frozen BatchNorm layers should not update running stats
    for module in model.modules():

        if isinstance(
            module,
            torch.nn.modules.batchnorm._BatchNorm,
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
                    for parameter in parameters
                )
            ):

                module.eval()


def run_epoch(
    model,
    dataloader,
    criterion,
    optimizer,
    device,
    training,
):

    if training:
        set_finetune_train_mode(
            model
        )
    else:
        model.eval()


    running_loss = 0.0

    all_targets = []
    all_predictions = []


    progress = tqdm(
        dataloader,
        desc=(
            "Fine-tuning"
            if training
            else
            "Validation"
        ),
        leave=False,
    )


    for batch in progress:

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


def main():

    parser = argparse.ArgumentParser()


    parser.add_argument(
        "--epochs",
        type=int,
        default=1,
    )


    parser.add_argument(
        "--run-name",
        type=str,
        default="efficientnetv2s_stage2",
    )


    args = parser.parse_args()


    print("=" * 84)
    print(
        "BREEDVISION AI - EFFICIENTNETV2-S STAGE 2 FINE-TUNING"
    )
    print("=" * 84)


    if not STAGE1_CHECKPOINT.exists():

        raise FileNotFoundError(
            f"Stage-1 checkpoint missing:\n"
            f"{STAGE1_CHECKPOINT}"
        )


    config = load_json(
        CONFIG_PATH
    )


    set_seed(
        int(
            config[
                "training"
            ][
                "random_seed"
            ]
        )
    )


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


    device = get_device()


    print()
    print(
        "Device         :",
        device
    )

    print(
        "Epochs         :",
        args.epochs
    )

    print(
        "Fine-tune LR   :",
        0.00005
    )


    # =====================================================
    # DATA
    # =====================================================

    data = create_dataloaders()


    train_loader = (
        data["train_loader"]
    )

    validation_loader = (
        data["validation_loader"]
    )

    class_weights = (
        data["class_weights"]
    )

    class_to_index = (
        data["class_to_index"]
    )


    # =====================================================
    # LOAD STAGE-1 MODEL
    # =====================================================

    checkpoint = torch.load(
        STAGE1_CHECKPOINT,
        map_location=device,
        weights_only=False,
    )


    model = create_model(
        model_name=
            "tf_efficientnetv2_s.in21k_ft_in1k",

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


    configure_stage2(
        model
    )


    model = model.to(
        device
    )


    total_parameters, trainable_parameters = (
        count_parameters(
            model
        )
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
            trainable_parameters
            /
            total_parameters
            *
            100,
            4,
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

    trainable_parameters_list = [
        parameter

        for parameter
        in model.parameters()

        if parameter.requires_grad
    ]


    optimizer = torch.optim.AdamW(
        trainable_parameters_list,
        lr=0.00005,
        weight_decay=float(
            config[
                "training"
            ][
                "weight_decay"
            ]
        ),
    )


    scheduler = (
        torch.optim.lr_scheduler
        .CosineAnnealingLR(
            optimizer,
            T_max=args.epochs,
        )
    )


    # =====================================================
    # OUTPUT PATHS
    # =====================================================

    CHECKPOINTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    checkpoint_path = (
        CHECKPOINTS_DIR
        /
        f"{args.run_name}_best.pth"
    )


    history_path = (
        REPORTS_DIR
        /
        f"{args.run_name}_history.csv"
    )


    summary_path = (
        REPORTS_DIR
        /
        f"{args.run_name}_summary.json"
    )


    best_f1 = -1.0
    best_epoch = 0

    history = []

    start_time = time.time()


    # =====================================================
    # TRAIN
    # =====================================================

    for epoch in range(
        1,
        args.epochs + 1
    ):

        epoch_start = time.time()


        print()
        print(
            f"Epoch {epoch}/{args.epochs}"
        )

        print("-" * 84)


        train_metrics = run_epoch(
            model,
            train_loader,
            criterion,
            optimizer,
            device,
            True,
        )


        validation_metrics = run_epoch(
            model,
            validation_loader,
            criterion,
            optimizer,
            device,
            False,
        )


        scheduler.step()


        epoch_seconds = (
            time.time()
            -
            epoch_start
        )


        print()

        print(
            "Train Loss     :",
            f"{train_metrics['loss']:.4f}"
        )

        print(
            "Train Macro F1 :",
            f"{train_metrics['macro_f1']:.4f}"
        )


        print()

        print(
            "Val Loss       :",
            f"{validation_metrics['loss']:.4f}"
        )

        print(
            "Val Accuracy   :",
            f"{validation_metrics['accuracy']:.4f}"
        )

        print(
            "Val Macro F1   :",
            f"{validation_metrics['macro_f1']:.4f}"
        )

        print(
            "Epoch Time     :",
            f"{epoch_seconds:.1f} sec"
        )


        history.append(
            {
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
        )


        current_f1 = (
            validation_metrics[
                "macro_f1"
            ]
        )


        if current_f1 > best_f1:

            best_f1 = current_f1
            best_epoch = epoch


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
                "★ New Stage-2 best checkpoint saved."
            )


    # =====================================================
    # SAVE HISTORY
    # =====================================================

    with history_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "epoch",
                "train_loss",
                "train_accuracy",
                "train_macro_f1",
                "validation_loss",
                "validation_accuracy",
                "validation_macro_f1",
                "epoch_seconds",
            ],
        )

        writer.writeheader()

        writer.writerows(
            history
        )


    total_seconds = (
        time.time()
        -
        start_time
    )


    summary = {

        "model":
            "tf_efficientnetv2_s.in21k_ft_in1k",

        "stage":
            2,

        "training_policy":
            "last_block_and_classifier_finetuning",

        "parent_checkpoint":
            str(
                STAGE1_CHECKPOINT
            ),

        "device":
            str(
                device
            ),

        "completed_epochs":
            len(
                history
            ),

        "best_epoch":
            best_epoch,

        "best_validation_macro_f1":
            best_f1,

        "learning_rate":
            0.00005,

        "total_parameters":
            total_parameters,

        "trainable_parameters":
            trainable_parameters,

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
    print(
        "EFFICIENTNETV2-S STAGE 2 COMPLETE"
    )
    print("=" * 84)


    print()
    print(
        "Best Val Macro F1:",
        round(
            best_f1,
            4
        )
    )

    print(
        "Checkpoint:"
    )

    print(
        checkpoint_path
    )


if __name__ == "__main__":

    main()