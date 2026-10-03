from pathlib import Path
import csv
import json
from collections import Counter, defaultdict


# =========================================================
# BREEDVISION AI
# PHASE 5 - TRAINING MANIFEST VALIDATION
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CONFIG_PATH = (
    PROJECT_ROOT
    / "configs"
    / "training_config.json"
)


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():

    print("=" * 80)
    print("BREEDVISION AI - TRAINING MANIFEST VALIDATION")
    print("=" * 80)


    config = load_json(
        CONFIG_PATH
    )


    manifest_path = (
        PROJECT_ROOT
        / config["dataset"]["manifest"]
    )


    class_map_path = (
        PROJECT_ROOT
        / config["dataset"]["class_to_index"]
    )


    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Dataset manifest not found:\n"
            f"{manifest_path}"
        )


    class_to_index = load_json(
        class_map_path
    )


    # =====================================================
    # READ MANIFEST
    # =====================================================

    with manifest_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        rows = list(
            csv.DictReader(file)
        )


    print()
    print(
        "Manifest rows:",
        len(rows)
    )

    print(
        "Configured classes:",
        len(class_to_index)
    )


    # =====================================================
    # VALIDATION VARIABLES
    # =====================================================

    errors = []

    split_counts = Counter()

    breed_counts = Counter()

    class_split_counts = defaultdict(
        Counter
    )

    seen_paths = set()

    missing_files = []

    duplicate_paths = []

    invalid_breeds = []

    invalid_indexes = []

    invalid_splits = []


    valid_splits = {
        "train",
        "validation",
        "test",
    }


    # =====================================================
    # VALIDATE EACH ROW
    # =====================================================

    for row in rows:

        image_path = Path(
            row["image_path"]
        )


        breed = (
            row["breed"]
            .strip()
        )


        split = (
            row["split"]
            .strip()
        )


        try:
            class_index = int(
                row["class_index"]
            )

        except ValueError:

            errors.append(
                f"Invalid class index for: {image_path}"
            )

            continue


        # ---------------------------------------------
        # File exists
        # ---------------------------------------------

        if not image_path.exists():

            missing_files.append(
                str(image_path)
            )


        # ---------------------------------------------
        # Duplicate manifest path
        # ---------------------------------------------

        resolved = str(
            image_path.resolve()
        )


        if resolved in seen_paths:

            duplicate_paths.append(
                resolved
            )

        else:

            seen_paths.add(
                resolved
            )


        # ---------------------------------------------
        # Breed validity
        # ---------------------------------------------

        if breed not in class_to_index:

            invalid_breeds.append(
                breed
            )

        else:

            expected_index = (
                class_to_index[
                    breed
                ]
            )


            if class_index != expected_index:

                invalid_indexes.append(
                    {
                        "breed":
                            breed,

                        "found":
                            class_index,

                        "expected":
                            expected_index,
                    }
                )


        # ---------------------------------------------
        # Split validity
        # ---------------------------------------------

        if split not in valid_splits:

            invalid_splits.append(
                split
            )


        split_counts[
            split
        ] += 1

        breed_counts[
            breed
        ] += 1

        class_split_counts[
            breed
        ][
            split
        ] += 1


    # =====================================================
    # CHECK EVERY CLASS IN EVERY SPLIT
    # =====================================================

    missing_class_splits = []


    for breed in class_to_index:

        for split in valid_splits:

            if (
                class_split_counts[
                    breed
                ][
                    split
                ]
                == 0
            ):

                missing_class_splits.append(
                    f"{breed} -> {split}"
                )


    # =====================================================
    # REGISTER ERRORS
    # =====================================================

    if missing_files:

        errors.append(
            f"{len(missing_files)} image files are missing."
        )


    if duplicate_paths:

        errors.append(
            f"{len(duplicate_paths)} duplicate image paths found."
        )


    if invalid_breeds:

        errors.append(
            f"{len(invalid_breeds)} invalid breed labels found."
        )


    if invalid_indexes:

        errors.append(
            f"{len(invalid_indexes)} class-index mismatches found."
        )


    if invalid_splits:

        errors.append(
            f"{len(invalid_splits)} invalid split values found."
        )


    if missing_class_splits:

        errors.append(
            "One or more classes are missing from "
            "train/validation/test."
        )


    # =====================================================
    # DISPLAY DATASET DISTRIBUTION
    # =====================================================

    print()
    print("-" * 80)
    print("SPLIT COUNTS")
    print("-" * 80)


    total_images = len(rows)


    for split in [
        "train",
        "validation",
        "test",
    ]:

        count = (
            split_counts[
                split
            ]
        )


        percentage = (
            count
            /
            max(
                total_images,
                1,
            )
            *
            100
        )


        print(
            f"{split:<12}: "
            f"{count:<8} "
            f"({percentage:.2f}%)"
        )


    print()
    print("-" * 80)
    print("CLASS COUNTS")
    print("-" * 80)


    for breed, index in sorted(
        class_to_index.items(),
        key=lambda item:
        item[1],
    ):

        print(
            f"[{index}] "
            f"{breed:<20} "
            f"{breed_counts[breed]}"
        )


    print()
    print("-" * 80)
    print("CLASS-WISE SPLIT DISTRIBUTION")
    print("-" * 80)


    print(
        f"{'Breed':<20}"
        f"{'Train':>10}"
        f"{'Validation':>14}"
        f"{'Test':>10}"
    )


    for breed in sorted(
        class_to_index,
        key=lambda breed:
        class_to_index[
            breed
        ],
    ):

        counts = (
            class_split_counts[
                breed
            ]
        )


        print(
            f"{breed:<20}"
            f"{counts['train']:>10}"
            f"{counts['validation']:>14}"
            f"{counts['test']:>10}"
        )


    # =====================================================
    # CLASS IMBALANCE
    # =====================================================

    if breed_counts:

        largest_class = max(
            breed_counts.values()
        )

        smallest_class = min(
            breed_counts.values()
        )


        imbalance_ratio = (
            largest_class
            /
            max(
                smallest_class,
                1,
            )
        )


    else:

        imbalance_ratio = 0


    print()
    print(
        "Largest / smallest class ratio:",
        round(
            imbalance_ratio,
            2,
        )
    )


    # =====================================================
    # FINAL RESULT
    # =====================================================

    print()
    print("=" * 80)


    if errors:

        print(
            "TRAINING MANIFEST STATUS: FAIL"
        )

        print("=" * 80)

        print()

        for error in errors:

            print(
                "[ERROR]",
                error
            )


    else:

        print(
            "TRAINING MANIFEST STATUS: PASS"
        )

        print("=" * 80)

        print()

        print(
            "Dataset is ready for PyTorch DataLoader construction."
        )


    print()

    print(
        "Missing files      :",
        len(missing_files)
    )

    print(
        "Duplicate paths    :",
        len(duplicate_paths)
    )

    print(
        "Invalid breeds     :",
        len(invalid_breeds)
    )

    print(
        "Index mismatches   :",
        len(invalid_indexes)
    )

    print(
        "Invalid splits     :",
        len(invalid_splits)
    )

    print(
        "Missing class/split:",
        len(missing_class_splits)
    )


if __name__ == "__main__":
    main()