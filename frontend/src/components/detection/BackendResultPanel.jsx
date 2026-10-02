import {
  CheckCircle2,
  FileImage,
  Maximize2,
  Database,
  BrainCircuit,
} from "lucide-react";

function BackendResultPanel({ result }) {
  if (!result) {
    return null;
  }

  const image = result.image;

  return (
    <div className="backend-result-panel">

      <div className="backend-result-header">
        <div>
          <span>FASTAPI RESPONSE</span>
          <h3>Image processed successfully</h3>
        </div>

        <CheckCircle2
          size={20}
          className="backend-result-success"
        />
      </div>

      <div className="backend-result-grid">

        <div className="backend-result-item">
          <FileImage size={17} />

          <div>
            <span>Filename</span>
            <strong>
              {image?.filename || "—"}
            </strong>
          </div>
        </div>

        <div className="backend-result-item">
          <Maximize2 size={17} />

          <div>
            <span>Resolution</span>
            <strong>
              {image
                ? `${image.width} × ${image.height}`
                : "—"}
            </strong>
          </div>
        </div>

        <div className="backend-result-item">
          <Database size={17} />

          <div>
            <span>File Size</span>
            <strong>
              {image
                ? `${image.size_mb} MB`
                : "—"}
            </strong>
          </div>
        </div>

        <div className="backend-result-item">
          <FileImage size={17} />

          <div>
            <span>Format</span>
            <strong>
              {image?.format || "—"}
            </strong>
          </div>
        </div>

      </div>

      <div className="backend-model-status">
        <BrainCircuit size={20} />

        <div>
          <strong>
            Backend connection successful
          </strong>

          <p>
            The image reached FastAPI successfully.
            Breed prediction will appear here after
            the ML models are connected.
          </p>
        </div>
      </div>

    </div>
  );
}

export default BackendResultPanel;