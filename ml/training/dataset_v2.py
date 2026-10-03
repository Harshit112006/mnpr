from pathlib import Path
import json
import random

import numpy as np
import pandas as pd
import torch

from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


# =========================================================
# BREEDVISION AI
# PHASE 6 - CLASSIFIER V2 DATASET
# =========================================================


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


CONFIG_PATH = (
    PROJECT_ROOT
    / "configs"
    / "training_config_v2.json"
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


def set_seed(seed):

    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)


# =========================================================
# TRANSFORMS
# =========================================================


def build_train_transform(
    image_size,
):

    return transforms.Compose(
        [
            transforms.RandomResizedCrop(
                image_size,
                scale=(
                    0.80,
                    1.00,
                ),
                ratio=(
                    0.85,
                    1.15,
                ),
            ),

            transforms.RandomHorizontalFlip(
                p=0.5
            ),

            transforms.RandomRotation(
                degrees=10
            ),

            transforms.ColorJitter(
                brightness=0.15,
                contrast=0.15,
                saturation=0.12,
                hue=0.03,
            ),

            transforms.ToTensor(),

            transforms.Normalize(
                mean=[
                    0.485,
                    0.456,
                    0.406,
                ],
                std=[
                    0.229,
                    0.224,
                    0.225,
                ],
            ),
        ]
    )


def build_eval_transform(
    image_size,
):

    resize_size = 256


    return transforms.Compose(
        [
            transforms.Resize(
                resize_size
            ),

            transforms.CenterCrop(
                image_size
            ),

            transforms.ToTensor(),

            transforms.Normalize(
                mean=[
                    0.485,
                    0.456,
                    0.406,
                ],
                std=[
                    0.229,
                    0.224,
                    0.225,
                ],
            ),
        ]
    )


# =========================================================
# DATASET
# =========================================================


class BreedVisionDatasetV2(
    Dataset
):

    def __init__(
        self,
        dataframe,
        transform,
    ):

        self.dataframe = (
            dataframe
            .reset_index(
                drop=True
            )
            .copy()
        )

        self.transform = transform


    def __len__(
        self
    ):

        return len(
            self.dataframe
        )


    def __getitem__(
        self,
        index,
    ):

        row = (
            self.dataframe
            .iloc[
                index
            ]
        )


        image_path = Path(
            row[
                "image_path"
            ]
        )


        with Image.open(
            image_path
        ) as image:

            image = (
                image
                .convert(
                    "RGB"
                )
            )


        image = self.transform(
            image
        )


        label = int(
            row[
                "class_index"
            ]
        )


        return {
            "image":
                image,

            "label":
                torch.tensor(
                    label,
                    dtype=torch.long,
                ),

            "image_path":
                str(
                    image_path
                ),

            "breed":
                str(
                    row[
                        "breed"
                    ]
                ),

            "species":
                str(
                    row[
                        "species"
                    ]
                ),
        }


# =========================================================
# CLASS WEIGHTS
# =========================================================


def calculate_class_weights(
    train_dataframe,
    num_classes,
):

    class_counts = (
        train_dataframe[
            "class_index"
        ]
        .astype(int)
        .value_counts()
        .to_dict()
    )


    total_samples = len(
        train_dataframe
    )


    weights = []


    for class_index in range(
        num_classes
    ):

        count = int(
            class_counts.get(
                class_index,
                0,
            )
        )


        if count <= 0:

            raise RuntimeError(
                f"Class {class_index} has "
                f"zero training samples."
            )


        weight = (
            total_samples
            /
            (
                num_classes
                *
                count
            )
        )


        weights.append(
            weight
        )


    return torch.tensor(
        weights,
        dtype=torch.float32,
    )


# =========================================================
# DATA LOADERS
# =========================================================


