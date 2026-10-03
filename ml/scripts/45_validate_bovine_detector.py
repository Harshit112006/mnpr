import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

import pandas as pd
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MANIFEST_PATH = (
    PROJECT_ROOT
    / "reports"
    / "classifier_v2_final_manifest.csv"
)

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)

CONFIGS_DIR = (
    PROJECT_ROOT
    / "configs"
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--per-species",
        type=int,
        default=60,
    )

    parser.add_argument(
        "--conf",
        type=float,
        default=0.20,
    )

    args = parser.parse_args()

    print("=" * 88)
    print(
        "BREEDVISION AI - BOVINE DETECTOR BASELINE"
    )
    print("=" * 88)

    dataframe = pd.read_csv(
        MANIFEST_PATH
    )

    validation = dataframe[
        dataframe[
            "split"
        ]
        ==
        "validation"
    ].copy()

    random.seed(42)

    selected_rows = []

    for species in [
        "cattle",
        "buffalo",
    ]:

        subset = validation[
            validation[
                "species"
            ]
            ==
            species
        ]

        count = min(
            args.per_species,
            len(subset),
        )

        sampled = subset.sample(
            n=count,
            random_state=42,
        )

        selected_rows.extend(
            sampled.to_dict(
                "records"
            )
        )

    print()
    print(
        "Images selected:",
        len(
            selected_rows
        )
    )

    print(
        "Loading YOLOv8n..."
    )

    model = YOLO(
        "yolov8n.pt"
    )

    names = model.names

    cow_class_id = None

    for class_id, name in names.items():

        if str(name).lower() == "cow":
            cow_class_id = int(
                class_id
            )
            break

    if cow_class_id is None:

        raise RuntimeError(
            "COCO cow class not found "
            "in detector."
        )

    print(
        "Cow class ID:",
        cow_class_id
    )

    results_rows = []

    species_stats = defaultdict(
        lambda: {
            "total": 0,
            "detected": 0,
        }
    )

    for index, row in enumerate(
        selected_rows,
        start=1,
    ):

        image_path = (
            row[
                "image_path"
            ]
        )

        species = (
            row[
                "species"
            ]
        )

        breed = (
            row[
                "breed"
            ]
        )

        prediction = model.predict(
            source=image_path,
            conf=args.conf,
            imgsz=640,
            device="cpu",
            verbose=False,
        )[0]

        detected = False
        best_score = 0.0

        boxes = prediction.boxes

        if boxes is not None:

            classes = (
                boxes.cls
                .cpu()
                .tolist()
            )

            scores = (
                boxes.conf
                .cpu()
                .tolist()
            )

            for class_value, score in zip(
                classes,
                scores,
            ):

                if (
                    int(class_value)
                    ==
                    cow_class_id
                ):

                    detected = True

                    best_score = max(
                        best_score,
                        float(score),
                    )

        species_stats[
            species
        ][
            "total"
        ] += 1

        if detected:

            species_stats[
                species
            ][
                "detected"
            ] += 1

        results_rows.append(
            {
                "image_path":
                    image_path,

                "species":
                    species,

                "breed":
                    breed,

                "bovine_detected":
                    detected,

                "detector_score":
                    best_score,
            }
        )

        if (
            index % 20 == 0
            or
            index
            ==
            len(
                selected_rows
            )
        ):

            print(
                f"Processed "
                f"{index}/"
                f"{len(selected_rows)}"
            )

    summary_by_species = {}

    for species in [
        "cattle",
        "buffalo",
    ]:

        total = (
            species_stats[
                species
            ][
                "total"
            ]
        )

        detected = (
            species_stats[
                species
            ][
                "detected"
            ]
        )

        coverage = (
            detected / total
            if total
            else 0.0
        )

        summary_by_species[
            species
        ] = {
            "total":
                total,

            "detected":
                detected,

            "detection_coverage":
                coverage,
        }

    csv_path = (
        REPORTS_DIR
        / "bovine_detector_validation.csv"
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
                "species",
                "breed",
                "bovine_detected",
                "detector_score",
            ],
        )

        writer.writeheader()
        writer.writerows(
            results_rows
        )

    report = {
        "detector":
            "yolov8n",

        "source_training":
            "COCO pretrained",

        "target_coco_class":
            "cow",

        "target_class_id":
            cow_class_id,

        "confidence_threshold":
            args.conf,

        "evaluation_type":
            (
                "presence coverage on known "
                "bovine validation images; "
                "not bounding-box mAP"
            ),

        "species_summary":
            summary_by_species,

        "important_limitation":
            (
                "COCO has a cow class but no "
                "dedicated buffalo class. "
                "Buffalo coverage is therefore "
                "a generalization/proxy measurement."
            ),
    }

    json_path = (
        REPORTS_DIR
        / "bovine_detector_validation.json"
    )

    with json_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
        )

    detector_config = {
        "detector_version":
            "bovine-detector-v1",

        "architecture":
            "yolov8n",

        "weights":
            "yolov8n.pt",

        "target_class":
            "cow",

        "target_class_id":
            cow_class_id,

        "confidence_threshold":
            args.conf,

        "buffalo_limitation":
            (
                "Buffalo is not a dedicated COCO "
                "class; detector behavior on buffalo "
                "is proxy generalization."
            ),
    }

    with (
        CONFIGS_DIR
        / "bovine_detector_v1.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            detector_config,
            file,
            indent=4,
        )

    print()

    for species, info in (
        summary_by_species.items()
    ):

        print(
            species,
            "=>",
            f"{info['detected']}/"
            f"{info['total']}",
            "coverage:",
            round(
                info[
                    "detection_coverage"
                ],
                4,
            ),
        )

    print()
    print("=" * 88)
    print(
        "BOVINE DETECTOR VALIDATION: COMPLETE"
    )
    print("=" * 88)


if __name__ == "__main__":
    main()