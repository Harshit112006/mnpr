import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  AlertCircle,
  CheckCircle2,
  ClipboardCheck,
  ImageOff,
  LoaderCircle,
  RefreshCw,
  ShieldX,
  X,
} from "lucide-react";

import {
  correctDetection,
  getPendingDetections,
  getReviews,
  rejectDetection,
  verifyDetection,
} from "../../services/phase9/reviewService";

import {
  getFarmers,
} from "../../services/phase9/farmerService";

import {
  getAnimals,
} from "../../services/phase9/animalService";

import {
  linkDetectionToAnimal,
  linkDetectionToFarmer,
} from "../../services/phase9/detectionLinkService";

import {
  getDetectionImageUrl,
} from "../../services/detectionDataService";

import "../../styles/Phase9.css";


function ReviewCenter() {

  const [pending, setPending] =
    useState([]);

  const [reviews, setReviews] =
    useState([]);

  const [farmers, setFarmers] =
    useState([]);

  const [animals, setAnimals] =
    useState([]);

  const [selected, setSelected] =
    useState(null);

  const [decision, setDecision] =
    useState("verified");

  const [
    reviewedSpecies,
    setReviewedSpecies,
  ] =
    useState("cattle");

  const [
    reviewedBreed,
    setReviewedBreed,
  ] =
    useState("");

  const [
    notes,
    setNotes,
  ] =
    useState("");

  const [
    farmerId,
    setFarmerId,
  ] =
    useState("");

  const [
    animalId,
    setAnimalId,
  ] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");


  const loadData =
    useCallback(async () => {

      try {

        setLoading(true);
        setError("");


        const [
          pendingRows,
          reviewRows,
          farmerRows,
          animalRows,
        ] =
          await Promise.all([
            getPendingDetections(),
            getReviews(),
            getFarmers(),
            getAnimals(),
          ]);


        const withImages =
          await Promise.all(
            pendingRows.map(
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

                }

                catch {

                  return {
                    ...detection,
                    signed_url:
                      null,
                  };
                }
              }
            )
          );


        setPending(
          withImages
        );

        setReviews(
          reviewRows
        );

        setFarmers(
          farmerRows
        );

        setAnimals(
          animalRows
        );

      }

      catch (
        loadError
      ) {

        setError(
          loadError.message ||
          "Unable to load review center."
        );

      }

      finally {

        setLoading(false);

      }

    }, []);


  useEffect(() => {
    loadData();
  }, [
    loadData,
  ]);


  const startReview = (
    detection
  ) => {

    const canVerify =
      Boolean(
        detection.species &&
        detection.predicted_breed
      );


    setSelected(
      detection
    );

    setDecision(
      canVerify
        ? "verified"
        : "corrected"
    );

    setReviewedSpecies(
      detection.species ||
      "cattle"
    );

    setReviewedBreed(
      detection.predicted_breed ||
      ""
    );

    setNotes("");

    setFarmerId(
      detection.farmer_id ||
      ""
    );

    setAnimalId(
      detection.animal_id ||
      ""
    );
  };


  const closeReview = () => {

    setSelected(
      null
    );

    setNotes("");

    setAnimalId("");

    setFarmerId("");
  };


  const availableAnimals =
    useMemo(() => {

      if (!farmerId) {
        return animals;
      }


      return animals.filter(
        (
          animal
        ) =>
          animal.farmer_id ===
          farmerId
      );

    }, [
      animals,
      farmerId,
    ]);


  const submitReview =
    async (
      event
    ) => {

      event.preventDefault();


      if (!selected) {
        return;
      }


      try {

        setSaving(true);
        setError("");


        if (animalId) {

          await linkDetectionToAnimal(
            selected.id,
            animalId
          );

        }

        else if (farmerId) {

          await linkDetectionToFarmer(
            selected.id,
            farmerId
          );
        }


        if (
          decision ===
          "verified"
        ) {

          await verifyDetection(
            selected.id,
            notes
          );

        }

        else if (
          decision ===
          "corrected"
        ) {

          await correctDetection({
            detectionId:
              selected.id,

            species:
              reviewedSpecies,

            breed:
              reviewedBreed,

            notes,
          });

        }

        else {

          await rejectDetection(
            selected.id,
            notes
          );
        }


        closeReview();

        await loadData();

      }

      catch (
        reviewError
      ) {

        console.error(
          "Review error:",
          reviewError
        );


        setError(
          reviewError.message ||
          "Unable to save human review."
        );

      }

      finally {

        setSaving(false);

      }

    };


  if (loading) {

    return (
      <div className="phase9-loading">
        <LoaderCircle
          className="phase9-spinner"
          size={32}
        />
        <h3>
          Loading review queue
        </h3>
      </div>
    );
  }


  return (
    <div className="phase9-page">

      <section className="phase9-header">

        <div>
          <span className="phase9-eyebrow">
            HUMAN-IN-THE-LOOP
          </span>

          <h1>
            Review Center
          </h1>

          <p>
            Verify, correct or reject model
            predictions without overwriting the
            original AI evidence.
          </p>
        </div>


        <button
          type="button"
          className="phase9-secondary"
          onClick={
            loadData
          }
        >
          <RefreshCw size={16} />
          Refresh
        </button>

      </section>


      <section className="phase9-summary-grid">

        <div className="phase9-summary-card">
          <ClipboardCheck size={21} />
          <div>
            <span>
              Pending
            </span>
            <strong>
              {pending.length}
            </strong>
          </div>
        </div>


        <div className="phase9-summary-card">
          <CheckCircle2 size={21} />
          <div>
            <span>
              Completed Reviews
            </span>
            <strong>
              {reviews.length}
            </strong>
          </div>
        </div>


        <div className="phase9-summary-card">
          <ShieldX size={21} />
          <div>
            <span>
              Rejected
            </span>
            <strong>
              {
                reviews.filter(
                  (
                    review
                  ) =>
                    review.decision ===
                    "rejected"
                ).length
              }
            </strong>
          </div>
        </div>

      </section>


      {error && (
        <div className="phase9-error">
          <AlertCircle size={17} />
          {error}
        </div>
      )}


      <section>

        <div className="phase9-section-heading">
          <div>
            <span>
              REVIEW QUEUE
            </span>
            <h2>
              Detections requiring attention
            </h2>
          </div>
        </div>


        {
          pending.length ===
          0 ? (

            <div className="phase9-empty">
              <CheckCircle2 size={35} />
              <h2>
                Review queue is clear
              </h2>
            </div>

          ) : (

            <div className="review-list">

              {
                pending.map(
                  (
                    detection
                  ) => (

                    <article
                      key={detection.id}
                      className="review-card"
                    >

                      <div className="review-image">

                        {
                          detection.signed_url
                            ? (
                              <img
                                src={
                                  detection.signed_url
                                }
                                alt="Detection"
                              />
                            )
                            : (
                              <div className="review-image-missing">
                                <ImageOff size={28} />
                              </div>
                            )
                        }

                      </div>


                      <div className="review-content">

                        <div className="review-top">

                          <div>
                            <span>
                              {
                                detection.review_status
                                  ?.replaceAll(
                                    "_",
                                    " "
                                  )
                                  .toUpperCase()
                              }
                            </span>

                            <h3>
                              {
                                detection.predicted_breed ||
                                "Unknown prediction"
                              }
                            </h3>
                          </div>


                          <button
                            type="button"
                            className="phase9-primary"
                            onClick={() =>
                              startReview(
                                detection
                              )
                            }
                          >
                            Review
                          </button>

                        </div>


                        <div className="phase9-detail-grid">

                          <div>
                            <span>
                              Species
                            </span>
                            <strong>
                              {
                                detection.species ||
                                "Unknown"
                              }
                            </strong>
                          </div>


                          <div>
                            <span>
                              Confidence
                            </span>
                            <strong>
                              {
                                detection.confidence !==
                                null
                                  ? `${(
                                      Number(
                                        detection.confidence
                                      ) * 100
                                    ).toFixed(2)}%`
                                  : "—"
                              }
                            </strong>
                          </div>


                          <div>
                            <span>
                              Source
                            </span>
                            <strong>
                              {detection.source}
                            </strong>
                          </div>


                          <div>
                            <span>
                              Model
                            </span>
                            <strong>
                              {
                                detection.model_version ||
                                "—"
                              }
                            </strong>
                          </div>

                        </div>

                      </div>

                    </article>

                  )
                )
              }

            </div>

          )
        }

      </section>


      <section>

        <div className="phase9-section-heading">
          <div>
            <span>
              AUDIT TRAIL
            </span>
            <h2>
              Completed human reviews
            </h2>
          </div>
        </div>


        <div className="phase9-table-wrap">

          <table className="phase9-table">

            <thead>
              <tr>
                <th>Decision</th>
                <th>Original</th>
                <th>Reviewed</th>
                <th>Notes</th>
                <th>Date</th>
              </tr>
            </thead>


            <tbody>

              {
                reviews.length ===
                0 ? (

                  <tr>
                    <td colSpan="5">
                      No reviews completed yet.
                    </td>
                  </tr>

                ) : (

                  reviews.map(
                    (
                      review
                    ) => (

                      <tr key={review.id}>

                        <td>
                          {review.decision}
                        </td>

                        <td>
                          {
                            review.original_breed ||
                            "Unknown"
                          }
                        </td>

                        <td>
                          {
                            review.reviewed_breed ||
                            "—"
                          }
                        </td>

                        <td>
                          {review.notes || "—"}
                        </td>

                        <td>
                          {
                            new Date(
                              review.created_at
                            ).toLocaleString(
                              "en-IN"
                            )
                          }
                        </td>

                      </tr>

                    )
                  )
                )
              }

            </tbody>

          </table>

        </div>

      </section>


      {selected && (

        <div className="phase9-modal-backdrop">

          <form
            className="phase9-modal"
            onSubmit={
              submitReview
            }
          >

            <div className="phase9-form-header">

              <div>
                <span>
                  HUMAN REVIEW
                </span>

                <h2>
                  Review detection
                </h2>
              </div>


              <button
                type="button"
                className="phase9-icon-button"
                onClick={
                  closeReview
                }
              >
                <X size={18} />
              </button>

            </div>


            <div className="phase9-field">
              <label>
                Decision
              </label>

              <select
                value={
                  decision
                }
                onChange={
                  (
                    event
                  ) =>
                    setDecision(
                      event.target.value
                    )
                }
              >

                <option
                  value="verified"
                  disabled={
                    !selected.species ||
                    !selected.predicted_breed
                  }
                >
                  Verify model prediction
                </option>

                <option value="corrected">
                  Correct prediction
                </option>

                <option value="rejected">
                  Reject detection
                </option>

              </select>
            </div>


            {decision ===
              "corrected" && (

              <>

                <div className="phase9-field">
                  <label>
                    Correct Species
                  </label>

                  <select
                    value={
                      reviewedSpecies
                    }
                    onChange={
                      (
                        event
                      ) =>
                        setReviewedSpecies(
                          event.target.value
                        )
                    }
                  >
                    <option value="cattle">
                      Cattle
                    </option>

                    <option value="buffalo">
                      Buffalo
                    </option>
                  </select>
                </div>


                <div className="phase9-field">
                  <label>
                    Correct Breed *
                  </label>

                  <input
                    value={
                      reviewedBreed
                    }
                    onChange={
                      (
                        event
                      ) =>
                        setReviewedBreed(
                          event.target.value
                        )
                    }
                    required
                  />
                </div>

              </>

            )}


            <div className="phase9-field">
              <label>
                Farmer
              </label>

              <select
                value={
                  farmerId
                }
                onChange={
                  (
                    event
                  ) => {

                    setFarmerId(
                      event.target.value
                    );

                    setAnimalId("");
                  }
                }
              >

                <option value="">
                  Unassigned
                </option>

                {
                  farmers.map(
                    (
                      farmer
                    ) => (
                      <option
                        key={farmer.id}
                        value={farmer.id}
                      >
                        {farmer.full_name}
                      </option>
                    )
                  )
                }

              </select>
            </div>


            <div className="phase9-field">
              <label>
                Animal
              </label>

              <select
                value={
                  animalId
                }
                onChange={
                  (
                    event
                  ) =>
                    setAnimalId(
                      event.target.value
                    )
                }
              >

                <option value="">
                  Unassigned
                </option>

                {
                  availableAnimals.map(
                    (
                      animal
                    ) => (
                      <option
                        key={animal.id}
                        value={animal.id}
                      >
                        {
                          animal.name ||
                          animal.tag_number ||
                          animal.id
                        }
                      </option>
                    )
                  )
                }

              </select>
            </div>


            <div className="phase9-field">
              <label>
                Notes
              </label>

              <textarea
                rows={3}
                value={
                  notes
                }
                onChange={
                  (
                    event
                  ) =>
                    setNotes(
                      event.target.value
                    )
                }
              />
            </div>


            <button
              type="submit"
              className="phase9-primary phase9-full-button"
              disabled={
                saving
              }
            >
              {
                saving
                  ? (
                    <LoaderCircle
                      className="phase9-spinner"
                      size={16}
                    />
                  )
                  : (
                    <ClipboardCheck
                      size={16}
                    />
                  )
              }

              {
                saving
                  ? "Saving..."
                  : "Save Review"
              }
            </button>

          </form>

        </div>

      )}

    </div>
  );
}


export default ReviewCenter;