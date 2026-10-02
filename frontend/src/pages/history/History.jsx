import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  AlertCircle,
  Camera,
  CheckCircle2,
  Clock3,
  FileImage,
  History as HistoryIcon,
  ImageOff,
  LoaderCircle,
  RefreshCw,
  Search,
  ShieldCheck,
  Trash2,
  Upload,
} from "lucide-react";

import {
  deleteDetection,
  getDetectionImageUrl,
  getUserDetections,
} from "../../services/detectionDataService";

import "../../styles/History.css";


function History() {
  const [
    detections,
    setDetections,
  ] = useState([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");

  const [
    search,
    setSearch,
  ] = useState("");

  const [
    deletingId,
    setDeletingId,
  ] = useState(null);


  /* =====================================================
     LOAD DETECTIONS
     ===================================================== */

  const loadDetections =
    useCallback(async () => {
      try {
        setLoading(true);

        setError("");


        const records =
          await getUserDetections();


        const recordsWithImages =
          await Promise.all(
            records.map(
              async (
                detection
              ) => {
                try {
                  const signedUrl =
                    await getDetectionImageUrl(
                      detection.image_path
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
                    "Unable to create signed image URL:",
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


        setDetections(
          recordsWithImages
        );

      } catch (
        historyError
      ) {
        console.error(
          "Detection history error:",
          historyError
        );


        setError(
          historyError.message ||
          "Unable to load detection history."
        );

      } finally {
        setLoading(false);
      }
    }, []);


  useEffect(() => {
    loadDetections();
  }, [
    loadDetections,
  ]);


  /* =====================================================
     DELETE DETECTION
     ===================================================== */

  const handleDelete =
    async (
      detection
    ) => {
      const confirmed =
        window.confirm(
          "Delete this detection permanently? The stored image and database record will both be removed."
        );


      if (!confirmed) {
        return;
      }


      try {
        setDeletingId(
          detection.id
        );

        setError("");


        await deleteDetection(
          detection
        );


        setDetections(
          (
            previous
          ) =>
            previous.filter(
              (item) =>
                item.id !==
                detection.id
            )
        );

      } catch (
        deleteError
      ) {
        console.error(
          "Delete detection error:",
          deleteError
        );


        setError(
          deleteError.message ||
          "Unable to delete the detection."
        );

      } finally {
        setDeletingId(
          null
        );
      }
    };


  /* =====================================================
     SEARCH
     ===================================================== */

  const filteredDetections =
    useMemo(() => {
      const query =
        search
          .trim()
          .toLowerCase();


      if (!query) {
        return detections;
      }


      return detections.filter(
        (
          detection
        ) => {
          const values = [
            detection.original_filename,
            detection.source,
            detection.review_status,
            detection.species,
            detection.predicted_breed,
          ];


          return values.some(
            (
              value
            ) =>
              value
                ?.toString()
                .toLowerCase()
                .includes(
                  query
                )
          );
        }
      );

    }, [
      detections,
      search,
    ]);


  /* =====================================================
     HELPERS
     ===================================================== */

  const formatDate = (
    value
  ) => {
    if (!value) {
      return "—";
    }


    return new Date(
      value
    ).toLocaleString(
      "en-IN",
      {
        day: "2-digit",

        month: "short",

        year: "numeric",

        hour: "2-digit",

        minute:
          "2-digit",
      }
    );
  };


  const formatFileSize = (
    bytes
  ) => {
    if (
      !bytes &&
      bytes !== 0
    ) {
      return "—";
    }


    return `${(
      bytes /
      1024 /
      1024
    ).toFixed(2)} MB`;
  };


  const formatRoleText = (
    value
  ) => {
    if (!value) {
      return "—";
    }


    return value
      .replaceAll(
        "_",
        " "
      )
      .replace(
        /\b\w/g,
        (
          character
        ) =>
          character.toUpperCase()
      );
  };


  /* =====================================================
     LOADING
     ===================================================== */

  if (loading) {
    return (
      <div className="history-loading-state">

        <LoaderCircle
          size={31}
          className="history-spinner"
        />

        <h3>
          Loading detection history
        </h3>

        <p>
          Retrieving your private BreedVision records...
        </p>

      </div>
    );
  }


  return (
    <div className="history-page">

      {/* =================================================
          HEADER
      ================================================= */}

      <section className="history-header">

        <div>

          <span className="history-eyebrow">
            BREEDVISION RECORDS
          </span>

          <h1>
            Detection History
          </h1>

          <p>
            Review images and metadata securely stored
            under your BreedVision account.
          </p>

        </div>


        <button
          type="button"
          className="history-refresh-button"
          onClick={
            loadDetections
          }
        >
          <RefreshCw
            size={16}
          />

          Refresh
        </button>

      </section>


      {/* =================================================
          SUMMARY
      ================================================= */}

      <section className="history-summary-grid">

        <div className="history-summary-card">

          <div className="history-summary-icon">

            <HistoryIcon
              size={19}
            />

          </div>

          <div>

            <span>
              Total Records
            </span>

            <strong>
              {detections.length}
            </strong>

          </div>

        </div>


        <div className="history-summary-card">

          <div className="history-summary-icon">

            <Upload
              size={19}
            />

          </div>

          <div>

            <span>
              Uploaded
            </span>

            <strong>
              {
                detections.filter(
                  (
                    item
                  ) =>
                    item.source ===
                    "upload"
                ).length
              }
            </strong>

          </div>

        </div>


        <div className="history-summary-card">

          <div className="history-summary-icon">

            <Camera
              size={19}
            />

          </div>

          <div>

            <span>
              Camera
            </span>

            <strong>
              {
                detections.filter(
                  (
                    item
                  ) =>
                    item.source ===
                    "camera"
                ).length
              }
            </strong>

          </div>

        </div>


        <div className="history-summary-card">

          <div className="history-summary-icon">

            <ShieldCheck
              size={19}
            />

          </div>

          <div>

            <span>
              Pending Review
            </span>

            <strong>
              {
                detections.filter(
                  (
                    item
                  ) =>
                    item.review_status ===
                    "pending"
                ).length
              }
            </strong>

          </div>

        </div>

      </section>


      {/* =================================================
          TOOLBAR
      ================================================= */}

      <section className="history-toolbar">

        <div className="history-search">

          <Search
            size={17}
          />

          <input
            type="text"
            placeholder="Search filename, source, breed or status..."
            value={
              search
            }
            onChange={
              (
                event
              ) =>
                setSearch(
                  event.target.value
                )
            }
          />

        </div>


        <span className="history-result-count">
          {filteredDetections.length}
          {" "}
          record
          {filteredDetections.length ===
          1
            ? ""
            : "s"}
        </span>

      </section>


      {/* ERROR */}

      {error && (

        <div className="history-error">

          <AlertCircle
            size={17}
          />

          <span>
            {error}
          </span>

        </div>

      )}


      {/* =================================================
          EMPTY STATE
      ================================================= */}

      {detections.length ===
      0 ? (

        <section className="history-empty-state">

          <div className="history-empty-icon">

            <FileImage
              size={31}
            />

          </div>

          <h2>
            No detections yet
          </h2>

          <p>
            Analyze your first cattle or buffalo image
            to create a secure detection record.
          </p>

        </section>

      ) : filteredDetections.length ===
        0 ? (

        <section className="history-empty-state">

          <div className="history-empty-icon">

            <Search
              size={30}
            />

          </div>

          <h2>
            No matching detections
          </h2>

          <p>
            Try searching with a different filename,
            source or status.
          </p>

        </section>

      ) : (

        /* ===============================================
           HISTORY CARDS
        =============================================== */

        <section className="history-list">

          {filteredDetections.map(
            (
              detection
            ) => (

              <article
                className="history-record-card"
                key={
                  detection.id
                }
              >

                {/* IMAGE */}

                <div className="history-record-image">

                  {detection.signed_url ? (

                    <img
                      src={
                        detection.signed_url
                      }
                      alt={
                        detection.original_filename ||
                        "Detection"
                      }
                    />

                  ) : (

                    <div className="history-image-unavailable">

                      <ImageOff
                        size={27}
                      />

                      <span>
                        Image unavailable
                      </span>

                    </div>

                  )}


                  <span className={`history-source-badge ${detection.source}`}>

                    {detection.source ===
                    "camera" ? (

                      <Camera
                        size={12}
                      />

                    ) : (

                      <Upload
                        size={12}
                      />

                    )}

                    {formatRoleText(
                      detection.source
                    )}

                  </span>

                </div>


                {/* INFORMATION */}

                <div className="history-record-content">

                  <div className="history-record-top">

                    <div>

                      <span>
                        DETECTION RECORD
                      </span>

                      <h2>
                        {detection.original_filename ||
                          "Animal Image"}
                      </h2>

                    </div>


                    <span className={`history-review-status ${detection.review_status}`}>

                      {formatRoleText(
                        detection.review_status
                      )}

                    </span>

                  </div>


                  <div className="history-record-details">

                    <div>

                      <span>
                        Resolution
                      </span>

                      <strong>
                        {detection.image_width &&
                        detection.image_height
                          ? `${detection.image_width} × ${detection.image_height}`
                          : "—"}
                      </strong>

                    </div>


                    <div>

                      <span>
                        File Size
                      </span>

                      <strong>
                        {formatFileSize(
                          detection.file_size_bytes
                        )}
                      </strong>

                    </div>


                    <div>

                      <span>
                        Quality
                      </span>

                      <strong>
                        {detection.quality_score !==
                        null
                          ? `${Number(
                              detection.quality_score
                            ).toFixed(
                              0
                            )}%`
                          : "—"}
                      </strong>

                    </div>


                    <div>

                      <span>
                        Breed
                      </span>

                      <strong>
                        {detection.predicted_breed ||
                          "Awaiting ML"}
                      </strong>

                    </div>

                  </div>


                  <div className="history-record-footer">

                    <div className="history-record-time">

                      <Clock3
                        size={14}
                      />

                      <span>
                        {formatDate(
                          detection.created_at
                        )}
                      </span>

                    </div>


                    <button
                      type="button"
                      className="history-delete-button"
                      onClick={() =>
                        handleDelete(
                          detection
                        )
                      }
                      disabled={
                        deletingId ===
                        detection.id
                      }
                    >

                      {deletingId ===
                      detection.id ? (

                        <LoaderCircle
                          size={15}
                          className="history-spinner"
                        />

                      ) : (

                        <Trash2
                          size={15}
                        />

                      )}

                      {deletingId ===
                      detection.id
                        ? "Deleting..."
                        : "Delete"}

                    </button>

                  </div>

                </div>

              </article>

            )
          )}

        </section>

      )}

    </div>
  );
}


export default History;