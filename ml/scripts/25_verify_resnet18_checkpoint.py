import sys
from pathlib import Path

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


from training.model_factory import create_model
from training.engine import get_device


# =========================================================
# CHECKPOINT
# =========================================================

CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "checkpoints"
    / "resnet18_baseline_best.pth"
)


def main():

    print("=" * 80)
    print("BREEDVISION AI - RESNET18 CHECKPOINT VERIFICATION")
    print("=" * 80)


    # =====================================================
    # FILE CHECK
    # =====================================================

    if not CHECKPOINT_PATH.exists():

        raise FileNotFoundError(
            f"Checkpoint not found:\n{CHECKPOINT_PATH}"
        )


    print()
    print(
        "Checkpoint:",
        CHECKPOINT_PATH
    )


    # =====================================================
    # DEVICE
    # =====================================================

    device = get_device()


    print(
        "Device:",
        device
    )


    # =====================================================
    # LOAD CHECKPOINT
    # =====================================================

    checkpoint = torch.load(
        CHECKPOINT_PATH,
        map_location=device,
        weights_only=False,
    )


    required_keys = {
        "epoch",
        "model_name",
        "model_state_dict",
        "validation_macro_f1",
        "class_to_index",
    }


    missing_keys = (
        required_keys
        -
        set(
            checkpoint.keys()
        )
    )


    if missing_keys:

        raise RuntimeError(
            f"Checkpoint is missing keys: "
            f"{sorted(missing_keys)}"
        )


    # =====================================================
    # CLASS INFORMATION
    # =====================================================

    class_to_index = (
        checkpoint[
            "class_to_index"
        ]
    )


    num_classes = len(
        class_to_index
    )


    # =====================================================
    # RECREATE MODEL
    # =====================================================

    model = create_model(
        model_name="resnet18",
        num_classes=num_classes,
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
    # DUMMY FORWARD PASS
    # =====================================================

    dummy_input = torch.randn(
        1,
        3,
        224,
        224,
        device=device,
    )


    with torch.no_grad():

        output = model(
            dummy_input
        )


    # =====================================================
    # DISPLAY
    # =====================================================

    print()
    print("-" * 80)

    print(
        "Checkpoint Epoch    :",
        checkpoint[
            "epoch"
        ]
    )

    print(
        "Validation Macro F1 :",
        round(
            float(
                checkpoint[
                    "validation_macro_f1"
                ]
            ),
            4,
        )
    )

    print(
        "Number of Classes   :",
        num_classes
    )

    print(
        "Output Shape        :",
        tuple(
            output.shape
        )
    )


    print()
    print("-" * 80)
    print("CLASS MAPPING")
    print("-" * 80)


    for breed, index in sorted(
        class_to_index.items(),
        key=lambda item: item[1],
    ):

        print(
            f"{index} -> {breed}"
        )


    # =====================================================
    # OUTPUT VALIDATION
    # =====================================================

    expected_shape = (
        1,
        num_classes,
    )


    if tuple(
        output.shape
    ) != expected_shape:

        raise RuntimeError(
            f"Unexpected model output shape. "
            f"Expected {expected_shape}, "
            f"got {tuple(output.shape)}"
        )


    print()
    print("=" * 80)
    print("CHECKPOINT STATUS: PASS")
    print("=" * 80)


if __name__ == "__main__":

    main()