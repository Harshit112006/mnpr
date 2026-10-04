import {
  getUserDetections,
} from "../detectionDataService";

import {
  getFarmers,
} from "./farmerService";

import {
  getAnimals,
} from "./animalService";

import {
  getAlerts,
} from "./alertService";

import {
  getReviews,
} from "./reviewService";


const countBy = (
  rows,
  getter
) => {

  const counts = {};


  rows.forEach(
    (
      row
    ) => {

      const key =
        getter(
          row
        );


      if (!key) {
        return;
      }


      counts[
        key
      ] =
        (
          counts[
            key
          ] ||
          0
        )
        +
        1;
    }
  );


  return Object.entries(
    counts
  )
    .map(
      ([
        label,
        count,
      ]) => ({
        label,
        count,
      })
    )
    .sort(
      (
        left,
        right
      ) =>
        right.count -
        left.count
    );
};


export const getOperationalAnalytics =
  async () => {

    const [
      detections,
      farmers,
      animals,
      alerts,
      reviews,
    ] =
      await Promise.all([
        getUserDetections(),
        getFarmers(),
        getAnimals(),
        getAlerts(),
        getReviews(),
      ]);


    const confidenceValues =
      detections
        .map(
          (
            detection
          ) =>
            Number(
              detection.confidence
            )
        )
        .filter(
          Number.isFinite
        );


    const averageConfidence =
      confidenceValues.length
        ? (
            confidenceValues.reduce(
              (
                total,
                value
              ) =>
                total +
                value,
              0
            )
            /
            confidenceValues.length
          )
        : null;


    const knownDetections =
      detections.filter(
        (
          detection
        ) =>
          Boolean(
            detection.predicted_breed
          )
      ).length;


    const reviewRequired =
      detections.filter(
        (
          detection
        ) =>
          [
            "pending",
            "needs_review",
          ].includes(
            detection.review_status
          )
      ).length;


    return {

      summary: {
        detections:
          detections.length,

        known_detections:
          knownDetections,

        review_required:
          reviewRequired,

        farmers:
          farmers.length,

        animals:
          animals.length,

        alerts:
          alerts.length,

        unread_alerts:
          alerts.filter(
            (
              alert
            ) =>
              alert.status ===
              "unread"
          ).length,

        reviews:
          reviews.length,

        average_confidence:
          averageConfidence,
      },


      detection_species:
        countBy(
          detections,
          (
            detection
          ) =>
            detection.species
        ),


      detection_breeds:
        countBy(
          detections,
          (
            detection
          ) =>
            detection.predicted_breed
        ),


      animal_species:
        countBy(
          animals,
          (
            animal
          ) =>
            animal.species
        ),


      review_decisions:
        countBy(
          reviews,
          (
            review
          ) =>
            review.decision
        ),


      alert_statuses:
        countBy(
          alerts,
          (
            alert
          ) =>
            alert.status
        ),


      raw: {
        detections,
        farmers,
        animals,
        alerts,
        reviews,
      },
    };
  };