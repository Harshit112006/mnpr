import {
  CheckCircle2,
  Database,
  FileImage,
  Ruler,
  Server,
} from "lucide-react";


function BackendResultPanel({
  result,
}) {

  if (!result) {
    return null;
  }


  const image =
    result.image || {};


  const bovine =
    result.bovine || null;


  const prediction =
    result.prediction || null;


  const topPredictions =
    prediction
      ?.top_predictions ||
    [];


  const fileSize =
    image.size_mb !==
      undefined &&
    image.size_mb !==
      null
      ? `${Number(
          image.size_mb
        ).toFixed(2)} MB`
      : image.size_bytes
        ? `${(
            image.size_bytes /
            1024 /
            1024
          ).toFixed(2)} MB`
        : "—";


  const confidence =
    prediction
      ?.calibrated_probability !==
      undefined
      ? `${(
          Number(
            prediction
              .calibrated_probability
          ) * 100
        ).toFixed(2)}%`
      : "—";


  const detectorScore =
    bovine?.score !==
      null &&
    bovine?.score !==
      undefined
      ? `${(
          Number(
            bovine.score
          ) * 100
        ).toFixed(2)}%`
      : "—";


  return (
    <div className="backend-result-panel">

      <div className="backend-result-title">

        <CheckCircle2
          size={18}
        />

        <div>

          <strong>
            BreedVision analysis complete
          </strong>

          <span>
            {result.message}
          </span>

        </div>

      </div>


      <div className="backend-result-grid">

        <div>

          <FileImage
            size={15}
          />

          <span>
            Filename
          </span>

          <strong>
            {image.filename ||
              "—"}
          </strong>

        </div>


        <div>

          <Ruler
            size={15}
          />

          <span>
            Resolution
          </span>

          <strong>
            {image.width &&
            image.height
              ? `${image.width} × ${image.height}`
              : "—"}
          </strong>

        </div>


        <div>

          <Database
            size={15}
          />

          <span>
            File Size
          </span>

          <strong>
            {fileSize}
          </strong>

        </div>


        <div>

          <Server
            size={15}
          />

          <span>
            Format
          </span>

          <strong>
            {image.format ||
              image.content_type ||
              "—"}
          </strong>

        </div>

      </div>


      <div className="backend-result-title">

        <Server
          size={18}
        />

        <div>

          <strong>
            Bovine detector
          </strong>

          <span>
            {bovine?.detected
              ? "Bovine detected successfully."
              : "No bovine detected in this image."}
          </span>

        </div>

      </div>


      <div className="backend-result-grid">

        <div>

          <span>
            Detected
          </span>

          <strong>
            {bovine?.detected
              ? "Yes"
              : "No"}
          </strong>

        </div>


        <div>

          <span>
            Detector Score
          </span>

          <strong>
            {detectorScore}
          </strong>

        </div>


        <div>

          <span>
            Detector
          </span>

          <strong>
            {bovine
              ?.model_version ||
              "—"}
          </strong>

        </div>

      </div>


      {prediction && (

        <>

          <div className="backend-result-title">

            <CheckCircle2
              size={18}
            />

            <div>

              <strong>
                Breed prediction
              </strong>

              <span>
                Temperature-calibrated
                classifier output.
              </span>

            </div>

          </div>


          <div className="backend-result-grid">

            <div>

              <span>
                Status
              </span>

              <strong>
                {prediction.status}
              </strong>

            </div>


            <div>

              <span>
                Breed
              </span>

              <strong>
                {prediction.breed ||
                  "Unknown"}
              </strong>

            </div>


            <div>

              <span>
                Species
              </span>

              <strong>
                {prediction.species ||
                  "Unknown"}
              </strong>

            </div>


            <div>

              <span>
                Calibrated probability
              </span>

              <strong>
                {confidence}
              </strong>

            </div>


            <div>

              <span>
                Model
              </span>

              <strong>
                {prediction
                  .model_version ||
                  "—"}
              </strong>

            </div>

          </div>


          {topPredictions.length >
            0 && (

            <div className="backend-result-note">

              <Server
                size={15}
              />

              <span>

                Top-3:{" "}

                {topPredictions
                  .map(
                    (
                      candidate
                    ) =>
                      `${candidate.rank}. ${candidate.breed} (${(
                        Number(
                          candidate.probability
                        ) * 100
                      ).toFixed(2)}%)`
                  )
                  .join(" • ")}

              </span>

            </div>

          )}

        </>

      )}


      <div className="backend-result-note">

        <Server
          size={15}
        />

        <span>
          {result.message ||
            "BreedVision analysis completed."}
        </span>

      </div>

    </div>
  );
}


export default BackendResultPanel;