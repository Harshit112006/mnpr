import csv
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

from PIL import Image
from torchvision import models, transforms


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
    build_eval_transform
)


WEIGHTS_PATH = (
    PROJECT_ROOT
    / "weights"
    / "breed_classifier_v2.pth"
)

CALIBRATION_CONFIG = (
    PROJECT_ROOT
    / "configs"
    / "phase7_calibration.json"
)

THRESHOLD_CONFIG = (
    PROJECT_ROOT
    / "configs"
    / "phase7_unknown_threshold.json"
)

MANIFEST = (
    PROJECT_ROOT
    / "reports"
    / "classifier_v2_final_manifest.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "phase7"
    / "gradcam"
)

OUTPUT_CSV = (
    PROJECT_ROOT
    / "reports"
    / "phase7_gradcam_examples.csv"
)

OUTPUT_JSON = (
    PROJECT_ROOT
    / "reports"
    / "phase7_gradcam_summary.json"
)


def load_json(path):

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


class GradCAM:

    def __init__(
        self,
        model,
        target_layer,
    ):

        self.model = model

        self.activations = None
        self.gradients = None


        self.forward_handle = (
            target_layer.register_forward_hook(
                self._forward_hook
            )
        )


        self.backward_handle = (
            target_layer.register_full_backward_hook(
                self._backward_hook
            )
        )


    def _forward_hook(
        self,
        module,
        inputs,
        output,
    ):

        self.activations = (
            output.detach()
        )


    def _backward_hook(
        self,
        module,
        grad_input,
        grad_output,
    ):

        self.gradients = (
            grad_output[
                0
            ].detach()
        )


    def generate(
        self,
        tensor,
        target_index,
    ):

        self.model.zero_grad(
            set_to_none=True
        )


        logits = self.model(
            tensor
        )


        target_score = (
            logits[
                0,
                target_index
            ]
        )


        target_score.backward()


        if (
            self.activations
            is None
            or
            self.gradients
            is None
        ):

            raise RuntimeError(
                "Grad-CAM hooks did not "
                "capture activations/gradients."
            )


        weights = (
            self.gradients
            .mean(
                dim=(
                    2,
                    3,
                ),
                keepdim=True,
            )
        )


        cam = (
            weights
            *
            self.activations
        ).sum(
            dim=1,
            keepdim=True,
        )


        cam = torch.relu(
            cam
        )


        cam = F.interpolate(
            cam,
            size=(
                224,
                224,
            ),
            mode="bilinear",
            align_corners=False,
        )


        cam = cam[
            0,
            0
        ]


        minimum = cam.min()
        maximum = cam.max()


        if (
            maximum
            >
            minimum
        ):

            cam = (
                cam
                -
                minimum
            ) / (
                maximum
                -
                minimum
            )

        else:

            cam = torch.zeros_like(
                cam
            )


        return (
            cam
            .cpu()
            .numpy()
        )


    def close(
        self,
    ):

        self.forward_handle.remove()
        self.backward_handle.remove()


