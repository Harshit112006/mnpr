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


  const fileSize =
    image.size_mb !==
      undefined &&
    image.size_mb !== null
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


  return (
    <div className="backend-result-panel">

      <div className="backend-result-title">

        <CheckCircle2
          size={18}
        />

        <div>

          <strong>
            Backend connection successful
          </strong>

          <span>
            FastAPI received and validated
            the image successfully.
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


      <div className="backend-result-note">

        <Server
          size={15}
        />

        <span>
          {result.message ||
            "Backend validation completed. ML inference is not connected yet."}
        </span>

      </div>

    </div>
  );
}


export default BackendResultPanel;