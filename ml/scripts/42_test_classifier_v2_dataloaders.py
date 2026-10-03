import sys
from pathlib import Path

import torch


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


from training.dataset_v2 import (
    create_v2_dataloaders
)


def main():

    print("=" * 88)
    print(
        "BREEDVISION AI - CLASSIFIER V2 DATALOADER TEST"
    )
    print("=" * 88)


    data = (
        create_v2_dataloaders()
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


    class_to_index = (
        data[
            "class_to_index"
        ]
    )


    class_weights = (
        data[
            "class_weights"
        ]
    )


    print()
    print(
        "Train images      :",
        len(
            train_loader.dataset
        )
    )

    print(
        "Validation images :",
        len(
            validation_loader.dataset
        )
    )

    print(
        "Test images       :",
        len(
            test_loader.dataset
        )
    )

    print(
        "Total images      :",
        (
            len(
                train_loader.dataset
            )
            +
            len(
                validation_loader.dataset
            )
            +
            len(
                test_loader.dataset
            )
        )
    )


    print()
    print(
        "Classes:",
        len(
            class_to_index
        )
    )


    for breed, index in (
        class_to_index.items()
    ):

        print(
            f"  {index:>2} -> "
            f"{breed}"
        )


    print()
    print(
        "Class weights:"
    )


    for breed, index in (
        class_to_index.items()
    ):

        print(
            f"  {breed:<20}"
            f"{class_weights[index].item():.4f}"
        )


    # =====================================================
    # ONE TRAIN BATCH
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
    )


    labels = (
        batch[
            "label"
        ]
    )


    print()
    print(
        "Image tensor shape:",
        tuple(
            images.shape
        )
    )

    print(
        "Label tensor shape:",
        tuple(
            labels.shape
        )
    )


    assert (
        images.ndim
        ==
        4
    )


    assert (
        images.shape[
            1
        ]
        ==
        3
    )


    assert (
        images.shape[
            2
        ]
        ==
        224
    )


    assert (
        images.shape[
            3
        ]
        ==
        224
    )


    assert (
        labels.min().item()
        >=
        0
    )


    assert (
        labels.max().item()
        <
        len(
            class_to_index
        )
    )


    assert torch.isfinite(
        images
    ).all()


    assert torch.isfinite(
        class_weights
    ).all()


    # =====================================================
    # TOTAL MUST STILL BE 6487
    # =====================================================


    total = (
        len(
            train_loader.dataset
        )
        +
        len(
            validation_loader.dataset
        )
        +
        len(
            test_loader.dataset
        )
    )


    assert (
        total
        ==
        6487
    ), (
        f"Expected 6487 images, "
        f"got {total}"
    )


    print()
    print("=" * 88)
    print(
        "CLASSIFIER V2 DATALOADER STATUS: PASS"
    )
    print("=" * 88)


if __name__ == "__main__":

    main()