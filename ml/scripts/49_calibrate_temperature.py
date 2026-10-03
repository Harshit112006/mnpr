import json
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from scipy.optimize import minimize_scalar


# =========================================================
# BREEDVISION AI
# PHASE 7
# TEMPERATURE SCALING + CALIBRATION METRICS
#
# IMPORTANT:
# - Uses VALIDATION logits only.
# - Does NOT use test data.
# - Temperature is selected by validation NLL.
# =========================================================


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


INPUT_NPZ = (
    PROJECT_ROOT
    / "phase7"
    / "cache"
    / "validation_logits.npz"
)


PHASE7_CONFIG = (
    PROJECT_ROOT
    / "configs"
    / "phase7_config.json"
)


OUTPUT_CALIBRATION_CONFIG = (
    PROJECT_ROOT
    / "configs"
    / "phase7_calibration.json"
)


OUTPUT_METRICS = (
    PROJECT_ROOT
    / "reports"
    / "phase7_calibration_metrics.json"
)


OUTPUT_NPZ = (
    PROJECT_ROOT
    / "phase7"
    / "cache"
    / "validation_calibrated.npz"
)


# =========================================================
# HELPERS
# =========================================================


def load_json(path):

    if not path.exists():

        raise FileNotFoundError(
            f"Required JSON missing:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def negative_log_likelihood(
    logits,
    labels,
    temperature,
):

    scaled_logits = (
        logits
        /
        temperature
    )

    loss = F.cross_entropy(
        scaled_logits,
        labels,
    )

    return float(
        loss.item()
    )


def softmax_numpy(
    logits,
):

    shifted = (
        logits
        -
        np.max(
            logits,
            axis=1,
            keepdims=True,
        )
    )

    exp_values = np.exp(
        shifted
    )

    return (
        exp_values
        /
        np.sum(
            exp_values,
            axis=1,
            keepdims=True,
        )
    )


def expected_calibration_error(
    probabilities,
    labels,
    num_bins=15,
):

    confidences = np.max(
        probabilities,
        axis=1,
    )

    predictions = np.argmax(
        probabilities,
        axis=1,
    )

    correctness = (
        predictions
        ==
        labels
    ).astype(
        np.float64
    )


    bin_boundaries = np.linspace(
        0.0,
        1.0,
        num_bins + 1,
    )


    ece = 0.0

    bins = []


    for index in range(
        num_bins
    ):

        lower = (
            bin_boundaries[
                index
            ]
        )

        upper = (
            bin_boundaries[
                index + 1
            ]
        )


        if index == 0:

            mask = (
                confidences
                >=
                lower
            ) & (
                confidences
                <=
                upper
            )

        else:

            mask = (
                confidences
                >
                lower
            ) & (
                confidences
                <=
                upper
            )


        count = int(
            np.sum(
                mask
            )
        )


        if count == 0:

            bins.append(
                {
                    "bin":
                        index + 1,

                    "lower":
                        float(
                            lower
                        ),

                    "upper":
                        float(
                            upper
                        ),

                    "count":
                        0,

                    "accuracy":
                        None,

                    "mean_confidence":
                        None,
                }
            )

            continue


        bin_accuracy = float(
            np.mean(
                correctness[
                    mask
                ]
            )
        )


        bin_confidence = float(
            np.mean(
                confidences[
                    mask
                ]
            )
        )


        weight = (
            count
            /
            len(
                labels
            )
        )


        ece += (
            weight
            *
            abs(
                bin_accuracy
                -
                bin_confidence
            )
        )


        bins.append(
            {
                "bin":
                    index + 1,

                "lower":
                    float(
                        lower
                    ),

                "upper":
                    float(
                        upper
                    ),

                "count":
                    count,

                "accuracy":
                    bin_accuracy,

                "mean_confidence":
                    bin_confidence,
            }
        )


    return (
        float(
            ece
        ),
        bins,
    )


def multiclass_brier_score(
    probabilities,
    labels,
    num_classes,
):

    one_hot = np.zeros(
        (
            len(
                labels
            ),
            num_classes,
        ),
        dtype=np.float64,
    )


    one_hot[
        np.arange(
            len(
                labels
            )
        ),
        labels,
    ] = 1.0


    squared_error = (
        probabilities
        -
        one_hot
    ) ** 2


    return float(
        np.mean(
            np.sum(
                squared_error,
                axis=1,
            )
        )
    )


def top1_accuracy(
    probabilities,
    labels,
):

    predictions = np.argmax(
        probabilities,
        axis=1,
    )


    return float(
        np.mean(
            predictions
            ==
            labels
        )
    )


