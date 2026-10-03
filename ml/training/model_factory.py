from pathlib import Path
import json

import torch.nn as nn
import torchvision.models as models
import timm


# =========================================================
# BREEDVISION AI
# PHASE 5 - MODEL FACTORY
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CONFIG_PATH = (
    PROJECT_ROOT
    / "configs"
    / "training_config.json"
)


def load_json(path):

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def get_num_classes():

    config = load_json(
        CONFIG_PATH
    )

    class_map_path = (
        PROJECT_ROOT
        / config["dataset"]["class_to_index"]
    )

    class_to_index = load_json(
        class_map_path
    )

    return len(
        class_to_index
    )


# =========================================================
# RESNET18
# =========================================================


def create_resnet18(
    num_classes,
    pretrained=True,
    freeze_backbone=False,
):

    if pretrained:

        weights = (
            models
            .ResNet18_Weights
            .DEFAULT
        )

    else:

        weights = None


    model = models.resnet18(
        weights=weights
    )


    # -----------------------------------------------------
    # Freeze pretrained feature extractor
    # -----------------------------------------------------

    if freeze_backbone:

        for parameter in model.parameters():

            parameter.requires_grad = False


    in_features = (
        model.fc.in_features
    )


    # New classifier remains trainable

    model.fc = nn.Linear(
        in_features,
        num_classes,
    )


    return model


# =========================================================
# EFFICIENTNETV2-S
# =========================================================


def create_efficientnetv2_s(
    num_classes,
    pretrained=True,
    freeze_backbone=False,
):

    model = timm.create_model(
        "tf_efficientnetv2_s.in21k_ft_in1k",
        pretrained=pretrained,
        num_classes=num_classes,
    )


    if freeze_backbone:

        for parameter in model.parameters():

            parameter.requires_grad = False


        # Re-enable classifier parameters

        classifier = model.get_classifier()


        for parameter in classifier.parameters():

            parameter.requires_grad = True


    return model


# =========================================================
# FACTORY
# =========================================================


def create_model(
    model_name,
    num_classes=None,
    pretrained=True,
    freeze_backbone=False,
):

    if num_classes is None:

        num_classes = (
            get_num_classes()
        )


    model_name = (
        model_name
        .strip()
        .lower()
    )


    if model_name == "resnet18":

        return create_resnet18(
            num_classes=num_classes,
            pretrained=pretrained,
            freeze_backbone=freeze_backbone,
        )


    if model_name in {
        "efficientnetv2_s",
        "tf_efficientnetv2_s.in21k_ft_in1k",
    }:

        return create_efficientnetv2_s(
            num_classes=num_classes,
            pretrained=pretrained,
            freeze_backbone=freeze_backbone,
        )


    raise ValueError(
        f"Unsupported model: {model_name}"
    )