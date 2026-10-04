import {
  supabase,
} from "../../lib/supabaseClient";


const VALID_DECISIONS = [
  "verified",
  "corrected",
  "rejected",
];


const cleanOptionalText = (
  value
) => {

  if (
    value === null ||
    value === undefined
  ) {
    return null;
  }


  const cleaned =
    String(
      value
    ).trim();


  return cleaned
    ? cleaned
    : null;
};


const getCurrentUser =
  async () => {

    const {
      data: {
        user,
      },
      error,
    } =
      await supabase.auth
        .getUser();


    if (error) {
      throw error;
    }


    if (!user) {

      throw new Error(
        "You must be signed in to review detections."
      );
    }


    return user;
  };


const validateReviewInput = ({
  detectionId,
  decision,
  reviewedSpecies,
  reviewedBreed,
}) => {

  if (!detectionId) {

    throw new Error(
      "Detection ID is required."
    );
  }


  if (
    !VALID_DECISIONS.includes(
      decision
    )
  ) {

    throw new Error(
      "Review decision must be verified, corrected or rejected."
    );
  }


  if (
    decision ===
    "corrected"
  ) {

    if (
      reviewedSpecies !==
        "cattle" &&
      reviewedSpecies !==
        "buffalo"
    ) {

      throw new Error(
        "Corrected species must be cattle or buffalo."
      );
    }


    if (
      !cleanOptionalText(
        reviewedBreed
      )
    ) {

      throw new Error(
        "Corrected breed is required."
      );
    }
  }
};


export const reviewDetection =
  async ({
    detectionId,
    decision,
    reviewedSpecies = null,
    reviewedBreed = null,
    notes = null,
  }) => {

    await getCurrentUser();


    validateReviewInput({
      detectionId,
      decision,
      reviewedSpecies,
      reviewedBreed,
    });


    const {
      data,
      error,
    } =
      await supabase.rpc(
        "review_detection",
        {
          p_detection_id:
            detectionId,

          p_decision:
            decision,

          p_reviewed_species:
            decision ===
            "corrected"
              ? reviewedSpecies
              : null,

          p_reviewed_breed:
            decision ===
            "corrected"
              ? cleanOptionalText(
                  reviewedBreed
                )
              : null,

          p_notes:
            cleanOptionalText(
              notes
            ),
        }
      );


    if (error) {
      throw error;
    }


    return data;
  };


export const getDetectionReview =
  async (
    detectionId
  ) => {

    if (!detectionId) {

      throw new Error(
        "Detection ID is required."
      );
    }


    await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "detection_reviews"
        )
        .select(
          "*"
        )
        .eq(
          "detection_id",
          detectionId
        )
        .maybeSingle();


    if (error) {
      throw error;
    }


    return data || null;
  };


export const getReviews =
  async () => {

    await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "detection_reviews"
        )
        .select(
          `
            *,
            detections (
              id,
              image_path,
              original_filename,
              species,
              predicted_breed,
              confidence,
              top_predictions,
              model_version,
              review_status,
              created_at
            )
          `
        )
        .order(
          "created_at",
          {
            ascending:
              false,
          }
        );


    if (error) {
      throw error;
    }


    return data || [];
  };


export const getPendingDetections =
  async () => {

    await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "detections"
        )
        .select(
          "*"
        )
        .in(
          "review_status",
          [
            "pending",
            "needs_review",
          ]
        )
        .order(
          "created_at",
          {
            ascending:
              false,
          }
        );


    if (error) {
      throw error;
    }


    return data || [];
  };


export const verifyDetection =
  async (
    detectionId,
    notes = null
  ) => {

    return reviewDetection({
      detectionId,
      decision:
        "verified",
      notes,
    });
  };


export const correctDetection =
  async ({
    detectionId,
    species,
    breed,
    notes = null,
  }) => {

    return reviewDetection({
      detectionId,

      decision:
        "corrected",

      reviewedSpecies:
        species,

      reviewedBreed:
        breed,

      notes,
    });
  };


export const rejectDetection =
  async (
    detectionId,
    notes = null
  ) => {

    return reviewDetection({
      detectionId,

      decision:
        "rejected",

      notes,
    });
  };