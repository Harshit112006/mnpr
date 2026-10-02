import { useEffect, useRef, useState } from "react";
import {
  UploadCloud,
  Camera,
  ImagePlus,
  X,
  ScanSearch,
  ShieldCheck,
  Info,
  FileImage,
} from "lucide-react";

import "../../styles/Detection.css";

function Detection() {
  const fileInputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState("");

  const allowedTypes = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
  ];

  const maxFileSize = 10 * 1024 * 1024;

  const handleFile = (file) => {
    setError("");

    if (!file) {
      return;
    }

    if (!allowedTypes.includes(file.type)) {
      setError("Please upload a JPG, JPEG, PNG or WEBP image.");
      return;
    }

    if (file.size > maxFileSize) {
      setError("Image size must be less than 10 MB.");
      return;
    }

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    const newPreviewUrl = URL.createObjectURL(file);

    setSelectedFile(file);
    setPreviewUrl(newPreviewUrl);
  };

  const handleInputChange = (event) => {
    const file = event.target.files?.[0];

    handleFile(file);

    event.target.value = "";
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();

    setIsDragging(false);

    const file = event.dataTransfer.files?.[0];

    handleFile(file);
  };

  const removeImage = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setSelectedFile(null);
    setPreviewUrl("");
    setError("");
  };

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  return (
    <div className="detection-page">
      <section className="detection-header">
        <div>
          <span className="detection-eyebrow">
            BREEDVISION COMPUTER VISION
          </span>

          <h1>AI Breed Detection</h1>

          <p>
            Upload a clear image of cattle or buffalo for breed
            identification and confidence analysis.
          </p>
        </div>

        <div className="detection-status">
          <div className="detection-status-dot" />

          <div>
            <span>Detection Interface</span>
            <p>Frontend ready</p>
          </div>
        </div>
      </section>

      <section className="detection-workspace">
        <div className="detection-upload-panel">
          <div className="detection-panel-heading">
            <div>
              <span>STEP 01</span>
              <h2>Provide animal image</h2>
              <p>
                Upload a clear side or front-view image for better
                breed analysis.
              </p>
            </div>

            <ImagePlus size={23} />
          </div>

          {!previewUrl ? (
            <div
              className={`image-drop-zone ${
                isDragging ? "dragging" : ""
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="drop-zone-icon">
                <UploadCloud size={32} />
              </div>

              <h3>
                {isDragging
                  ? "Drop image here"
                  : "Upload animal image"}
              </h3>

              <p>
                Drag and drop your image here or click to browse
              </p>

              <button
                type="button"
                className="browse-image-button"
                onClick={(event) => {
                  event.stopPropagation();
                  fileInputRef.current?.click();
                }}
              >
                <FileImage size={17} />
                Browse Image
              </button>

              <span className="upload-requirements">
                JPG, JPEG, PNG or WEBP • Maximum 10 MB
              </span>
            </div>
          ) : (
            <div className="image-preview-container">
              <div className="image-preview-toolbar">
                <div>
                  <span>IMAGE READY</span>
                  <p>{selectedFile?.name}</p>
                </div>

                <button
                  type="button"
                  className="remove-image-button"
                  onClick={removeImage}
                  title="Remove image"
                >
                  <X size={18} />
                </button>
              </div>

              <div className="image-preview">
                <img
                  src={previewUrl}
                  alt="Animal preview"
                />
              </div>

              <div className="image-file-info">
                <div>
                  <span>File size</span>
                  <strong>
                    {selectedFile
                      ? `${(
                          selectedFile.size /
                          1024 /
                          1024
                        ).toFixed(2)} MB`
                      : "—"}
                  </strong>
                </div>

                <div>
                  <span>Format</span>
                  <strong>
                    {selectedFile?.type
                      ?.replace("image/", "")
                      .toUpperCase() || "—"}
                  </strong>
                </div>

                <div>
                  <span>Status</span>
                  <strong className="valid-image-status">
                    Valid
                  </strong>
                </div>
              </div>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleInputChange}
            hidden
          />

          {error && (
            <div className="detection-error-message">
              <Info size={16} />
              {error}
            </div>
          )}

          <div className="image-source-divider">
            <span />
            <p>OR</p>
            <span />
          </div>

          <button
            type="button"
            className="camera-source-button"
          >
            <Camera size={18} />
            Capture using Camera

            <span>Coming next</span>
          </button>
        </div>

        <aside className="detection-analysis-panel">
          <div className="analysis-panel-heading">
            <ScanSearch size={23} />

            <div>
              <span>STEP 02</span>
              <h2>AI Analysis</h2>
            </div>
          </div>

          {!selectedFile ? (
            <div className="analysis-empty-state">
              <div className="analysis-empty-icon">
                <ScanSearch size={31} />
              </div>

              <h3>Waiting for an image</h3>

              <p>
                Upload or capture an animal image before starting
                BreedVision analysis.
              </p>
            </div>
          ) : (
            <div className="analysis-ready-state">
              <div className="analysis-ready-icon">
                <ShieldCheck size={28} />
              </div>

              <span>IMAGE VALIDATED</span>

              <h3>Ready for breed analysis</h3>

              <p>
                Your image passed the frontend validation checks.
                Model inference will be connected through the
                FastAPI backend.
              </p>

              <button
                type="button"
                className="analyze-animal-button"
                disabled
              >
                <ScanSearch size={18} />
                Analyze Animal
              </button>

              <div className="model-not-connected">
                ML backend not connected yet
              </div>
            </div>
          )}

          <div className="detection-help-card">
            <h4>For better accuracy</h4>

            <div>
              <span>01</span>
              <p>Keep the complete animal visible.</p>
            </div>

            <div>
              <span>02</span>
              <p>Use good lighting and avoid heavy blur.</p>
            </div>

            <div>
              <span>03</span>
              <p>Prefer one animal per image.</p>
            </div>

            <div>
              <span>04</span>
              <p>Side or front views work best.</p>
            </div>
          </div>
        </aside>
      </section>
    </div>
  );
}

export default Detection;