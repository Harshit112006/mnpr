import json
import threading

import numpy as np

from PIL import Image

from ultralytics import YOLO

from app.services.ml.paths import (
    DETECTOR_CONFIG,
    YOLO_WEIGHTS,
)


class BovineDetectorService:

    def __init__(
        self,
    ):

        self._lock = threading.Lock()

        with DETECTOR_CONFIG.open(
            "r",
            encoding="utf-8",
        ) as file:

            config = json.load(
                file
            )

        self.detector_version = (
            config.get(
                "detector_version",
                "bovine-detector-v1",
            )
        )

        self.target_class = (
            config.get(
                "target_class",
                "cow",
            )
        )

        self.target_class_id = int(
            config[
                "target_class_id"
            ]
        )

        # Phase-6 validated threshold.
        self.primary_threshold = float(
            config[
                "confidence_threshold"
            ]
        )

        # Phase-8 runtime recovery pass.
        #
        # COCO YOLO has only "cow" rather than
        # dedicated Indian cattle/buffalo classes.
        # A second lower-threshold + larger-resolution
        # pass improves recall without inventing a
        # detection.
        self.fallback_threshold = 0.08

        self.primary_image_size = 640

        self.fallback_image_size = 640

        self.model = YOLO(
            str(
                YOLO_WEIGHTS
            )
        )


    def _predict_best_bovine(
        self,
        image_array,
        confidence_threshold,
        image_size,
    ):

        with self._lock:

            result = (
                self.model.predict(
                    source=image_array,

                    conf=
                        confidence_threshold,

                    imgsz=
                        image_size,

                    device=
                        "cpu",

                    verbose=
                        False,
                )[
                    0
                ]
            )

        best_box = None
        best_score = -1.0

        boxes = result.boxes

        if boxes is None:

            return (
                None,
                None,
            )

        for box in boxes:

            class_id = int(
                box.cls.item()
            )

            if (
                class_id
                !=
                self.target_class_id
            ):

                continue

            score = float(
                box.conf.item()
            )

            if (
                score
                <=
                best_score
            ):

                continue

            coordinates = (
                box.xyxy[
                    0
                ]
                .cpu()
                .tolist()
            )

            best_box = [
                float(
                    value
                )

                for value
                in coordinates
            ]

            best_score = score

        if best_box is None:

            return (
                None,
                None,
            )

        return (
            best_box,
            float(
                best_score
            ),
        )


    def detect(
        self,
        image: Image.Image,
    ):

        if not isinstance(
            image,
            Image.Image,
        ):

            raise TypeError(
                "Detector input must be a PIL image."
            )

        image = image.convert(
            "RGB"
        )

        image_array = np.asarray(
            image
        )


        # =================================================
        # PASS 1
        # =================================================

        best_box, best_score = (
            self._predict_best_bovine(
                image_array=
                    image_array,

                confidence_threshold=
                    self.primary_threshold,

                image_size=
                    self.primary_image_size,
            )
        )


        if best_box is not None:

            return {
                "detected":
                    True,

                "score":
                    best_score,

                "bbox":
                    best_box,

                "target_class":
                    self.target_class,

                "model_version":
                    self.detector_version,

                "detection_mode":
                    "primary",

                "runtime_threshold":
                    self.primary_threshold,

                "image_size":
                    self.primary_image_size,
            }


        # =================================================
        # PASS 2 — RECALL FALLBACK
        # =================================================

        best_box, best_score = (
            self._predict_best_bovine(
                image_array=
                    image_array,

                confidence_threshold=
                    self.fallback_threshold,

                image_size=
                    self.fallback_image_size,
            )
        )


        if best_box is not None:

            return {
                "detected":
                    True,

                "score":
                    best_score,

                "bbox":
                    best_box,

                "target_class":
                    self.target_class,

                "model_version":
                    self.detector_version,

                "detection_mode":
                    "fallback",

                "runtime_threshold":
                    self.fallback_threshold,

                "image_size":
                    self.fallback_image_size,
            }


        return {
            "detected":
                False,

            "score":
                None,

            "bbox":
                None,

            "target_class":
                self.target_class,

            "model_version":
                self.detector_version,

            "detection_mode":
                "none",

            "runtime_threshold":
                None,

            "image_size":
                self.fallback_image_size,
        }


    @staticmethod
    def crop(
        image: Image.Image,
        bbox,
    ):

        if not bbox:

            raise ValueError(
                "Bounding box required."
            )

        width, height = (
            image.size
        )

        x1, y1, x2, y2 = bbox

        x1 = max(
            0,
            int(
                x1
            ),
        )

        y1 = max(
            0,
            int(
                y1
            ),
        )

        x2 = min(
            width,
            int(
                x2
            ),
        )

        y2 = min(
            height,
            int(
                y2
            ),
        )

        if (
            x2 <= x1
            or
            y2 <= y1
        ):

            raise RuntimeError(
                "Detector returned an invalid bounding box."
            )

        return image.crop(
            (
                x1,
                y1,
                x2,
                y2,
            )
        )


    def health(
        self,
    ):

        return {
            "ready":
                True,

            "model_version":
                self.detector_version,

            "target_class":
                self.target_class,

            "target_class_id":
                self.target_class_id,

            "primary_threshold":
                self.primary_threshold,

            "fallback_threshold":
                self.fallback_threshold,

            "primary_image_size":
                self.primary_image_size,

            "fallback_image_size":
                self.fallback_image_size,

            "weights":
                str(
                    YOLO_WEIGHTS
                ),
        }