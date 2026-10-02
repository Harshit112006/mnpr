import {
  getDetectionImageUrl,
  getUserDetections,
} from "./detectionDataService";


const startOfDay = (date) => {
  const copy = new Date(date);

  copy.setHours(
    0,
    0,
    0,
    0
  );

  return copy;
};


const formatDayLabel = (
  date
) => {
  return date.toLocaleDateString(
    "en-IN",
    {
      weekday: "short",
    }
  );
};


export const getDashboardData =
  async () => {
    const detections =
      await getUserDetections();


    /* =====================================================
       BASIC COUNTS
       ===================================================== */

    const totalDetections =
      detections.length;


    const pendingReviews =
      detections.filter(
        (
          detection
        ) =>
          detection.review_status ===
          "pending"
      ).length;


    const cameraDetections =
      detections.filter(
        (
          detection
        ) =>
          detection.source ===
          "camera"
      ).length;


    /* =====================================================
       REAL CONFIDENCE ONLY

       ML is not connected yet, therefore NULL confidence
       values are excluded instead of creating fake scores.
       ===================================================== */

    const confidenceValues =
      detections
        .map(
          (
            detection
          ) =>
            detection.confidence
        )
        .filter(
          (
            confidence
          ) =>
            confidence !== null &&
            confidence !== undefined &&
            Number.isFinite(
              Number(
                confidence
              )
            )
        )
        .map(Number);


    const averageConfidence =
      confidenceValues.length >
      0
        ? confidenceValues.reduce(
            (
              total,
              value
            ) =>
              total +
              value,
            0
          ) /
          confidenceValues.length
        : null;


    /* =====================================================
       LAST 7 DAYS ACTIVITY
       ===================================================== */

    const today =
      startOfDay(
        new Date()
      );


    const activity = [];


    for (
      let offset = 6;
      offset >= 0;
      offset -= 1
    ) {
      const day =
        new Date(
          today
        );

      day.setDate(
        today.getDate() -
          offset
      );


      const nextDay =
        new Date(
          day
        );

      nextDay.setDate(
        day.getDate() + 1
      );


      const count =
        detections.filter(
          (
            detection
          ) => {
            const createdAt =
              new Date(
                detection.created_at
              );


            return (
              createdAt >=
                day &&
              createdAt <
                nextDay
            );
          }
        ).length;


      activity.push({
        date:
          day.toISOString(),

        day:
          formatDayLabel(
            day
          ),

        detections:
          count,
      });
    }


    /* =====================================================
       BREED DISTRIBUTION

       Only REAL ML predictions are counted.
       ===================================================== */

    const breedMap =
      new Map();


    detections.forEach(
      (
        detection
      ) => {
        if (
          !detection.predicted_breed
        ) {
          return;
        }


        const breed =
          detection.predicted_breed;


        breedMap.set(
          breed,
          (
            breedMap.get(
              breed
            ) || 0
          ) + 1
        );
      }
    );


    const breedDistribution =
      Array.from(
        breedMap.entries()
      )
        .map(
          ([
            breed,
            count,
          ]) => ({
            breed,
            count,
          })
        )
        .sort(
          (
            first,
            second
          ) =>
            second.count -
            first.count
        );


    /* =====================================================
       RECENT DETECTIONS
       ===================================================== */

    const recentRaw =
      detections.slice(
        0,
        5
      );


    const recentDetections =
      await Promise.all(
        recentRaw.map(
          async (
            detection
          ) => {
            try {
              const signedUrl =
                await getDetectionImageUrl(
                  detection.image_path,
                  1800
                );


              return {
                ...detection,

                signed_url:
                  signedUrl,
              };

            } catch (
              imageError
            ) {
              console.error(
                "Recent detection image URL error:",
                imageError
              );


              return {
                ...detection,

                signed_url:
                  null,
              };
            }
          }
        )
      );


    return {
      totalDetections,

      pendingReviews,

      cameraDetections,

      averageConfidence,

      activity,

      breedDistribution,

      recentDetections,
    };
  };