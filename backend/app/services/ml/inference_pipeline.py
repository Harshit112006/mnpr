from functools import lru_cache

from PIL import Image

from app.services.ml.paths import validate_ml_paths


class BreedVisionInferencePipeline:
    def __init__(self):
        path_status = validate_ml_paths()

        if not path_status["ready"]:
            raise RuntimeError(
                "Required ML files are missing: "
                f"{path_status['missing']}"
            )

        # Import heavy ML dependencies only when
        # inference is actually requested.
        import torch

        torch.set_num_threads(1)

        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass

        from app.services.ml.detector_service import (
            BovineDetectorService,
        )
        from app.services.ml.classifier_service import (
            BreedClassifierService,
        )

        self.detector = BovineDetectorService()
        self.classifier = BreedClassifierService()

    def predict(self, image: Image.Image):
        if not isinstance(image, Image.Image):
            raise TypeError(
                "Pipeline input must be a PIL image."
            )

        rgb_image = image.convert("RGB")

        detection = self.detector.detect(rgb_image)

        if not detection["detected"]:
            return {
                "pipeline_status": "no_bovine",
                "bovine": detection,
                "prediction": None,
            }

        crop = self.detector.crop(
            rgb_image,
            detection["bbox"],
        )

        prediction = self.classifier.predict(
            crop,
            top_k=3,
        )

        return {
            "pipeline_status": prediction["status"],
            "bovine": detection,
            "prediction": prediction,
        }

    def health(self):
        return {
            "ready": True,
            "detector": self.detector.health(),
            "classifier": self.classifier.health(),
        }


@lru_cache(maxsize=1)
def get_inference_pipeline():
    return BreedVisionInferencePipeline()