from pathlib import Path
import json


# =========================================================
# BREEDVISION AI
# PHASE 6.6
# CLASSIFIER V2 CLASS CONFIGURATION
# =========================================================


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

CONFIGS_DIR = (
    PROJECT_ROOT
    / "configs"
)


V1_DATASET_CONFIG = (
    CONFIGS_DIR
    / "dataset_config.json"
)

BUFFALO_CONFIG = (
    CONFIGS_DIR
    / "phase6_buffalo_final_classes.json"
)


OUTPUT_CONFIG = (
    CONFIGS_DIR
    / "classifier_v2_dataset_config.json"
)

OUTPUT_CLASS_MAP = (
    CONFIGS_DIR
    / "classifier_v2_class_to_index.json"
)

OUTPUT_SPECIES_MAP = (
    CONFIGS_DIR
    / "classifier_v2_species_mapping.json"
)


def load_json(path):

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def main():

    print("=" * 84)
    print(
        "BREEDVISION AI - CLASSIFIER V2 CONFIGURATION"
    )
    print("=" * 84)


    v1 = load_json(
        V1_DATASET_CONFIG
    )


    buffalo = load_json(
        BUFFALO_CONFIG
    )


    cattle_classes = list(
        v1[
            "cattle_classes"
        ]
    )


    buffalo_classes = list(
        buffalo[
            "final_buffalo_classes"
        ]
    )


    classes = (
        sorted(
            cattle_classes
        )
        +
        sorted(
            buffalo_classes
        )
    )


    class_to_index = {

        breed: index

        for index, breed
        in enumerate(
            classes
        )
    }


    species_mapping = {}


    for breed in cattle_classes:

        species_mapping[
            breed
        ] = "cattle"


    for breed in buffalo_classes:

        species_mapping[
            breed
        ] = "buffalo"


    config = {

        "project":
            "BreedVision AI",

        "classifier_version":
            "v2",

        "num_classes":
            len(
                classes
            ),

        "num_cattle_classes":
            len(
                cattle_classes
            ),

        "num_buffalo_classes":
            len(
                buffalo_classes
            ),

        "classes":
            classes,

        "cattle_classes":
            sorted(
                cattle_classes
            ),

        "buffalo_classes":
            sorted(
                buffalo_classes
            ),

        "class_to_index":
            class_to_index,

        "species_mapping":
            species_mapping,

        "split_policy": {
            "train": 0.70,
            "validation": 0.15,
            "test": 0.15,
        },

        "image_policy": {
            "minimum_width": 224,
            "minimum_height": 224,
            "raw_data_modified": False,
            "validation_augmentation": False,
            "test_augmentation": False,
        },

        "near_duplicate_policy":
            (
                "All members of a near-duplicate group "
                "must stay in the same split."
            ),
    }


    with OUTPUT_CONFIG.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            config,
            file,
            indent=4,
        )


    with OUTPUT_CLASS_MAP.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            class_to_index,
            file,
            indent=4,
        )


    with OUTPUT_SPECIES_MAP.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            species_mapping,
            file,
            indent=4,
        )


    print()
    print(
        "Cattle classes :",
        len(
            cattle_classes
        )
    )

    print(
        "Buffalo classes:",
        len(
            buffalo_classes
        )
    )

    print(
        "Total classes  :",
        len(
            classes
        )
    )


    print()
    print("Classes:")


    for breed, index in (
        class_to_index.items()
    ):

        print(
            f"  {index:>2} -> "
            f"{breed:<20} "
            f"({species_mapping[breed]})"
        )


    print()
    print("=" * 84)
    print(
        "CLASSIFIER V2 CONFIG STATUS: PASS"
    )
    print("=" * 84)


if __name__ == "__main__":

    main()