def mean_confidence(
    probabilities,
):

    return float(
        np.mean(
            np.max(
                probabilities,
                axis=1,
            )
        )
    )


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 92)
    print(
        "BREEDVISION AI - PHASE 7 TEMPERATURE CALIBRATION"
    )
    print("=" * 92)


    if not INPUT_NPZ.exists():

        raise FileNotFoundError(
            f"Validation logits missing:\n"
            f"{INPUT_NPZ}"
        )


    config = load_json(
        PHASE7_CONFIG
    )


    calibration_config = (
        config[
            "calibration"
        ]
    )


    minimum_temperature = float(
        calibration_config[
            "minimum_temperature"
        ]
    )


    maximum_temperature = float(
        calibration_config[
            "maximum_temperature"
        ]
    )


    cache = np.load(
        INPUT_NPZ
    )


    logits_numpy = (
        cache[
            "logits"
        ]
        .astype(
            np.float64
        )
    )


    labels_numpy = (
        cache[
            "labels"
        ]
        .astype(
            np.int64
        )
    )


    image_paths = (
        cache[
            "image_paths"
        ]
    )


    if logits_numpy.ndim != 2:

        raise RuntimeError(
            "Expected logits to be a 2D array."
        )


    if labels_numpy.ndim != 1:

        raise RuntimeError(
            "Expected labels to be a 1D array."
        )


    if (
        logits_numpy.shape[
            0
        ]
        !=
        labels_numpy.shape[
            0
        ]
    ):

        raise RuntimeError(
            "Logit and label sample counts differ."
        )


    if not np.isfinite(
        logits_numpy
    ).all():

        raise RuntimeError(
            "Non-finite logits detected."
        )


    num_samples = int(
        logits_numpy.shape[
            0
        ]
    )


    num_classes = int(
        logits_numpy.shape[
            1
        ]
    )


    print()
    print(
        "Samples:",
        num_samples
    )

    print(
        "Classes:",
        num_classes
    )


    logits_tensor = torch.tensor(
        logits_numpy,
        dtype=torch.float64,
    )


    labels_tensor = torch.tensor(
        labels_numpy,
        dtype=torch.long,
    )


    # =====================================================
    # RAW METRICS
    # =====================================================


    raw_probabilities = (
        softmax_numpy(
            logits_numpy
        )
    )


    raw_nll = (
        negative_log_likelihood(
            logits_tensor,
            labels_tensor,
            temperature=1.0,
        )
    )


    raw_ece, raw_bins = (
        expected_calibration_error(
            raw_probabilities,
            labels_numpy,
            num_bins=15,
        )
    )


    raw_brier = (
        multiclass_brier_score(
            raw_probabilities,
            labels_numpy,
            num_classes,
        )
    )


    raw_accuracy = (
        top1_accuracy(
            raw_probabilities,
            labels_numpy,
        )
    )


    raw_mean_confidence = (
        mean_confidence(
            raw_probabilities
        )
    )


    # =====================================================
    # TEMPERATURE OPTIMIZATION
    # =====================================================


    print()
    print(
        "Optimizing temperature..."
    )


    def objective(
        temperature,
    ):

        return negative_log_likelihood(
            logits_tensor,
            labels_tensor,
            temperature=float(
                temperature
            ),
        )


    result = minimize_scalar(
        objective,
        bounds=(
            minimum_temperature,
            maximum_temperature,
        ),
        method="bounded",
        options={
            "xatol": 1e-6,
        },
    )


    if not result.success:

        raise RuntimeError(
            "Temperature optimization failed: "
            f"{result.message}"
        )


    temperature = float(
        result.x
    )


    if not (
        minimum_temperature
        <=
        temperature
        <=
        maximum_temperature
    ):

        raise RuntimeError(
            "Optimized temperature outside "
            "configured bounds."
        )


    # =====================================================
    # CALIBRATED METRICS
    # =====================================================


    calibrated_logits = (
        logits_numpy
        /
        temperature
    )


    calibrated_probabilities = (
        softmax_numpy(
            calibrated_logits
        )
    )


    calibrated_nll = (
        negative_log_likelihood(
            logits_tensor,
            labels_tensor,
            temperature=
                temperature,
        )
    )


    calibrated_ece, calibrated_bins = (
        expected_calibration_error(
            calibrated_probabilities,
            labels_numpy,
            num_bins=15,
        )
    )


    calibrated_brier = (
        multiclass_brier_score(
            calibrated_probabilities,
            labels_numpy,
            num_classes,
        )
    )


    calibrated_accuracy = (
        top1_accuracy(
            calibrated_probabilities,
            labels_numpy,
        )
    )


    calibrated_mean_confidence = (
        mean_confidence(
            calibrated_probabilities
        )
    )


    # Temperature scaling must not change argmax predictions.

    if abs(
        raw_accuracy
        -
        calibrated_accuracy
    ) > 1e-12:

        raise RuntimeError(
            "Temperature scaling unexpectedly "
            "changed classification accuracy."
        )


    # Since temperature is selected by NLL,
    # calibrated NLL should not be worse beyond tiny
    # numerical tolerance.

    if (
        calibrated_nll
        >
        raw_nll
        +
        1e-6
    ):

        raise RuntimeError(
            "Calibrated NLL is worse than raw NLL."
        )


    # =====================================================
    # SAVE CALIBRATED CACHE
    # =====================================================


    OUTPUT_NPZ.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    np.savez_compressed(
        OUTPUT_NPZ,

        logits=
            logits_numpy,

        calibrated_logits=
            calibrated_logits,

        raw_probabilities=
            raw_probabilities,

        calibrated_probabilities=
            calibrated_probabilities,

        labels=
            labels_numpy,

        image_paths=
            image_paths,

        temperature=
            np.array(
                temperature,
                dtype=np.float64,
            ),
    )


    # =====================================================
    # SAVE CALIBRATION CONFIG
    # =====================================================


    calibration_output = {

        "project":
            "BreedVision AI",

        "phase":
            7,

        "classifier_version":
            "v2",

        "method":
            "temperature_scaling",

        "fit_split":
            "validation",

        "temperature":
            temperature,

        "optimization_metric":
            "negative_log_likelihood",

        "temperature_bounds": {
            "minimum":
                minimum_temperature,

            "maximum":
                maximum_temperature,
        },

        "important_note":
            (
                "Temperature was fitted using validation "
                "data only. Test data was not used."
            ),
    }


    with OUTPUT_CALIBRATION_CONFIG.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            calibration_output,
            file,
            indent=4,
        )


    # =====================================================
    # SAVE REPORT
    # =====================================================


    metrics_output = {

        "phase":
            (
                "Phase 7 - Temperature "
                "Calibration Evaluation"
            ),

        "samples":
            num_samples,

        "num_classes":
            num_classes,

        "temperature":
            temperature,

        "before_calibration": {
            "accuracy":
                raw_accuracy,

            "negative_log_likelihood":
                raw_nll,

            "expected_calibration_error":
                raw_ece,

            "multiclass_brier_score":
                raw_brier,

            "mean_top1_probability":
                raw_mean_confidence,
        },

        "after_calibration": {
            "accuracy":
                calibrated_accuracy,

            "negative_log_likelihood":
                calibrated_nll,

            "expected_calibration_error":
                calibrated_ece,

            "multiclass_brier_score":
                calibrated_brier,

            "mean_top1_probability":
                calibrated_mean_confidence,
        },

        "delta": {
            "negative_log_likelihood":
                calibrated_nll
                -
                raw_nll,

            "expected_calibration_error":
                calibrated_ece
                -
                raw_ece,

            "multiclass_brier_score":
                calibrated_brier
                -
                raw_brier,
        },

        "reliability_bins_before":
            raw_bins,

        "reliability_bins_after":
            calibrated_bins,

        "interpretation_note":
            (
                "Temperature scaling was optimized for "
                "validation negative log-likelihood. "
                "ECE or Brier score may improve or worsen "
                "slightly because they were not directly "
                "optimized."
            ),
    }


    with OUTPUT_METRICS.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metrics_output,
            file,
            indent=4,
        )


    # =====================================================
    # DISPLAY
    # =====================================================


    print()
    print("-" * 92)

    print(
        "Optimal temperature :",
        round(
            temperature,
            6,
        )
    )


    print()
    print(
        "Accuracy"
    )

    print(
        " Before:",
        round(
            raw_accuracy,
            6,
        )
    )

    print(
        " After :",
        round(
            calibrated_accuracy,
            6,
        )
    )


    print()
    print(
        "Negative Log-Likelihood"
    )

    print(
        " Before:",
        round(
            raw_nll,
            6,
        )
    )

    print(
        " After :",
        round(
            calibrated_nll,
            6,
        )
    )


    print()
    print(
        "Expected Calibration Error"
    )

    print(
        " Before:",
        round(
            raw_ece,
            6,
        )
    )

    print(
        " After :",
        round(
            calibrated_ece,
            6,
        )
    )


    print()
    print(
        "Multiclass Brier Score"
    )

    print(
        " Before:",
        round(
            raw_brier,
            6,
        )
    )

    print(
        " After :",
        round(
            calibrated_brier,
            6,
        )
    )


    print()
    print(
        "Mean Top-1 Probability"
    )

    print(
        " Before:",
        round(
            raw_mean_confidence,
            6,
        )
    )

    print(
        " After :",
        round(
            calibrated_mean_confidence,
            6,
        )
    )


    print()
    print("=" * 92)
    print(
        "PHASE 7 TEMPERATURE CALIBRATION: PASS"
    )
    print("=" * 92)


if __name__ == "__main__":

    main()