def main():

    print("=" * 92)
    print(
        "BREEDVISION AI - PHASE 7 GRAD-CAM"
    )
    print("=" * 92)


    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else
        "cpu"
    )


    calibration = load_json(
        CALIBRATION_CONFIG
    )

    threshold_config = load_json(
        THRESHOLD_CONFIG
    )


    temperature = float(
        calibration[
            "temperature"
        ]
    )

    threshold = float(
        threshold_config[
            "threshold"
        ]
    )


    checkpoint = torch.load(
        WEIGHTS_PATH,
        map_location=device,
        weights_only=False,
    )


    class_to_index = (
        checkpoint[
            "class_to_index"
        ]
    )


    index_to_class = {
        index: breed

        for breed, index
        in class_to_index.items()
    }


    model = models.resnet18(
        weights=None
    )


    model.fc = nn.Linear(
        model.fc.in_features,
        len(
            class_to_index
        ),
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


    gradcam = GradCAM(
        model=
            model,

        target_layer=
            model.layer4[
                -1
            ],
    )


    input_transform = (
        build_eval_transform(
            224
        )
    )


    display_transform = (
        transforms.Compose(
            [
                transforms.Resize(
                    256
                ),

                transforms.CenterCrop(
                    224
                ),
            ]
        )
    )


    dataframe = pd.read_csv(
        MANIFEST
    )


    test = dataframe[
        dataframe[
            "split"
        ]
        ==
        "test"
    ]


    # One example per known class where available.

    selected = (
        test
        .groupby(
            "breed",
            group_keys=False,
        )
        .head(1)
        .sort_values(
            "breed"
        )
    )


    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    rows = []


    for sample_number, (
        _,
        row,
    ) in enumerate(
        selected.iterrows(),
        start=1,
    ):

        image_path = Path(
            row[
                "image_path"
            ]
        )


        with Image.open(
            image_path
        ) as image:

            image = image.convert(
                "RGB"
            )


            display_image = (
                display_transform(
                    image
                )
            )


            display_array = (
                np.asarray(
                    display_image
                )
                .astype(
                    np.float32
                )
                /
                255.0
            )


            tensor = (
                input_transform(
                    image
                )
                .unsqueeze(0)
                .to(device)
            )


        with torch.no_grad():

            raw_logits = model(
                tensor
            )


            probabilities = torch.softmax(
                raw_logits
                /
                temperature,
                dim=1,
            )


            probability, predicted = (
                probabilities.max(
                    dim=1
                )
            )


        predicted_index = int(
            predicted.item()
        )


        predicted_breed = (
            index_to_class[
                predicted_index
            ]
        )


        calibrated_probability = float(
            probability.item()
        )


        decision = (
            "unknown"
            if calibrated_probability
            <
            threshold
            else
            "known"
        )


        heatmap = gradcam.generate(
            tensor=
                tensor,

            target_index=
                predicted_index,
        )


        colormap = plt.get_cmap(
            "jet"
        )


        heatmap_rgb = (
            colormap(
                heatmap
            )[
                :,
                :,
                :3
            ]
        )


        overlay = np.clip(
            (
                0.60
                *
                display_array
            )
            +
            (
                0.40
                *
                heatmap_rgb
            ),
            0.0,
            1.0,
        )


        safe_breed = (
            str(
                row[
                    "breed"
                ]
            )
            .replace(
                " ",
                "_"
            )
        )


        output_name = (
            f"{sample_number:02d}_"
            f"{safe_breed}_gradcam.png"
        )


        output_path = (
            OUTPUT_DIR
            /
            output_name
        )


        plt.figure(
            figsize=(
                5,
                5,
            )
        )

        plt.imshow(
            overlay
        )

        plt.axis(
            "off"
        )

        plt.tight_layout(
            pad=0
        )

        plt.savefig(
            output_path,
            dpi=180,
            bbox_inches="tight",
            pad_inches=0,
        )

        plt.close()


        rows.append(
            {
                "actual_breed":
                    row[
                        "breed"
                    ],

                "predicted_breed":
                    predicted_breed,

                "decision":
                    decision,

                "calibrated_probability":
                    calibrated_probability,

                "image_path":
                    str(
                        image_path
                    ),

                "gradcam_path":
                    str(
                        output_path
                    ),
            }
        )


        print(
            f"Generated "
            f"{sample_number}/"
            f"{len(selected)}: "
            f"{row['breed']}"
        )


    gradcam.close()


    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "actual_breed",
                "predicted_breed",
                "decision",
                "calibrated_probability",
                "image_path",
                "gradcam_path",
            ],
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


    generated_files = [
        row[
            "gradcam_path"
        ]

        for row in rows
    ]


    summary = {

        "status":
            "PASS",

        "method":
            "Grad-CAM",

        "architecture":
            "resnet18",

        "target_layer":
            "layer4[-1]",

        "samples_generated":
            len(
                rows
            ),

        "expected_known_classes":
            len(
                class_to_index
            ),

        "files":
            generated_files,

        "interpretation_note":
            (
                "Grad-CAM highlights image regions that "
                "contributed to the selected model output. "
                "It does not prove causal reasoning."
            ),
    }


    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
        )


    if len(
        rows
    ) == 0:

        raise RuntimeError(
            "No Grad-CAM examples generated."
        )


    print()
    print(
        "Grad-CAM images generated:",
        len(
            rows
        )
    )


    print()
    print("=" * 92)
    print(
        "PHASE 7 GRAD-CAM: PASS"
    )
    print("=" * 92)


if __name__ == "__main__":
    main()