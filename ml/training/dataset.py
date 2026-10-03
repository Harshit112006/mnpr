from pathlib import Path
import json

import pandas as pd
import torch

from PIL import Image

from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


# =========================================================
# BREEDVISION AI
# PHASE 5 - DATASET / DATALOADER PIPELINE
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]


TRAINING_CONFIG_PATH = (
    PROJECT_ROOT
    / "configs"
    / "training_config.json"
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


def get_training_config():
    return load_json(
        TRAINING_CONFIG_PATH
    )


# =========================================================
# IMAGE TRANSFORMS
# =========================================================


def get_train_transform(
    image_size=224,
):

    return transforms.Compose(
        [
            transforms.RandomResizedCrop(
                size=image_size,
                scale=(0.80, 1.0),
                ratio=(0.85, 1.15),
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


def get_eval_transform(
    image_size=224,
):

    return transforms.Compose(
        [
            transforms.Resize(
                size=256
            ),

            transforms.CenterCrop(
                size=image_size
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


class BreedVisionDataset(Dataset):

    def __init__(
        self,
        dataframe,
        transform=None,
    ):

        self.dataframe = (
            dataframe
            .reset_index(
                drop=True
            )
            .copy()
        )

        self.transform = transform


    def __len__(self):

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


        breed = str(
            row[
                "breed"
            ]
        )


        class_index = int(
            row[
                "class_index"
            ]
        )


        # ---------------------------------------------
        # Read image safely
        # ---------------------------------------------

        with Image.open(
            image_path
        ) as image:

            image = image.convert(
                "RGB"
            )


            if self.transform:

                image = self.transform(
                    image
                )


        return {
            "image":
                image,

            "label":
                torch.tensor(
                    class_index,
                    dtype=torch.long,
                ),

            "breed":
                breed,

            "image_path":
                str(
                    image_path
                ),
        }


# =========================================================
# LOAD MANIFEST
# =========================================================


def load_dataset_manifest():

    config = (
        get_training_config()
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


    if not manifest_path.exists():

        raise FileNotFoundError(
            f"Dataset manifest not found:\n"
            f"{manifest_path}"
        )


    dataframe = pd.read_csv(
        manifest_path
    )


    return dataframe


# =========================================================
# TRAIN / VAL / TEST DATAFRAMES
# =========================================================


def get_split_dataframes():

    dataframe = (
        load_dataset_manifest()
    )


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


    return (
        train_df,
        validation_df,
        test_df,
    )


# =========================================================
# CLASS WEIGHTS
#
# Calculated ONLY from training split.
# =========================================================


def calculate_class_weights(
    train_df,
    num_classes,
):

    class_counts = (
        train_df[
            "class_index"
        ]
        .value_counts()
        .sort_index()
    )


    total_samples = len(
        train_df
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


        if count == 0:

            raise ValueError(
                f"Class index {class_index} "
                f"has no training samples."
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
# BUILD DATALOADERS
# =========================================================


def create_dataloaders():

    config = (
        get_training_config()
    )


    image_size = int(
        config[
            "dataset"
        ][
            "image_size"
        ]
    )


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


    (
        train_df,
        validation_df,
        test_df,
    ) = get_split_dataframes()


    # =====================================================
    # TRANSFORMS
    #
    # Train      -> augmentation
    # Validation -> deterministic
    # Test       -> deterministic
    # =====================================================


    train_dataset = (
        BreedVisionDataset(
            dataframe=train_df,
            transform=get_train_transform(
                image_size
            ),
        )
    )


    validation_dataset = (
        BreedVisionDataset(
            dataframe=validation_df,
            transform=get_eval_transform(
                image_size
            ),
        )
    )


    test_dataset = (
        BreedVisionDataset(
            dataframe=test_df,
            transform=get_eval_transform(
                image_size
            ),
        )
    )


    train_loader = DataLoader(
        train_dataset,

        batch_size=
            batch_size,

        shuffle=True,

        num_workers=
            num_workers,

        pin_memory=
            pin_memory,

        drop_last=False,
    )


    validation_loader = DataLoader(
        validation_dataset,

        batch_size=
            batch_size,

        shuffle=False,

        num_workers=
            num_workers,

        pin_memory=
            pin_memory,

        drop_last=False,
    )


    test_loader = DataLoader(
        test_dataset,

        batch_size=
            batch_size,

        shuffle=False,

        num_workers=
            num_workers,

        pin_memory=
            pin_memory,

        drop_last=False,
    )


    class_to_index_path = (
        PROJECT_ROOT
        /
        config[
            "dataset"
        ][
            "class_to_index"
        ]
    )


    class_to_index = load_json(
        class_to_index_path
    )


    class_weights = (
        calculate_class_weights(
            train_df=
                train_df,

            num_classes=
                len(
                    class_to_index
                ),
        )
    )


    return {
        "train_loader":
            train_loader,

        "validation_loader":
            validation_loader,

        "test_loader":
            test_loader,

        "train_dataset":
            train_dataset,

        "validation_dataset":
            validation_dataset,

        "test_dataset":
            test_dataset,

        "class_weights":
            class_weights,

        "class_to_index":
            class_to_index,

        "train_df":
            train_df,

        "validation_df":
            validation_df,

        "test_df":
            test_df,
    }