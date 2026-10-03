import json
from pathlib import Path

import torch
import torch.nn as nn

from PIL import Image
from torchvision import models


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


from training.dataset_v2 import (
    build_eval_transform
)


class BreedVisionPhase7Predictor:

    def __init__(
        self,
        device=None,
    ):

        self.device = (
            torch.device(
                device
            )
            if device
            else
            (
                torch.device(
                    "cuda"
                )
                if torch.cuda.is_available()
                else
                torch.device(
                    "cpu"
                )
            )
        )


        calibration_path = (
            PROJECT_ROOT
            / "configs"
            / "phase7_calibration.json"
        )

        threshold_path = (
            PROJECT_ROOT
            / "configs"
            / "phase7_unknown_threshold.json"
        )

        species_path = (
            PROJECT_ROOT
            / "configs"
            / "classifier_v2_species_mapping.json"
        )

        weights_path = (
            PROJECT_ROOT
            / "weights"
            / "breed_classifier_v2.pth"
        )


        with calibration_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            calibration = json.load(
                file
            )


        with threshold_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            threshold = json.load(
                file
            )


        with species_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            self.species_mapping = (
                json.load(
                    file
                )
            )


        self.temperature = float(
            calibration[
                "temperature"
            ]
        )

        self.threshold = float(
            threshold[
                "threshold"
            ]
        )


        checkpoint = torch.load(
            weights_path,
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
            index: breed

            for breed, index
            in self.class_to_index.items()
        }


        self.model = models.resnet18(
            weights=None
        )


        self.model.fc = nn.Linear(
            self.model.fc.in_features,
            len(
                self.class_to_index
            ),
        )


        self.model.load_state_dict(
            checkpoint[
                "model_state_dict"
            ]
        )


        self.model = self.model.to(
            self.device
        )


        self.model.eval()


        self.transform = (
            build_eval_transform(
                224
            )
        )


    def predict(
        self,
        image_path,
        top_k=3,
    ):

        image_path = Path(
            image_path
        )


        with Image.open(
            image_path
        ) as image:

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


        with torch.no_grad():

            logits = self.model(
                tensor
            )


            calibrated_logits = (
                logits
                /
                self.temperature
            )


            probabilities = torch.softmax(
                calibrated_logits,
                dim=1,
            )


            number_of_predictions = min(
                top_k,
                len(
                    self.class_to_index
                ),
            )


            scores, indices = (
                probabilities.topk(
                    number_of_predictions,
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


        candidates = []


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
                    class_index
                ]
            )


            candidates.append(
                {
                    "rank":
                        rank,

                    "breed":
                        breed,

                    "species":
                        self.species_mapping[
                            breed
                        ],

                    "calibrated_probability":
                        float(
                            score
                        ),
                }
            )


        maximum_probability = float(
            scores[
                0
            ]
        )


        is_unknown = (
            maximum_probability
            <
            self.threshold
        )


        return {

            "status":
                (
                    "unknown"
                    if is_unknown
                    else
                    "known"
                ),

            "unknown":
                is_unknown,

            "threshold":
                self.threshold,

            "temperature":
                self.temperature,

            "max_calibrated_probability":
                maximum_probability,

            "predicted_breed":
                (
                    None
                    if is_unknown
                    else candidates[
                        0
                    ][
                        "breed"
                    ]
                ),

            "predicted_species":
                (
                    None
                    if is_unknown
                    else candidates[
                        0
                    ][
                        "species"
                    ]
                ),

            "top3":
                candidates,

            "note":
                (
                    "Probability is temperature-calibrated. "
                    "Unknown decision uses the frozen "
                    "Phase-7 threshold."
                ),
        }