from pathlib import Path
import random

import numpy as np
import torch

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)


# =========================================================
# BREEDVISION AI
# PHASE 5 - TRAINING ENGINE
# =========================================================


def set_seed(seed=42):

    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)


    if torch.cuda.is_available():

        torch.cuda.manual_seed_all(
            seed
        )


# =========================================================
# DEVICE
# =========================================================


def get_device():

    if torch.cuda.is_available():

        return torch.device(
            "cuda"
        )

    return torch.device(
        "cpu"
    )


# =========================================================
# LOSS FUNCTION
# =========================================================


def create_loss_function(
    class_weights,
    device,
    label_smoothing=0.0,
):

    class_weights = (
        class_weights
        .to(device)
    )


    criterion = (
        torch.nn.CrossEntropyLoss(
            weight=class_weights,
            label_smoothing=
                label_smoothing,
        )
    )


    return criterion


# =========================================================
# OPTIMIZER
# =========================================================


def create_optimizer(
    model,
    learning_rate,
    weight_decay,
):

    return torch.optim.AdamW(
        model.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay,
    )


# =========================================================
# SCHEDULER
# =========================================================


def create_scheduler(
    optimizer,
    epochs,
):

    return (
        torch.optim.lr_scheduler
        .CosineAnnealingLR(
            optimizer,
            T_max=epochs,
        )
    )


# =========================================================
# METRICS
# =========================================================


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

        "precision_macro":
            precision_score(
                targets,
                predictions,
                average="macro",
                zero_division=0,
            ),

        "recall_macro":
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


# =========================================================
# ONE TRAINING EPOCH
# =========================================================


def train_one_epoch(
    model,
    dataloader,
    criterion,
    optimizer,
    device,
):

    model.train()


    running_loss = 0.0

    all_targets = []

    all_predictions = []


    for batch in dataloader:

        images = (
            batch[
                "image"
            ]
            .to(
                device,
                non_blocking=True,
            )
        )


        targets = (
            batch[
                "label"
            ]
            .to(
                device,
                non_blocking=True,
            )
        )


        optimizer.zero_grad(
            set_to_none=True
        )


        logits = model(
            images
        )


        loss = criterion(
            logits,
            targets,
        )


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


    epoch_loss = (
        running_loss
        /
        len(
            dataloader.dataset
        )
    )


    metrics = (
        calculate_metrics(
            all_targets,
            all_predictions,
        )
    )


    metrics[
        "loss"
    ] = epoch_loss


    return metrics


# =========================================================
# VALIDATION / TEST
# =========================================================


@torch.no_grad()
def evaluate(
    model,
    dataloader,
    criterion,
    device,
):

    model.eval()


    running_loss = 0.0

    all_targets = []

    all_predictions = []


    for batch in dataloader:

        images = (
            batch[
                "image"
            ]
            .to(
                device,
                non_blocking=True,
            )
        )


        targets = (
            batch[
                "label"
            ]
            .to(
                device,
                non_blocking=True,
            )
        )


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
            logits.argmax(
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


    epoch_loss = (
        running_loss
        /
        len(
            dataloader.dataset
        )
    )


    metrics = (
        calculate_metrics(
            all_targets,
            all_predictions,
        )
    )


    metrics[
        "loss"
    ] = epoch_loss


    return metrics


# =========================================================
# CHECKPOINT
# =========================================================


def save_checkpoint(
    path,
    model,
    optimizer,
    scheduler,
    epoch,
    validation_macro_f1,
    model_name,
    class_to_index,
):

    path = Path(
        path
    )


    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    checkpoint = {

        "epoch":
            epoch,

        "model_name":
            model_name,

        "model_state_dict":
            model.state_dict(),

        "optimizer_state_dict":
            optimizer.state_dict(),

        "scheduler_state_dict":
            scheduler.state_dict(),

        "validation_macro_f1":
            validation_macro_f1,

        "class_to_index":
            class_to_index,
    }


    torch.save(
        checkpoint,
        path,
    )