import sys
from pathlib import Path
import json

import torch


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


from training.dataset import (
    create_dataloaders,
)

from training.model_factory import (
    create_model,
)

from training.engine import (
    get_device,
    create_loss_function,
    create_optimizer,
    create_scheduler,
    calculate_metrics,
    save_checkpoint,
)


# =========================================================
# CONFIG
# =========================================================


CONFIG_PATH = (
    PROJECT_ROOT
    / "configs"
    / "training_config.json"
)


with CONFIG_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    config = json.load(file)


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 80)
    print("BREEDVISION AI - TRAINING STACK SMOKE TEST")
    print("=" * 80)


    # =====================================================
    # DEVICE
    # =====================================================


    device = (
        get_device()
    )


    print()
    print(
        "Device:",
        device
    )


    # =====================================================
    # DATA
    # =====================================================


    data = (
        create_dataloaders()
    )


    train_loader = (
        data[
            "train_loader"
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


    num_classes = len(
        class_to_index
    )


    print(
        "Classes:",
        num_classes
    )


    # =====================================================
    # MODEL
    # =====================================================


    model = create_model(
        model_name="resnet18",
        num_classes=num_classes,
        pretrained=True,
    )


    model = model.to(
        device
    )


    print(
        "Model:",
        model.__class__.__name__
    )


    # =====================================================
    # LOSS
    # =====================================================


    criterion = (
        create_loss_function(
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
    )


    # =====================================================
    # OPTIMIZER
    # =====================================================


    optimizer = (
        create_optimizer(
            model=model,

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
    )


    # =====================================================
    # SCHEDULER
    # =====================================================


    scheduler = (
        create_scheduler(
            optimizer=
                optimizer,

            epochs=
                config[
                    "training"
                ][
                    "epochs"
                ],
        )
    )


    # =====================================================
    # ONE BATCH FORWARD/BACKWARD
    # =====================================================


    batch = next(
        iter(
            train_loader
        )
    )


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
        .to(
            device
        )
    )


    optimizer.zero_grad(
        set_to_none=True
    )


    logits = model(
        images
    )


    print()
    print(
        "Input shape :",
        tuple(
            images.shape
        )
    )


    print(
        "Output shape:",
        tuple(
            logits.shape
        )
    )


    expected_output_shape = (
        images.shape[0],
        num_classes,
    )


    if (
        tuple(
            logits.shape
        )
        !=
        expected_output_shape
    ):

        raise RuntimeError(
            "Invalid model output shape."
        )


    loss = criterion(
        logits,
        targets,
    )


    print(
        "Loss:",
        round(
            float(
                loss.item()
            ),
            6,
        )
    )


    loss.backward()


    optimizer.step()


    scheduler.step()


    # =====================================================
    # METRIC TEST
    # =====================================================


    predictions = (
        logits
        .argmax(
            dim=1
        )
        .detach()
        .cpu()
        .tolist()
    )


    target_list = (
        targets
        .detach()
        .cpu()
        .tolist()
    )


    metrics = (
        calculate_metrics(
            target_list,
            predictions,
        )
    )


    print()
    print("Batch Metrics:")


    for name, value in (
        metrics.items()
    ):

        print(
            f"  {name:<18}: "
            f"{value:.4f}"
        )


    # =====================================================
    # CHECKPOINT TEST
    # =====================================================


    test_checkpoint = (
        PROJECT_ROOT
        / "checkpoints"
        / "smoke_test_checkpoint.pth"
    )


    save_checkpoint(
        path=
            test_checkpoint,

        model=
            model,

        optimizer=
            optimizer,

        scheduler=
            scheduler,

        epoch=
            0,

        validation_macro_f1=
            0.0,

        model_name=
            "resnet18",

        class_to_index=
            class_to_index,
    )


    if not (
        test_checkpoint.exists()
    ):

        raise RuntimeError(
            "Checkpoint was not created."
        )


    print()
    print(
        "Checkpoint created:"
    )

    print(
        test_checkpoint
    )


    # Remove smoke-test checkpoint

    test_checkpoint.unlink()


    print(
        "Temporary checkpoint cleaned."
    )


    print()
    print("=" * 80)
    print("TRAINING STACK STATUS: PASS")
    print("=" * 80)


    print()
    print(
        "Model forward pass     : PASS"
    )

    print(
        "Weighted loss          : PASS"
    )

    print(
        "Backward pass          : PASS"
    )

    print(
        "Optimizer              : PASS"
    )

    print(
        "Scheduler              : PASS"
    )

    print(
        "Metrics                : PASS"
    )

    print(
        "Checkpoint system      : PASS"
    )


if __name__ == "__main__":

    main()