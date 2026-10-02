import { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";

import {
  UploadCloud,
  Camera,
  ImagePlus,
  X,
  ScanSearch,
  ShieldCheck,
  Info,
  FileImage,
  CameraOff,
  LoaderCircle,
} from "lucide-react";

import ImageQualityPanel from "../../components/detection/ImageQualityPanel";
import { analyzeImageQuality } from "../../utils/imageQuality";

import "../../styles/Detection.css";

function Detection() {
  const fileInputRef = useRef(null);
  const webcamRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");

  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState("");

  const [cameraOpen, setCameraOpen] = useState(false);
  const [cameraError, setCameraError] = useState("");

  const [quality, setQuality] = useState(null);
  const [qualityLoading, setQualityLoading] = useState(false);

  const allowedTypes = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
  ];

  const maxFileSize = 10 * 1024 * 1024;

  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: "environment",
  };

  const clearOldPreview = () => {
    if (previewUrl && previewUrl.startsWith("blob:")) {
      URL.revokeObjectURL(previewUrl);
    }
  };

  const handleFile = (file) => {
    setError("");
    setQuality(null);

    if (!file) {
      return;
    }

    if (!allowedTypes.includes(file.type)) {
      setError(
        "Please upload a JPG, JPEG, PNG or WEBP image."
      );
      return;
    }

    if (file.size > maxFileSize) {
      setError(
        "Image size must be less than 10 MB."
      );
      return;
    }

    clearOldPreview();

    const newPreviewUrl =
      URL.createObjectURL(file);

    setSelectedFile(file);
    setPreviewUrl(newPreviewUrl);
  };

  const handleInputChange = (event) => {
    const file =
      event.target.files?.[0];

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

    const file =
      event.dataTransfer.files?.[0];

    handleFile(file);
  };

  const removeImage = () => {
    clearOldPreview();

    setSelectedFile(null);
    setPreviewUrl("");
    setQuality(null);
    setError("");
  };

  const openCamera = () => {
    setCameraError("");
    setCameraOpen(true);
  };

  const closeCamera = () => {
    setCameraOpen(false);
    setCameraError("");
  };

  const capturePhoto = async () => {
    const screenshot =
      webcamRef.current?.getScreenshot();

    if (!screenshot) {
      setCameraError(
        "Unable to capture image. Please try again."
      );

      return;
    }

    try {
      const response =
        await fetch(screenshot);

      const blob =
        await response.blob();

      const capturedFile =
        new File(
          [blob],
          `breedvision-capture-${Date.now()}.jpg`,
          {
            type: "image/jpeg",
          }
        );

      handleFile(capturedFile);

      setCameraOpen(false);
      setCameraError("");
    } catch (captureError) {
      console.error(
        "Camera capture error:",
        captureError
      );

      setCameraError(
        "Unable to process captured image."
      );
    }
  };

  useEffect(() => {
    if (!previewUrl) {
      setQuality(null);
      return;
    }

    let cancelled = false;

    const runQualityAnalysis = async () => {
      try {
        setQualityLoading(true);

        const result =
          await analyzeImageQuality(previewUrl);

        if (!cancelled) {
          setQuality(result);
        }
      } catch (qualityError) {
        console.error(
          "Image quality analysis failed:",
          qualityError
        );

        if (!cancelled) {
          setQuality(null);
        }
      } finally {
        if (!cancelled) {
          setQualityLoading(false);
        }
      }
    };

    runQualityAnalysis();

    return () => {
      cancelled = true;
    };
  }, [previewUrl]);

  useEffect(() => {
    return () => {
      if (
        previewUrl &&
        previewUrl.startsWith("blob:")
      ) {
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
            Upload or capture a clear image of cattle
            or buffalo for breed identification and
            confidence analysis.
          </p>
        </div>

        <div className="detection-status">
          <div className="detection-status-dot" />

          <div>
            <span>Detection Interface</span>
            <p>Upload, camera & quality check ready</p>
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
                Upload a clear side or front-view image
                for better breed analysis.
              </p>
            </div>

            <ImagePlus size={23} />
          </div>

          {cameraOpen ? (

            <div className="camera-workspace">

              <div className="camera-toolbar">
                <div>
                  <span>LIVE CAMERA</span>

                  <p>
                    Position the animal clearly
                    inside the frame
                  </p>
                </div>

                <button
                  type="button"
                  className="camera-close-button"
                  onClick={closeCamera}
                >
                  <X size={18} />
                </button>
              </div>

              <div className="webcam-container">

                {!cameraError ? (
                  <Webcam
                    ref={webcamRef}
                    audio={false}
                    mirrored={false}
                    screenshotFormat="image/jpeg"
                    screenshotQuality={0.95}
                    videoConstraints={videoConstraints}
                    className="webcam-video"
                    onUserMedia={() => {
                      setCameraError("");
                    }}
                    onUserMediaError={() => {
                      setCameraError(
                        "Camera access failed. Please allow camera permission in your browser."
                      );
                    }}
                  />
                ) : (
                  <div className="camera-error-state">
                    <CameraOff size={32} />

                    <h3>Camera unavailable</h3>

                    <p>{cameraError}</p>
                  </div>
                )}

                {!cameraError && (
                  <div className="camera-frame-guide">
                    <div className="frame-corner top-left" />
                    <div className="frame-corner top-right" />
                    <div className="frame-corner bottom-left" />
                    <div className="frame-corner bottom-right" />
                  </div>
                )}

              </div>

              <div className="camera-controls">

                <button
                  type="button"
                  className="camera-cancel-button"
                  onClick={closeCamera}
                >
                  <CameraOff size={17} />
                  Cancel
                </button>

                <button
                  type="button"
                  className="capture-photo-button"
                  onClick={capturePhoto}
                  disabled={Boolean(cameraError)}
                >
                  <Camera size={19} />
                  Capture Photo
                </button>

              </div>

            </div>

          ) : !previewUrl ? (

            <div
              className={`image-drop-zone ${
                isDragging ? "dragging" : ""
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() =>
                fileInputRef.current?.click()
              }
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
                Drag and drop your image here
                or click to browse
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

          {!cameraOpen && (
            <>
              <div className="image-source-divider">
                <span />
                <p>OR</p>
                <span />
              </div>

              <button
                type="button"
                className="camera-source-button"
                onClick={openCamera}
              >
                <Camera size={18} />

                Capture using Camera

                <span>LIVE</span>
              </button>
            </>
          )}

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
                Upload or capture an animal image
                before starting BreedVision analysis.
              </p>

            </div>

          ) : (

            <>
              {qualityLoading ? (

                <div className="quality-loading-state">
                  <LoaderCircle
                    size={28}
                    className="quality-loading-spinner"
                  />

                  <h3>Checking image quality</h3>

                  <p>
                    BreedVision is analyzing resolution,
                    brightness and sharpness.
                  </p>
                </div>

              ) : (

                <ImageQualityPanel quality={quality} />

              )}

              <div className="analysis-ready-state compact-analysis">

                <div className="analysis-ready-icon">
                  <ShieldCheck size={28} />
                </div>

                <span>FRONTEND VALIDATION COMPLETE</span>

                <h3>
                  {quality?.suitable
                    ? "Ready for breed analysis"
                    : "Image can still be submitted"}
                </h3>

                <p>
                  Image-quality checks are advisory.
                  Final breed recognition will be performed
                  by the FastAPI ML pipeline.
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
                  FastAPI backend connection is the next phase
                </div>

              </div>
            </>
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