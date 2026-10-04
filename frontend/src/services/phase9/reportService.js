import {
  getOperationalAnalytics,
} from "./analyticsService";


const escapeCsv = (
  value
) => {

  if (
    value === null ||
    value === undefined
  ) {
    return "";
  }


  const text =
    String(
      value
    );


  return `"${text.replaceAll(
    '"',
    '""'
  )}"`;
};


const downloadText = (
  filename,
  content,
  mimeType
) => {

  const blob =
    new Blob(
      [
        content,
      ],
      {
        type:
          mimeType,
      }
    );


  const url =
    URL.createObjectURL(
      blob
    );


  const anchor =
    document.createElement(
      "a"
    );


  anchor.href =
    url;

  anchor.download =
    filename;


  document.body.appendChild(
    anchor
  );


  anchor.click();

  anchor.remove();


  URL.revokeObjectURL(
    url
  );
};


export const buildOperationsReport =
  async () => {

    const analytics =
      await getOperationalAnalytics();


    return {
      project:
        "BreedVision AI",

      report:
        "Phase 9 Operational Report",

      generated_at:
        new Date()
          .toISOString(),

      summary:
        analytics.summary,

      distributions: {
        detection_species:
          analytics.detection_species,

        detection_breeds:
          analytics.detection_breeds,

        animal_species:
          analytics.animal_species,

        review_decisions:
          analytics.review_decisions,

        alert_statuses:
          analytics.alert_statuses,
      },

      records:
        analytics.raw,
    };
  };


export const downloadOperationsJson =
  async () => {

    const report =
      await buildOperationsReport();


    downloadText(
      `breedvision-report-${Date.now()}.json`,
      JSON.stringify(
        report,
        null,
        2
      ),
      "application/json"
    );


    return report;
  };


export const downloadDetectionsCsv =
  async () => {

    const report =
      await buildOperationsReport();


    const detections =
      report.records
        .detections;


    const headers = [
      "id",
      "created_at",
      "original_filename",
      "source",
      "species",
      "predicted_breed",
      "confidence",
      "review_status",
      "farmer_id",
      "animal_id",
      "model_version",
    ];


    const rows = [
      headers.join(","),
      ...detections.map(
        (
          detection
        ) =>
          headers
            .map(
              (
                header
              ) =>
                escapeCsv(
                  detection[
                    header
                  ]
                )
            )
            .join(",")
      ),
    ];


    downloadText(
      `breedvision-detections-${Date.now()}.csv`,
      rows.join("\n"),
      "text/csv;charset=utf-8"
    );


    return detections.length;
  };