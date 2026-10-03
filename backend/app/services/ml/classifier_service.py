import json
import threading

import torch
import torch.nn as nn

from PIL import Image

from torchvision import models
from torchvision import transforms

from app.services.ml.paths import (
    CALIBRATION_CONFIG,
    CLASSIFIER_CONFIG,
    CLASSIFIER_WEIGHTS,
    SPECIES_MAPPING,
    UNKNOWN_THRESHOLD_CONFIG,
)


class BreedClassifierService:

    def __init__(
        self,
    ):

        self._lock = (
            threading.Lock()
        )

        self.device = (
            torch.device(
                "cuda"
            )
            if torch.cuda.is_available()
            else torch.device(
                "cpu"
            )
        )

        self.classifier_config = (
            self._load_json(
                CLASSIFIER_CONFIG
            )
        )

        self.species_mapping = (
            self._load_json(
                SPECIES_MAPPING
            )
        )

        calibration = (
            self._load_json(
                CALIBRATION_CONFIG
            )
        )

        unknown_config = (
            self._load_json(
                UNKNOWN_THRESHOLD_CONFIG
            )
        )

        self.temperature = float(
            calibration[
                "temperature"
            ]
        )

        self.unknown_threshold = float(
            unknown_config[
                "threshold"
            ]
        )

        self.model_version = (
            self.classifier_config.get(
                "model_version",
                "breed-classifier-v2",
            )
        )

        checkpoint = torch.load(
            CLASSIFIER_WEIGHTS,
            map_location=
                self.device,
            weights_only=False,
        )

        self.class_to_index = (
            checkpoint[
                "class_to_index"
            ]
        )

        self.index_to_class = {
            int(index):
                breed

            for breed, index
            in self.class_to_index.items()
        }

        num_classes = len(
            self.class_to_index
        )

        self.model = (
            models.resnet18(
                weights=None
            )
        )

        self.model.fc = (
            nn.Linear(
                self.model.fc.in_features,
                num_classes,
            )
        )

        self.model.load_state_dict(
            checkpoint[
                "model_state_dict"
            ]
        )

        self.model = (
            self.model.to(
                self.device
            )
        )

        self.model.eval()

        self.transform = (
            transforms.Compose(
                [
                    transforms.Resize(
                        256
                    ),

                    transforms.CenterCrop(
                        224
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
        )


    @staticmethod
    def _load_json(
        path,
    ):

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(
                file
            )


    def predict(
        self,
        image: Image.Image,
        top_k: int = 3,
    ):

        if not isinstance(
            image,
            Image.Image,
        ):

            raise TypeError(
                "Classifier input must be a PIL image."
            )

        image = image.convert(
            "RGB"
        )

        tensor = (
            self.transform(
                image
            )
            .unsqueeze(0)
            .to(
                self.device
            )
        )

        with self._lock:

            with torch.no_grad():

                logits = (
                    self.model(
                        tensor
                    )
                )

                calibrated_logits = (
                    logits
                    /
                    self.temperature
                )

                probabilities = (
                    torch.softmax(
                        calibrated_logits,
                        dim=1,
                    )
                )

                k = min(
                    top_k,
                    len(
                        self.class_to_index
                    ),
                )

                scores, indices = (
                    probabilities.topk(
                        k=k,
                        dim=1,
                    )
                )

        scores = (
            scores[
                0
            ]
            .cpu()
            .tolist()
        )

        indices = (
            indices[
                0
            ]
            .cpu()
            .tolist()
        )

        top_predictions = []

        for rank, (
            score,
            class_index,
        ) in enumerate(
            zip(
                scores,
                indices,
            ),
            start=1,
        ):

            breed = (
                self.index_to_class[
                    int(
                        class_index
                    )
                ]
            )

            species = (
                self.species_mapping.get(
                    breed
                )
            )

            top_predictions.append(
                {
                    "rank":
                        rank,

                    "breed":
                        breed,

                    "species":
                        species,

                    "probability":
                        float(
                            score
                        ),
                }
            )

        best = (
            top_predictions[
                0
            ]
        )

        calibrated_probability = (
            float(
                best[
                    "probability"
                ]
            )
        )

        is_unknown = (
            calibrated_probability
            <
            self.unknown_threshold
        )

        return {
            "status":
                (
                    "unknown"
                    if is_unknown
                    else "known"
                ),

            "breed":
                (
                    None
                    if is_unknown
                    else best[
                        "breed"
                    ]
                ),

            "species":
                (
                    None
                    if is_unknown
                    else best[
                        "species"
                    ]
                ),

            "calibrated_probability":
                calibrated_probability,

            "confidence":
                calibrated_probability,

            "unknown_threshold":
                self.unknown_threshold,

            "temperature":
                self.temperature,

            "top_predictions":
                top_predictions,

            "model_version":
                self.model_version,

            "architecture":
                "resnet18",
        }


    def health(
        self,
    ):

        return {
            "ready":
                True,

            "device":
                str(
                    self.device
                ),

            "model_version":
                self.model_version,

            "num_classes":
                len(
                    self.class_to_index
                ),

            "temperature":
                self.temperature,

            "unknown_threshold":
                self.unknown_threshold,
        }