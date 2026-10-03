import {
  useEffect,
  useRef,
  useState,
} from "react";

import Webcam from "react-webcam";

import {
  Camera,
  CameraOff,
  CheckCircle2,
  Cloud,
  Database,
  FileImage,
  ImagePlus,
  Info,
  LoaderCircle,
  ScanSearch,
  ShieldCheck,
  UploadCloud,
  X,
} from "lucide-react";

import {
  detectAnimal,
} from "../../services/detectionService";

import {
  saveDetection,
} from "../../services/detectionDataService";

import BackendResultPanel from "../../components/detection/BackendResultPanel";

import ImageQualityPanel from "../../components/detection/ImageQualityPanel";

import {
  analyzeImageQuality,
} from "../../utils/imageQuality";

import "../../styles/Detection.css";
import "../../styles/DetectionPersistence.css";


function Detection() {
  const fileInputRef =
    useRef(null);

  const webcamRef =
    useRef(null);


  /* =====================================================
     IMAGE STATE
     ===================================================== */

  const [
    selectedFile,
    setSelectedFile,
  ] = useState(null);

  const [
    previewUrl,
    setPreviewUrl,
  ] = useState("");

  const [
    imageSource,
    setImageSource,
  ] = useState("upload");

  const [
    isDragging,
    setIsDragging,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");


  /* =====================================================
     CAMERA STATE
     ===================================================== */

  const [
    cameraOpen,
    setCameraOpen,
  ] = useState(false);

  const [
    cameraError,
    setCameraError,
  ] = useState("");


  /* =====================================================
     QUALITY STATE
     ===================================================== */

  const [
    quality,
    setQuality,
  ] = useState(null);

  const [
    qualityLoading,
    setQualityLoading,
  ] = useState(false);


  /* =====================================================
     BACKEND + DATABASE STATE
     ===================================================== */

  const [
    analysisLoading,
    setAnalysisLoading,
  ] = useState(false);

  const [
    backendResult,
    setBackendResult,
  ] = useState(null);

  const [
    backendError,
    setBackendError,
  ] = useState("");

  const [
    persistenceError,
    setPersistenceError,
  ] = useState("");

  const [
    savedDetection,
    setSavedDetection,
  ] = useState(null);


  /* =====================================================
     CONSTANTS
     ===================================================== */

  const allowedTypes = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
  ];


  const maxFileSize =
    10 * 1024 * 1024;


  const videoConstraints = {
    width: 1280,

    height: 720,

    facingMode:
      "environment",
  };


  /* =====================================================
     PREVIEW CLEANUP
     ===================================================== */

  const clearOldPreview =
    () => {
      if (
        previewUrl &&
        previewUrl.startsWith(
          "blob:"
        )
      ) {
        URL.revokeObjectURL(
          previewUrl
        );
      }
    };


  /* =====================================================
     HANDLE NEW FILE
     ===================================================== */

  const handleFile = (
    file,
    source = "upload"
  ) => {
    setError("");
    setQuality(null);

    setBackendResult(null);
    setBackendError("");
    setPersistenceError("");
    setSavedDetection(null);


    if (!file) {
      return;
    }


    if (
      !allowedTypes.includes(
        file.type
      )
    ) {
      setError(
        "Please upload a JPG, JPEG, PNG or WEBP image."
      );

      return;
    }


    if (
      file.size >
      maxFileSize
    ) {
      setError(
        "Image size must be less than 10 MB."
      );

      return;
    }


    clearOldPreview();


    const newPreviewUrl =
      URL.createObjectURL(
        file
      );


    setSelectedFile(file);

    setPreviewUrl(
      newPreviewUrl
    );

    setImageSource(
      source
    );
  };


  /* =====================================================
     FILE INPUT
     ===================================================== */

  const handleInputChange = (
    event
  ) => {
    const file =
      event.target
        .files?.[0];


    handleFile(
      file,
      "upload"
    );


    event.target.value =
      "";
  };


  /* =====================================================
     DRAG + DROP
     ===================================================== */

  const handleDragOver = (
    event
  ) => {
    event.preventDefault();

    setIsDragging(true);
  };


  const handleDragLeave = (
    event
  ) => {
    event.preventDefault();

    setIsDragging(false);
  };


  const handleDrop = (
    event
  ) => {
    event.preventDefault();

    setIsDragging(false);


    const file =
      event.dataTransfer
        .files?.[0];


    handleFile(
      file,
      "upload"
    );
  };


  /* =====================================================
     REMOVE IMAGE
     ===================================================== */

  const removeImage = () => {
    clearOldPreview();

    setSelectedFile(null);

    setPreviewUrl("");

    setQuality(null);

    setError("");

    setBackendResult(null);

    setBackendError("");

    setPersistenceError("");

    setSavedDetection(null);

    setImageSource(
      "upload"
    );
  };


  /* =====================================================
     CAMERA
     ===================================================== */

  const openCamera = () => {
    setCameraError("");

    setCameraOpen(true);
  };


  const closeCamera = () => {
    setCameraOpen(false);

    setCameraError("");
  };


  const capturePhoto =
    async () => {
      const screenshot =
        webcamRef.current
          ?.getScreenshot();


      if (!screenshot) {
        setCameraError(
          "Unable to capture image. Please try again."
        );

        return;
      }


      try {
        const response =
          await fetch(
            screenshot
          );


        const blob =
          await response.blob();


        const capturedFile =
          new File(
            [blob],

            `breedvision-capture-${Date.now()}.jpg`,

            {
              type:
                "image/jpeg",
            }
          );


        handleFile(
          capturedFile,
          "camera"
        );


        setCameraOpen(
          false
        );

        setCameraError(
          ""
        );

      } catch (
        captureError
      ) {
        console.error(
          "Camera capture error:",
          captureError
        );


        setCameraError(
          "Unable to process captured image."
        );
      }
    };


  /* =====================================================
     FRONTEND QUALITY ANALYSIS
     ===================================================== */

  useEffect(() => {
    if (!previewUrl) {
      setQuality(null);

      return;
    }


    let cancelled =
      false;


    const runQualityAnalysis =
      async () => {
        try {
          setQualityLoading(
            true
          );


          const result =
            await analyzeImageQuality(
              previewUrl
            );


          if (!cancelled) {
            setQuality(
              result
            );
          }

        } catch (
          qualityError
        ) {
          console.error(
            "Image quality analysis failed:",
            qualityError
          );


          if (!cancelled) {
            setQuality(
              null
            );
          }

        } finally {
          if (!cancelled) {
            setQualityLoading(
              false
            );
          }
        }
      };


    runQualityAnalysis();


    return () => {
      cancelled = true;
    };

  }, [previewUrl]);


  /* =====================================================
     REVOKE BLOB URL
     ===================================================== */

  useEffect(() => {
    return () => {
      if (
        previewUrl &&
        previewUrl.startsWith(
          "blob:"
        )
      ) {
        URL.revokeObjectURL(
          previewUrl
        );
      }
    };

  }, [previewUrl]);


  /* =====================================================
     ANALYZE + SAVE
     ===================================================== */

  const handleAnalyzeAnimal =
    async () => {
      if (!selectedFile) {
        setBackendError(
          "Please select an image first."
        );

        return;
      }


      if (
        qualityLoading
      ) {
        setBackendError(
          "Please wait for the image quality check to finish."
        );

        return;
      }


      if (
        savedDetection
      ) {
        return;
      }


      setBackendError("");

      setPersistenceError("");

      setBackendResult(null);

      setAnalysisLoading(
        true
      );


      try {
        /* ===============================================
           1. FASTAPI
           =============================================== */

        const result =
          await detectAnimal(
            selectedFile
          );


        setBackendResult(
          result
        );


        /* ===============================================
           2. SUPABASE STORAGE + DATABASE
           =============================================== */

        try {
          const saved =
            await saveDetection({
              file:
                selectedFile,

              source:
                imageSource,

              quality,

              backendImage:
                result?.image ||
                null,

              backendResult:
                result,
            });


          setSavedDetection(
            saved.detection
          );

        } catch (
          storageError
        ) {
          console.error(
            "Detection persistence error:",
            storageError
          );


          setPersistenceError(
            storageError.message ||
            "Backend analysis succeeded, but the detection could not be saved."
          );
        }

      } catch (
        analysisError
      ) {
        console.error(
          "Backend analysis error:",
          analysisError
        );


        const message =
          analysisError
            ?.response
            ?.data
            ?.detail ||
          analysisError
            ?.message ||
          "Unable to connect to the BreedVision backend.";


        setBackendError(
          message
        );

      } finally {
        setAnalysisLoading(
          false
        );
      }
    };


  /* =====================================================
     UI
     ===================================================== */

  return (
    <div className="detection-page">

      {/* HEADER */}

      <section className="detection-header">

        <div>

          <span className="detection-eyebrow">
            BREEDVISION COMPUTER VISION
          </span>

          <h1>
            AI Breed Detection
          </h1>

          <p>
            Upload or capture a clear image of cattle
            or buffalo for breed identification and
            confidence analysis.
          </p>

        </div>


        <div className="detection-status">

          <div className="detection-status-dot" />

          <div>

            <span>
              Detection Interface
            </span>

            <p>
              FastAPI, private storage & database ready
            </p>

          </div>

        </div>

      </section>


      {/* WORKSPACE */}

      <section className="detection-workspace">

        {/* =================================================
            LEFT SIDE
        ================================================= */}

        <div className="detection-upload-panel">

          <div className="detection-panel-heading">

            <div>

              <span>
                STEP 01
              </span>

              <h2>
                Provide animal image
              </h2>

              <p>
                Upload a clear side or front-view image
                for better breed analysis.
              </p>

            </div>

            <ImagePlus
              size={23}
            />

          </div>


          {/* CAMERA */}

          {cameraOpen ? (

            <div className="camera-workspace">

              <div className="camera-toolbar">

                <div>

                  <span>
                    LIVE CAMERA
                  </span>

                  <p>
                    Position the animal clearly
                    inside the frame.
                  </p>

                </div>


                <button
                  type="button"
                  className="camera-close-button"
                  onClick={
                    closeCamera
                  }
                >
                  <X
                    size={18}
                  />
                </button>

              </div>


              <div className="webcam-container">

                {!cameraError ? (

                  <Webcam
                    ref={
                      webcamRef
                    }
                    audio={
                      false
                    }
                    mirrored={
                      false
                    }
                    screenshotFormat="image/jpeg"
                    screenshotQuality={
                      0.95
                    }
                    videoConstraints={
                      videoConstraints
                    }
                    className="webcam-video"
                    onUserMedia={() => {
                      setCameraError(
                        ""
                      );
                    }}
                    onUserMediaError={() => {
                      setCameraError(
                        "Camera access failed. Please allow camera permission in your browser."
                      );
                    }}
                  />

                ) : (

                  <div className="camera-error-state">

                    <CameraOff
                      size={32}
                    />

                    <h3>
                      Camera unavailable
                    </h3>

                    <p>
                      {cameraError}
                    </p>

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
                  onClick={
                    closeCamera
                  }
                >
                  <CameraOff
                    size={17}
                  />

                  Cancel
                </button>


                <button
                  type="button"
                  className="capture-photo-button"
                  onClick={
                    capturePhoto
                  }
                  disabled={
                    Boolean(
                      cameraError
                    )
                  }
                >
                  <Camera
                    size={19}
                  />

                  Capture Photo
                </button>

              </div>

            </div>

          ) : !previewUrl ? (

            /* UPLOAD */

            <div
              className={`image-drop-zone ${
                isDragging
                  ? "dragging"
                  : ""
              }`}
              onDragOver={
                handleDragOver
              }
              onDragLeave={
                handleDragLeave
              }
              onDrop={
                handleDrop
              }
              onClick={() =>
                fileInputRef.current
                  ?.click()
              }
            >

              <div className="drop-zone-icon">

                <UploadCloud
                  size={32}
                />

              </div>


              <h3>
                {isDragging
                  ? "Drop image here"
                  : "Upload animal image"}
              </h3>


              <p>
                Drag and drop your image here
                or click to browse.
              </p>


              <button
                type="button"
                className="browse-image-button"
                onClick={
                  (
                    event
                  ) => {
                    event.stopPropagation();

                    fileInputRef.current
                      ?.click();
                  }
                }
              >
                <FileImage
                  size={17}
                />

                Browse Image
              </button>


              <span className="upload-requirements">
                JPG, JPEG, PNG or WEBP • Maximum 10 MB
              </span>

            </div>

          ) : (

            /* IMAGE PREVIEW */

            <div className="image-preview-container">

              <div className="image-preview-toolbar">

                <div>

                  <span>
                    IMAGE READY
                  </span>

                  <p>
                    {selectedFile?.name}
                  </p>

                </div>


                <button
                  type="button"
                  className="remove-image-button"
                  onClick={
                    removeImage
                  }
                  disabled={
                    analysisLoading
                  }
                >
                  <X
                    size={18}
                  />
                </button>

              </div>


              <div className="image-preview">

                <img
                  src={
                    previewUrl
                  }
                  alt="Animal preview"
                />

              </div>


              <div className="image-file-info">

                <div>

                  <span>
                    File size
                  </span>

                  <strong>
                    {selectedFile
                      ? `${(
                          selectedFile.size /
                          1024 /
                          1024
                        ).toFixed(
                          2
                        )} MB`
                      : "—"}
                  </strong>

                </div>


                <div>

                  <span>
                    Format
                  </span>

                  <strong>
                    {selectedFile
                      ?.type
                      ?.replace(
                        "image/",
                        ""
                      )
                      .toUpperCase() ||
                      "—"}
                  </strong>

                </div>


                <div>

                  <span>
                    Source
                  </span>

                  <strong className="valid-image-status">
                    {imageSource ===
                    "camera"
                      ? "Camera"
                      : "Upload"}
                  </strong>

                </div>

              </div>

            </div>

          )}


          <input
            ref={
              fileInputRef
            }
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={
              handleInputChange
            }
            hidden
          />


          {error && (

            <div className="detection-error-message">

              <Info
                size={16}
              />

              {error}

            </div>

          )}


          {!cameraOpen && (

            <>
              <div className="image-source-divider">

                <span />

                <p>
                  OR
                </p>

                <span />

              </div>


              <button
                type="button"
                className="camera-source-button"
                onClick={
                  openCamera
                }
                disabled={
                  analysisLoading
                }
              >
                <Camera
                  size={18}
                />

                Capture using Camera

                <span>
                  LIVE
                </span>

              </button>
            </>

          )}

        </div>


        {/* =================================================
            RIGHT SIDE
        ================================================= */}

        <aside className="detection-analysis-panel">

          <div className="analysis-panel-heading">

            <ScanSearch
              size={23}
            />

            <div>

              <span>
                STEP 02
              </span>

              <h2>
                AI Analysis
              </h2>

            </div>

          </div>


          {!selectedFile ? (

            <div className="analysis-empty-state">

              <div className="analysis-empty-icon">

                <ScanSearch
                  size={31}
                />

              </div>

              <h3>
                Waiting for an image
              </h3>

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

                  <h3>
                    Checking image quality
                  </h3>

                  <p>
                    BreedVision is analyzing resolution,
                    brightness and sharpness.
                  </p>

                </div>

              ) : (

                <ImageQualityPanel
                  quality={
                    quality
                  }
                />

              )}


              <div className="analysis-ready-state compact-analysis">

                <div className="analysis-ready-icon">

                  <ShieldCheck
                    size={28}
                  />

                </div>


                <span>
                  FRONTEND VALIDATION COMPLETE
                </span>


                <h3>
                  {quality?.suitable
                    ? "Ready for analysis"
                    : "Image can still be submitted"}
                </h3>


                <p>
                  Image quality checks are advisory.
                  FastAPI validates the image before
                  the detection record is stored.
                </p>


                <button
                  type="button"
                  className="analyze-animal-button"
                  onClick={
                    handleAnalyzeAnimal
                  }
                  disabled={
                    analysisLoading ||
                    qualityLoading ||
                    Boolean(
                      savedDetection
                    )
                  }
                >

                  {analysisLoading ? (

                    <>
                      <LoaderCircle
                        size={18}
                        className="quality-loading-spinner"
                      />

                      Analyzing & Saving...
                    </>

                  ) : savedDetection ? (

                    <>
                      <CheckCircle2
                        size={18}
                      />

                      Detection Saved
                    </>

                  ) : (

                    <>
                      <ScanSearch
                        size={18}
                      />

                      Analyze Animal
                    </>

                  )}

                </button>

              </div>


              {/* FASTAPI ERROR */}

              {backendError && (

                <div className="detection-persistence-message error">

                  <Info
                    size={17}
                  />

                  <div>

                    <strong>
                      Analysis failed
                    </strong>

                    <span>
                      {backendError}
                    </span>

                  </div>

                </div>

              )}


              {/* FASTAPI RESULT */}

              {backendResult && (

                <BackendResultPanel
                  result={
                    backendResult
                  }
                />

              )}


              {/* SUPABASE ERROR */}

              {persistenceError && (

                <div className="detection-persistence-message error">

                  <Database
                    size={17}
                  />

                  <div>

                    <strong>
                      Database save failed
                    </strong>

                    <span>
                      {persistenceError}
                    </span>

                  </div>

                </div>

              )}


              {/* SAVED */}

              {savedDetection && (

                <div className="detection-persistence-card">

                  <div className="detection-persistence-icon">

                    <Cloud
                      size={21}
                    />

                  </div>


                  <div>

                    <span>
                      SECURE STORAGE COMPLETE
                    </span>

                    <h4>
                      Detection saved successfully
                    </h4>

                    <p>
                      The private image and its
                      metadata are now linked to
                      your BreedVision account.
                    </p>

                  </div>


                  <div className="detection-persistence-details">

                    <div>

                      <span>
                        Record
                      </span>

                      <strong>
                        {savedDetection.id
                          ?.slice(
                            0,
                            8
                          )}
                        ...
                      </strong>

                    </div>


                    <div>

                      <span>
                        Source
                      </span>

                      <strong>
                        {savedDetection.source ===
                        "camera"
                          ? "Camera"
                          : "Upload"}
                      </strong>

                    </div>


                    <div>

                      <span>
                        Review
                      </span>

                      <strong>
                        Pending
                      </strong>

                    </div>

                  </div>

                </div>

              )}

            </>

          )}


          {/* HELP */}

          <div className="detection-help-card">

            <h4>
              For better accuracy
            </h4>

            <div>
              <span>
                01
              </span>

              <p>
                Keep the complete animal visible.
              </p>
            </div>

            <div>
              <span>
                02
              </span>

              <p>
                Use good lighting and avoid heavy blur.
              </p>
            </div>

            <div>
              <span>
                03
              </span>

              <p>
                Prefer one animal per image.
              </p>
            </div>

            <div>
              <span>
                04
              </span>

              <p>
                Side or front views work best.
              </p>
            </div>

          </div>

        </aside>

      </section>

    </div>
  );
}


export default Detection;