def create_v2_dataloaders():

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


    manifest_path = (
        PROJECT_ROOT
        /
        config[
            "dataset"
        ][
            "manifest"
        ]
    )


    class_map_path = (
        PROJECT_ROOT
        /
        config[
            "dataset"
        ][
            "class_to_index"
        ]
    )


    dataframe = pd.read_csv(
        manifest_path
    )


    class_to_index = load_json(
        class_map_path
    )


    image_size = int(
        config[
            "dataset"
        ][
            "image_size"
        ]
    )


    # =====================================================
    # BASIC VALIDATION
    # =====================================================


    required_columns = {
        "image_path",
        "breed",
        "species",
        "class_index",
        "split",
        "group_id",
    }


    missing_columns = (
        required_columns
        -
        set(
            dataframe.columns
        )
    )


    if missing_columns:

        raise RuntimeError(
            f"Missing manifest columns: "
            f"{sorted(missing_columns)}"
        )


    valid_splits = {
        "train",
        "validation",
        "test",
    }


    invalid_splits = set(
        dataframe[
            "split"
        ]
        .astype(str)
    ) - valid_splits


    if invalid_splits:

        raise RuntimeError(
            f"Invalid splits found: "
            f"{invalid_splits}"
        )


    if (
        dataframe[
            "image_path"
        ]
        .duplicated()
        .any()
    ):

        raise RuntimeError(
            "Duplicate image paths detected."
        )


    # =====================================================
    # SPLITS
    # =====================================================


    train_df = (
        dataframe[
            dataframe[
                "split"
            ]
            ==
            "train"
        ]
        .copy()
    )


    validation_df = (
        dataframe[
            dataframe[
                "split"
            ]
            ==
            "validation"
        ]
        .copy()
    )


    test_df = (
        dataframe[
            dataframe[
                "split"
            ]
            ==
            "test"
        ]
        .copy()
    )


    num_classes = len(
        class_to_index
    )


    # =====================================================
    # VERIFY EVERY CLASS EXISTS IN ALL SPLITS
    # =====================================================


    expected_indices = set(
        class_to_index.values()
    )


    for name, split_df in [
        (
            "train",
            train_df,
        ),
        (
            "validation",
            validation_df,
        ),
        (
            "test",
            test_df,
        ),
    ]:

        indices = set(
            split_df[
                "class_index"
            ]
            .astype(int)
            .unique()
            .tolist()
        )


        missing = (
            expected_indices
            -
            indices
        )


        if missing:

            raise RuntimeError(
                f"{name} split missing "
                f"class indices: {sorted(missing)}"
            )


    # =====================================================
    # TRANSFORMS
    # =====================================================


    train_transform = (
        build_train_transform(
            image_size
        )
    )


    eval_transform = (
        build_eval_transform(
            image_size
        )
    )


    # =====================================================
    # DATASETS
    # =====================================================


    train_dataset = (
        BreedVisionDatasetV2(
            train_df,
            train_transform,
        )
    )


    validation_dataset = (
        BreedVisionDatasetV2(
            validation_df,
            eval_transform,
        )
    )


    test_dataset = (
        BreedVisionDatasetV2(
            test_df,
            eval_transform,
        )
    )


    # =====================================================
    # CLASS WEIGHTS
    # =====================================================


    class_weights = (
        calculate_class_weights(
            train_dataframe=
                train_df,

            num_classes=
                num_classes,
        )
    )


    # =====================================================
    # LOADERS
    # =====================================================


    batch_size = int(
        config[
            "dataloader"
        ][
            "batch_size"
        ]
    )


    num_workers = int(
        config[
            "dataloader"
        ][
            "num_workers"
        ]
    )


    pin_memory = bool(
        config[
            "dataloader"
        ][
            "pin_memory"
        ]
    )


    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )


    validation_loader = DataLoader(
        validation_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )


    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )


    return {
        "train_loader":
            train_loader,

        "validation_loader":
            validation_loader,

        "test_loader":
            test_loader,

        "train_dataframe":
            train_df,

        "validation_dataframe":
            validation_df,

        "test_dataframe":
            test_df,

        "class_weights":
            class_weights,

        "class_to_index":
            class_to_index,

        "num_classes":
            num_classes,
    }