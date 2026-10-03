import csv
import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from torchvision import models


# =========================================================
# PATH SETUP
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


from training.dataset_v2 import (
    create_v2_dataloaders
)


# =========================================================
# PATHS
# =========================================================


WEIGHTS_PATH = (
    PROJECT_ROOT
    / "weights"
    / "breed_classifier_v2.pth"
)


OUTPUT_NPZ = (
    PROJECT_ROOT
    / "phase7"
    / "cache"
    / "validation_logits.npz"
)


OUTPUT_CSV = (
    PROJECT_ROOT
    / "reports"
    / "phase7_validation_predictions_raw.csv"
)


OUTPUT_JSON = (
    PROJECT_ROOT
    / "reports"
    / "phase7_validation_logits_summary.json"
)


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 90)
    print(
        "BREEDVISION AI - PHASE 7 VALIDATION LOGITS"
    )
    print("=" * 90)


    if not WEIGHTS_PATH.exists():

        raise FileNotFoundError(
            f"Classifier weight missing:\n"
            f"{WEIGHTS_PATH}"
        )


    device = (
        torch.device("cuda")
        if torch.cuda.is_available()
        else torch.device("cpu")
    )


    print()
    print(
        "Device:",
        device
    )


    # =====================================================
    # DATA
    # =====================================================


    data = create_v2_dataloaders()


    validation_loader = (
        data[
            "validation_loader"
        ]
    )


    class_to_index = (
        data[
            "class_to_index"
        ]
    )


    num_classes = (
        data[
            "num_classes"
        ]
    )


    index_to_class = {

        index: breed

        for breed, index
        in class_to_index.items()
    }


    print(
        "Validation images:",
        len(
            validation_loader.dataset
        )
    )


    print(
        "Classes:",
        num_classes
    )


    # =====================================================
    # LOAD CHECKPOINT
    # =====================================================


    checkpoint = torch.load(
        WEIGHTS_PATH,
        map_location=device,
        weights_only=False,
    )


    checkpoint_class_map = (
        checkpoint[
            "class_to_index"
        ]
    )


    if (
        checkpoint_class_map
        !=
        class_to_index
    ):

        raise RuntimeError(
            "Checkpoint class mapping does not match "
            "classifier-v2 dataset mapping."
        )


    # =====================================================
    # MODEL
    # =====================================================


    model = models.resnet18(
        weights=None
    )


    model.fc = nn.Linear(
        model.fc.in_features,
        num_classes,
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


    # =====================================================
    # COLLECT LOGITS
    # =====================================================


    all_logits = []
    all_labels = []
    all_paths = []

    csv_rows = []


    print()
    print(
        "Collecting validation logits..."
    )


    with torch.no_grad():

        for batch_index, batch in enumerate(
            validation_loader,
            start=1,
        ):

            images = (
                batch[
                    "image"
                ]
                .to(device)
            )


            labels = (
                batch[
                    "label"
                ]
                .to(device)
            )


            logits = model(
                images
            )


            probabilities = torch.softmax(
                logits,
                dim=1,
            )


            top_scores, top_indices = (
                probabilities.topk(
                    k=min(
                        3,
                        num_classes,
                    ),
                    dim=1,
                )
            )


            all_logits.append(
                logits
                .cpu()
                .numpy()
            )


            all_labels.append(
                labels
                .cpu()
                .numpy()
            )


            all_paths.extend(
                batch[
                    "image_path"
                ]
            )


            for sample_index in range(
                images.size(0)
            ):

                actual_index = int(
                    labels[
                        sample_index
                    ].item()
                )


                top_indices_list = (
                    top_indices[
                        sample_index
                    ]
                    .cpu()
                    .tolist()
                )


                top_scores_list = (
                    top_scores[
                        sample_index
                    ]
                    .cpu()
                    .tolist()
                )


                row = {

                    "image_path":
                        batch[
                            "image_path"
                        ][
                            sample_index
                        ],

                    "actual_index":
                        actual_index,

                    "actual_breed":
                        index_to_class[
                            actual_index
                        ],

                    "top1_index":
                        top_indices_list[
                            0
                        ],

                    "top1_breed":
                        index_to_class[
                            top_indices_list[
                                0
                            ]
                        ],

                    "top1_raw_softmax":
                        top_scores_list[
                            0
                        ],

                    "correct":
                        (
                            top_indices_list[
                                0
                            ]
                            ==
                            actual_index
                        ),
                }


                for rank in range(
                    1,
                    len(
                        top_indices_list
                    )
                    +
                    1,
                ):

                    class_index = (
                        top_indices_list[
                            rank
                            -
                            1
                        ]
                    )


                    score = (
                        top_scores_list[
                            rank
                            -
                            1
                        ]
                    )


                    row[
                        f"top{rank}_breed"
                    ] = (
                        index_to_class[
                            class_index
                        ]
                    )


                    row[
                        f"top{rank}_raw_softmax"
                    ] = (
                        score
                    )


                csv_rows.append(
                    row
                )


            if (
                batch_index % 20 == 0
                or
                batch_index
                ==
                len(
                    validation_loader
                )
            ):

                print(
                    f"Processed "
                    f"{batch_index}/"
                    f"{len(validation_loader)} "
                    f"batches"
                )


    logits_array = np.concatenate(
        all_logits,
        axis=0,
    )


    labels_array = np.concatenate(
        all_labels,
        axis=0,
    )


    # =====================================================
    # SANITY CHECKS
    # =====================================================


    if (
        logits_array.shape[
            0
        ]
        !=
        labels_array.shape[
            0
        ]
    ):

        raise RuntimeError(
            "Logit/label sample count mismatch."
        )


    if (
        logits_array.shape[
            1
        ]
        !=
        num_classes
    ):

        raise RuntimeError(
            "Logit class dimension mismatch."
        )


    if not np.isfinite(
        logits_array
    ).all():

        raise RuntimeError(
            "Non-finite logits detected."
        )


    # =====================================================
    # SAVE NPZ
    # =====================================================


    OUTPUT_NPZ.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    np.savez_compressed(
        OUTPUT_NPZ,
        logits=
            logits_array,

        labels=
            labels_array,

        image_paths=
            np.array(
                all_paths,
                dtype=str,
            ),
    )


    # =====================================================
    # SAVE CSV
    # =====================================================


    fieldnames = list(
        csv_rows[
            0
        ].keys()
    )


    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=
                fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            csv_rows
        )


    # =====================================================
    # SUMMARY
    # =====================================================


    correct = sum(

        1

        for row in csv_rows

        if row[
            "correct"
        ]
    )


    raw_accuracy = (
        correct
        /
        len(
            csv_rows
        )
    )


    summary = {

        "phase":
            "Phase 7 - Validation Logit Collection",

        "classifier_version":
            "v2",

        "split":
            "validation",

        "samples":
            len(
                labels_array
            ),

        "num_classes":
            num_classes,

        "logit_shape":
            list(
                logits_array.shape
            ),

        "raw_validation_accuracy":
            raw_accuracy,

        "output_npz":
            str(
                OUTPUT_NPZ
            ),

        "raw_softmax_note":
            (
                "These softmax scores are uncalibrated "
                "and must not yet be interpreted as "
                "reliable confidence values."
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


    print()
    print(
        "Logit shape:",
        logits_array.shape
    )

    print(
        "Label shape:",
        labels_array.shape
    )

    print(
        "Raw validation accuracy:",
        round(
            raw_accuracy,
            4,
        )
    )


    print()
    print("=" * 90)
    print(
        "PHASE 7 VALIDATION LOGITS: PASS"
    )
    print("=" * 90)


if __name__ == "__main__":

    main()