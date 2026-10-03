import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from training.dataset_v2 import build_eval_transform


MANIFEST_PATH = (
    PROJECT_ROOT
    / "reports"
    / "classifier_v2_final_manifest.csv"
)

CLASSIFIER_WEIGHT = (
    PROJECT_ROOT
    / "weights"
    / "breed_classifier_v2.pth"
)

CLASSIFIER_CONFIG = (
    PROJECT_ROOT
    / "configs"
    / "breed_classifier_v2.json"
)

SPECIES_MAP = (
    PROJECT_ROOT
    / "configs"
    / "classifier_v2_species_mapping.json"
)

DETECTOR_CONFIG = (
    PROJECT_ROOT
    / "configs"
    / "bovine_detector_v1.json"
)

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)


def load_json(path):

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():

    print("=" * 88)
    print(
        "BREEDVISION AI - DETECTOR + CLASSIFIER PIPELINE"
    )
    print("=" * 88)

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else
        "cpu"
    )

    classifier_config = load_json(
        CLASSIFIER_CONFIG
    )

    species_mapping = load_json(
        SPECIES_MAP
    )

    detector_config = load_json(
        DETECTOR_CONFIG
    )

    checkpoint = torch.load(
        CLASSIFIER_WEIGHT,
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

    classifier = models.resnet18(
        weights=None
    )

    classifier.fc = nn.Linear(
        classifier.fc.in_features,
        len(
            class_to_index
        ),
    )

    classifier.load_state_dict(
        checkpoint[
            "model_state_dict"
        ]
    )

    classifier = classifier.to(
        device
    )

    classifier.eval()

    transform = build_eval_transform(
        224
    )

    detector = YOLO(
        detector_config[
            "weights"
        ]
    )

    target_class = int(
        detector_config[
            "target_class_id"
        ]
    )

    conf_threshold = float(
        detector_config[
            "confidence_threshold"
        ]
    )

    dataframe = pd.read_csv(
        MANIFEST_PATH
    )

    test = dataframe[
        dataframe[
            "split"
        ]
        ==
        "test"
    ]

    samples = []

    for species in [
        "cattle",
        "buffalo",
    ]:

        subset = test[
            test[
                "species"
            ]
            ==
            species
        ]

        count = min(
            10,
            len(subset),
        )

        samples.extend(
            subset.sample(
                n=count,
                random_state=42,
            ).to_dict(
                "records"
            )
        )

    output_rows = []

    species_stats = defaultdict(
        lambda: {
            "attempted": 0,
            "detected": 0,
            "classified": 0,
        }
    )

    for index, row in enumerate(
        samples,
        start=1,
    ):

        image_path = Path(
            row[
                "image_path"
            ]
        )

        true_species = (
            row[
                "species"
            ]
        )

        species_stats[
            true_species
        ][
            "attempted"
        ] += 1

        prediction = detector.predict(
            source=str(
                image_path
            ),
            conf=conf_threshold,
            imgsz=640,
            device="cpu",
            verbose=False,
        )[0]

        best_box = None
        best_conf = -1.0

        if prediction.boxes is not None:

            for box in prediction.boxes:

                class_id = int(
                    box.cls.item()
                )

                score = float(
                    box.conf.item()
                )

                if (
                    class_id
                    ==
                    target_class
                    and
                    score
                    >
                    best_conf
                ):

                    best_conf = score

                    best_box = (
                        box.xyxy[
                            0
                        ]
                        .cpu()
                        .tolist()
                    )

        if best_box is None:

            output_rows.append(
                {
                    "image_path":
                        str(
                            image_path
                        ),

                    "actual_breed":
                        row[
                            "breed"
                        ],

                    "actual_species":
                        true_species,

                    "bovine_detected":
                        False,

                    "detector_score":
                        0.0,

                    "predicted_breed":
                        "",

                    "predicted_species":
                        "",

                    "softmax_score":
                        "",
                }
            )

            continue

        species_stats[
            true_species
        ][
            "detected"
        ] += 1

        with Image.open(
            image_path
        ) as image:

            image = image.convert(
                "RGB"
            )

            width, height = image.size

            x1, y1, x2, y2 = (
                best_box
            )

            x1 = max(
                0,
                int(x1),
            )

            y1 = max(
                0,
                int(y1),
            )

            x2 = min(
                width,
                int(x2),
            )

            y2 = min(
                height,
                int(y2),
            )

            crop = image.crop(
                (
                    x1,
                    y1,
                    x2,
                    y2,
                )
            )

            tensor = (
                transform(
                    crop
                )
                .unsqueeze(0)
                .to(device)
            )

        with torch.no_grad():

            logits = classifier(
                tensor
            )

            probabilities = (
                torch.softmax(
                    logits,
                    dim=1,
                )
            )

            score, predicted = (
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

        predicted_species = (
            species_mapping[
                predicted_breed
            ]
        )

        species_stats[
            true_species
        ][
            "classified"
        ] += 1

        output_rows.append(
            {
                "image_path":
                    str(
                        image_path
                    ),

                "actual_breed":
                    row[
                        "breed"
                    ],

                "actual_species":
                    true_species,

                "bovine_detected":
                    True,

                "detector_score":
                    best_conf,

                "predicted_breed":
                    predicted_breed,

                "predicted_species":
                    predicted_species,

                "softmax_score":
                    float(
                        score.item()
                    ),
            }
        )

        print(
            f"Processed "
            f"{index}/"
            f"{len(samples)}"
        )

    csv_path = (
        REPORTS_DIR
        / "bovine_classifier_pipeline_smoke.csv"
    )

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "image_path",
                "actual_breed",
                "actual_species",
                "bovine_detected",
                "detector_score",
                "predicted_breed",
                "predicted_species",
                "softmax_score",
            ],
        )

        writer.writeheader()
        writer.writerows(
            output_rows
        )

    summary = {
        "pipeline":
            "bovine detector -> crop -> breed classifier v2",

        "samples":
            len(
                output_rows
            ),

        "species_summary": {
            species:
                dict(
                    values
                )
            for species, values
            in species_stats.items()
        },

        "important_note":
            (
                "Classifier softmax scores are "
                "uncalibrated. Confidence calibration "
                "and unknown handling belong to Phase 7."
            ),
    }

    json_path = (
        REPORTS_DIR
        / "bovine_classifier_pipeline_smoke.json"
    )

    with json_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
        )

    print()
    print(
        json.dumps(
            summary[
                "species_summary"
            ],
            indent=2,
        )
    )

    print()
    print("=" * 88)
    print(
        "BOVINE CLASSIFIER PIPELINE: PASS"
    )
    print("=" * 88)


if __name__ == "__main__":
    main()