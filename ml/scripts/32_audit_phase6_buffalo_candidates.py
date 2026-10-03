from pathlib import Path
import csv
import json
from collections import Counter, defaultdict

from PIL import Image, UnidentifiedImageError


# =========================================================
# BREEDVISION AI
# PHASE 6.1
# BUFFALO CANDIDATE DATASET AUDIT
# =========================================================


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


RAW_ROOT = (
    PROJECT_ROOT
    / "data"
    / "raw"
)


REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)


OUTPUT_CSV = (
    REPORTS_DIR
    / "phase6_buffalo_candidate_inventory.csv"
)


OUTPUT_JSON = (
    REPORTS_DIR
    / "phase6_buffalo_candidate_summary.json"
)


# =========================================================
# CANDIDATE BREEDS
#
# These are candidates only.
# They are NOT automatically accepted into classifier v2.
# =========================================================


BUFFALO_ALIASES = {

    "Murrah": {
        "murrah",
    },

    "Jaffarabadi": {
        "jaffarabadi",
        "jaffarabad",
        "jaffrabadi",
    },

    "Mehsana": {
        "mehsana",
        "mehsani",
    },

    "Surti": {
        "surti",
    },

    "Banni": {
        "banni",
    },
}


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
}


MIN_WIDTH = 224
MIN_HEIGHT = 224


# =========================================================
# HELPERS
# =========================================================


def normalize_text(value):

    return (
        str(value)
        .lower()
        .replace("-", "")
        .replace("_", "")
        .replace(" ", "")
    )


NORMALIZED_ALIASES = {

    breed: {
        normalize_text(alias)
        for alias in aliases
    }

    for breed, aliases
    in BUFFALO_ALIASES.items()
}


def detect_breed_from_path(path):

    relative_parts = (
        path.relative_to(
            RAW_ROOT
        )
        .parts
    )


    normalized_parts = [
        normalize_text(part)
        for part in relative_parts
    ]


    for breed, aliases in (
        NORMALIZED_ALIASES.items()
    ):

        for part in normalized_parts:

            if part in aliases:

                return breed


    return None


def detect_source(path):

    try:

        relative = (
            path.relative_to(
                RAW_ROOT
            )
        )

        if relative.parts:

            return relative.parts[0]

    except ValueError:
        pass


    return "unknown"


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 84)
    print(
        "BREEDVISION AI - PHASE 6 BUFFALO CANDIDATE AUDIT"
    )
    print("=" * 84)


    if not RAW_ROOT.exists():

        raise FileNotFoundError(
            f"Raw dataset directory not found:\n"
            f"{RAW_ROOT}"
        )


    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    rows = []


    breed_total = Counter()

    breed_readable = Counter()

    breed_min_size_pass = Counter()

    breed_corrupt = Counter()

    breed_too_small = Counter()

    source_counts = defaultdict(
        Counter
    )


    all_image_files = [
        path

        for path in RAW_ROOT.rglob("*")

        if (
            path.is_file()
            and
            path.suffix.lower()
            in IMAGE_EXTENSIONS
        )
    ]


    print()
    print(
        "Total raw image files:",
        len(
            all_image_files
        )
    )


    matched_files = 0


    # =====================================================
    # SCAN
    # =====================================================


    for image_path in all_image_files:

        breed = detect_breed_from_path(
            image_path
        )


        if breed is None:

            continue


        matched_files += 1


        source = detect_source(
            image_path
        )


        breed_total[
            breed
        ] += 1


        source_counts[
            source
        ][
            breed
        ] += 1


        readable = False

        width = None
        height = None

        size_pass = False

        error = ""


        try:

            with Image.open(
                image_path
            ) as image:

                image.load()

                width, height = (
                    image.size
                )


                readable = True


                breed_readable[
                    breed
                ] += 1


                if (
                    width >= MIN_WIDTH
                    and
                    height >= MIN_HEIGHT
                ):

                    size_pass = True

                    breed_min_size_pass[
                        breed
                    ] += 1

                else:

                    breed_too_small[
                        breed
                    ] += 1


        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
        ) as exc:

            breed_corrupt[
                breed
            ] += 1

            error = str(
                exc
            )


        rows.append(
            {
                "source_dataset":
                    source,

                "candidate_breed":
                    breed,

                "image_path":
                    str(
                        image_path.resolve()
                    ),

                "readable":
                    readable,

                "width":
                    width,

                "height":
                    height,

                "minimum_size_pass":
                    size_pass,

                "error":
                    error,
            }
        )


    # =====================================================
    # WRITE CSV
    # =====================================================


    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "source_dataset",
                "candidate_breed",
                "image_path",
                "readable",
                "width",
                "height",
                "minimum_size_pass",
                "error",
            ],
        )


        writer.writeheader()

        writer.writerows(
            rows
        )


    # =====================================================
    # SUMMARY
    # =====================================================


    breed_summary = {}


    for breed in BUFFALO_ALIASES:

        usable = (
            breed_min_size_pass[
                breed
            ]
        )


        if usable >= 500:

            strength = "strong"

        elif usable >= 200:

            strength = "usable"

        elif usable >= 100:

            strength = "weak"

        else:

            strength = "insufficient"


        breed_summary[
            breed
        ] = {

            "total_detected":
                breed_total[
                    breed
                ],

            "readable":
                breed_readable[
                    breed
                ],

            "minimum_size_pass":
                usable,

            "too_small":
                breed_too_small[
                    breed
                ],

            "corrupt":
                breed_corrupt[
                    breed
                ],

            "data_strength":
                strength,
        }


    summary = {

        "phase":
            "Phase 6 - Buffalo Expansion",

        "raw_root":
            str(
                RAW_ROOT.resolve()
            ),

        "candidate_breeds":
            list(
                BUFFALO_ALIASES.keys()
            ),

        "minimum_dimensions": {
            "width":
                MIN_WIDTH,

            "height":
                MIN_HEIGHT,
        },

        "total_raw_images_scanned":
            len(
                all_image_files
            ),

        "matched_buffalo_images":
            matched_files,

        "breed_summary":
            breed_summary,

        "source_distribution": {

            source:
                dict(
                    counts
                )

            for source, counts
            in source_counts.items()
        },

        "policy": (
            "This audit does not automatically include any "
            "buffalo breed in classifier v2. Final inclusion "
            "requires enough real, readable, audited images."
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


    # =====================================================
    # TERMINAL OUTPUT
    # =====================================================


    print()
    print("-" * 84)
    print("BUFFALO CANDIDATE COUNTS")
    print("-" * 84)


    print(
        f"{'Breed':<20}"
        f"{'Detected':>12}"
        f"{'Readable':>12}"
        f"{'>=224':>12}"
        f"{'Strength':>15}"
    )


    for breed in BUFFALO_ALIASES:

        info = (
            breed_summary[
                breed
            ]
        )


        print(
            f"{breed:<20}"
            f"{info['total_detected']:>12}"
            f"{info['readable']:>12}"
            f"{info['minimum_size_pass']:>12}"
            f"{info['data_strength']:>15}"
        )


    print()
    print(
        "Matched buffalo images:",
        matched_files
    )


    print()
    print(
        "CSV report:"
    )

    print(
        OUTPUT_CSV
    )


    print()
    print(
        "JSON summary:"
    )

    print(
        OUTPUT_JSON
    )


    print()
    print("=" * 84)
    print(
        "PHASE 6.1 BUFFALO AUDIT: COMPLETE"
    )
    print("=" * 84)


if __name__ == "__main__":

    main()