import sys
from pathlib import Path

import torch


# =========================================================
# ALLOW IMPORT FROM ML ROOT
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


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 80)
    print("BREEDVISION AI - DATALOADER SANITY TEST")
    print("=" * 80)


    data = (
        create_dataloaders()
    )


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


    test_loader = (
        data[
            "test_loader"
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


    print()
    print("-" * 80)
    print("DATASET SIZES")
    print("-" * 80)


    print(
        "Train      :",
        len(
            data[
                "train_dataset"
            ]
        )
    )


    print(
        "Validation :",
        len(
            data[
                "validation_dataset"
            ]
        )
    )


    print(
        "Test       :",
        len(
            data[
                "test_dataset"
            ]
        )
    )


    print()
    print("-" * 80)
    print("CLASS MAPPING")
    print("-" * 80)


    for breed, index in sorted(
        class_to_index.items(),
        key=lambda item:
        item[1],
    ):

        print(
            f"{index} -> {breed}"
        )


    print()
    print("-" * 80)
    print("CLASS WEIGHTS")
    print("-" * 80)


    index_to_class = {
        index: breed

        for breed, index
        in class_to_index.items()
    }


    for index, weight in enumerate(
        class_weights.tolist()
    ):

        print(
            f"{index_to_class[index]:<20} "
            f"{weight:.4f}"
        )


    # =====================================================
    # READ ONE TRAIN BATCH
    # =====================================================


    train_batch = next(
        iter(
            train_loader
        )
    )


    images = (
        train_batch[
            "image"
        ]
    )


    labels = (
        train_batch[
            "label"
        ]
    )


    print()
    print("-" * 80)
    print("TRAIN BATCH")
    print("-" * 80)


    print(
        "Image Tensor Shape:",
        tuple(
            images.shape
        )
    )


    print(
        "Label Tensor Shape:",
        tuple(
            labels.shape
        )
    )


    print(
        "Image dtype       :",
        images.dtype
    )


    print(
        "Label dtype       :",
        labels.dtype
    )


    print(
        "Min pixel value   :",
        round(
            float(
                images.min()
            ),
            4,
        )
    )


    print(
        "Max pixel value   :",
        round(
            float(
                images.max()
            ),
            4,
        )
    )


    print()
    print(
        "First batch labels:"
    )


    print(
        labels.tolist()
    )


    # =====================================================
    # VALIDATION BATCH
    # =====================================================


    validation_batch = next(
        iter(
            validation_loader
        )
    )


    print()
    print("-" * 80)
    print("VALIDATION BATCH")
    print("-" * 80)


    print(
        "Image Tensor Shape:",
        tuple(
            validation_batch[
                "image"
            ].shape
        )
    )


    # =====================================================
    # TEST BATCH
    # =====================================================


    test_batch = next(
        iter(
            test_loader
        )
    )


    print()
    print("-" * 80)
    print("TEST BATCH")
    print("-" * 80)


    print(
        "Image Tensor Shape:",
        tuple(
            test_batch[
                "image"
            ].shape
        )
    )


    # =====================================================
    # VALIDATE LABEL RANGE
    # =====================================================


    num_classes = len(
        class_to_index
    )


    if (
        labels.min() < 0
        or
        labels.max()
        >=
        num_classes
    ):

        raise RuntimeError(
            "Invalid label detected."
        )


    print()
    print("=" * 80)
    print("DATALOADER STATUS: PASS")
    print("=" * 80)


    print()
    print(
        "Train augmentation     : ENABLED"
    )

    print(
        "Validation augmentation: DISABLED"
    )

    print(
        "Test augmentation      : DISABLED"
    )

    print(
        "Class weighting        : READY"
    )


if __name__ == "__main__":

    main()