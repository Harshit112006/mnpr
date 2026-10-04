import {
  supabase,
} from "../../lib/supabaseClient";


const VALID_SEVERITIES = [
  "info",
  "warning",
  "critical",
];


const cleanRequiredText = (
  value,
  label
) => {

  const cleaned =
    String(
      value || ""
    ).trim();


  if (!cleaned) {

    throw new Error(
      `${label} is required.`
    );
  }


  return cleaned;
};


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
        "You must be signed in to manage alerts."
      );
    }


    return user;
  };


export const createAlert =
  async ({
    detectionId = null,
    animalId = null,
    alertType,
    severity = "info",
    title,
    message,
  }) => {

    const user =
      await getCurrentUser();


    if (
      !VALID_SEVERITIES.includes(
        severity
      )
    ) {

      throw new Error(
        "Invalid alert severity."
      );
    }


    const payload = {

      user_id:
        user.id,

      detection_id:
        cleanOptionalText(
          detectionId
        ),

      animal_id:
        cleanOptionalText(
          animalId
        ),

      alert_type:
        cleanRequiredText(
          alertType,
          "Alert type"
        ),

      severity,

      title:
        cleanRequiredText(
          title,
          "Alert title"
        ),

      message:
        cleanRequiredText(
          message,
          "Alert message"
        ),

      status:
        "unread",
    };


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "alerts"
        )
        .insert(
          payload
        )
        .select()
        .single();


    if (error) {
      throw error;
    }


    return data;
  };


export const getAlerts =
  async () => {

    await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "alerts"
        )
        .select(
          `
            *,
            detections (
              id,
              original_filename,
              predicted_breed,
              species,
              confidence,
              review_status,
              created_at
            ),
            animals (
              id,
              tag_number,
              name,
              species,
              verified_breed
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


export const getUnreadAlerts =
  async () => {

    await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "alerts"
        )
        .select(
          "*"
        )
        .eq(
          "status",
          "unread"
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


export const markAlertAsRead =
  async (
    alertId
  ) => {

    if (!alertId) {

      throw new Error(
        "Alert ID is required."
      );
    }


    await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "alerts"
        )
        .update(
          {
            status:
              "read",

            read_at:
              new Date()
                .toISOString(),
          }
        )
        .eq(
          "id",
          alertId
        )
        .select()
        .single();


    if (error) {
      throw error;
    }


    return data;
  };


export const dismissAlert =
  async (
    alertId
  ) => {

    if (!alertId) {

      throw new Error(
        "Alert ID is required."
      );
    }


    await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "alerts"
        )
        .update(
          {
            status:
              "dismissed",
          }
        )
        .eq(
          "id",
          alertId
        )
        .select()
        .single();


    if (error) {
      throw error;
    }


    return data;
  };


export const markAllAlertsAsRead =
  async () => {

    await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "alerts"
        )
        .update(
          {
            status:
              "read",

            read_at:
              new Date()
                .toISOString(),
          }
        )
        .eq(
          "status",
          "unread"
        )
        .select();


    if (error) {
      throw error;
    }


    return data || [];
  };


export const deleteAlert =
  async (
    alertId
  ) => {

    if (!alertId) {

      throw new Error(
        "Alert ID is required."
      );
    }


    await getCurrentUser();


    const {
      error,
    } =
      await supabase
        .from(
          "alerts"
        )
        .delete()
        .eq(
          "id",
          alertId
        );


    if (error) {
      throw error;
    }


    return {
      success:
        true,

      alertId,
    };
  };
  export const createDetectionReviewAlert =
  async ({
    detection,
    backendResult = null,
  }) => {

    if (!detection?.id) {

      throw new Error(
        "Detection record is required."
      );
    }


    const pipelineStatus =
      backendResult
        ?.pipeline_status ||
      null;


    const predictionStatus =
      backendResult
        ?.prediction
        ?.status ||
      null;


    if (
      pipelineStatus !==
        "no_bovine" &&
      predictionStatus !==
        "unknown" &&
      detection
        .review_status !==
        "needs_review"
    ) {

      return null;
    }


    let alertType =
      "review_required";


    let severity =
      "warning";


    let title =
      "Detection requires review";


    let message =
      "A detection requires manual verification.";


    if (
      pipelineStatus ===
      "no_bovine"
    ) {

      alertType =
        "no_bovine_detected";


      title =
        "No bovine detected";


      message =
        (
          "BreedVision could not detect a bovine "
          +
          "in the uploaded image. Manual review is recommended."
        );

    }

    else if (
      predictionStatus ===
      "unknown"
    ) {

      alertType =
        "unknown_breed";


      title =
        "Unknown breed prediction";


      message =
        (
          "A bovine was detected, but the breed "
          +
          "confidence was below the Phase-7 unknown threshold."
        );
    }


    return createAlert({
      detectionId:
        detection.id,

      alertType,

      severity,

      title,

      message,
    });
  };