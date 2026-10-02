import { supabase } from "../lib/supabaseClient";


const DETECTION_BUCKET = "detection-images";


/* =====================================================
   HELPERS
   ===================================================== */

const getCurrentUser = async () => {
  const {
    data: { user },
    error,
  } = await supabase.auth.getUser();

  if (error) {
    throw error;
  }

  if (!user) {
    throw new Error(
      "You must be signed in to save a detection."
    );
  }

  return user;
};


const sanitizeFileName = (fileName) => {
  return fileName
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9._-]/g, "-")
    .replace(/-+/g, "-");
};


const createUniqueId = () => {
  if (
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
  ) {
    return crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random()
    .toString(36)
    .slice(2)}`;
};


const buildStoragePath = (
  userId,
  file
) => {
  const now = new Date();

  const year =
    now.getFullYear();

  const month =
    String(
      now.getMonth() + 1
    ).padStart(2, "0");

  const uniqueId =
    createUniqueId();

  const safeName =
    sanitizeFileName(
      file.name ||
        "animal-image.jpg"
    );

  return `${userId}/${year}/${month}/${uniqueId}-${safeName}`;
};


const numberOrNull = (
  value
) => {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return null;
  }

  const parsed =
    Number(value);

  return Number.isFinite(parsed)
    ? parsed
    : null;
};


/* =====================================================
   SAVE DETECTION
   ===================================================== */

export const saveDetection = async ({
  file,
  source = "upload",
  quality = null,
  backendImage = null,
}) => {
  if (!file) {
    throw new Error(
      "Detection image is required."
    );
  }


  if (
    source !== "upload" &&
    source !== "camera"
  ) {
    throw new Error(
      "Invalid image source."
    );
  }


  const user =
    await getCurrentUser();


  const imagePath =
    buildStoragePath(
      user.id,
      file
    );


  /* =====================================================
     1. UPLOAD PRIVATE IMAGE
     ===================================================== */

  const {
    error: uploadError,
  } = await supabase.storage
    .from(DETECTION_BUCKET)
    .upload(
      imagePath,
      file,
      {
        cacheControl: "3600",
        contentType:
          file.type ||
          "image/jpeg",
        upsert: false,
      }
    );


  if (uploadError) {
    throw uploadError;
  }


  /* =====================================================
     2. NORMALIZE QUALITY VALUES
     ===================================================== */

  const qualityScore =
    numberOrNull(
      quality?.score ??
      quality?.qualityScore ??
      quality?.quality_score
    );


  const qualityStatus =
    quality
      ? quality.suitable
        ? "suitable"
        : "warning"
      : null;


  const imageWidth =
    numberOrNull(
      backendImage?.width ??
      quality?.width ??
      quality?.resolution?.width
    );


  const imageHeight =
    numberOrNull(
      backendImage?.height ??
      quality?.height ??
      quality?.resolution?.height
    );


  /* =====================================================
     3. DATABASE RECORD
     ===================================================== */

  const detectionPayload = {
    user_id:
      user.id,

    image_path:
      imagePath,

    original_filename:
      file.name,

    mime_type:
      file.type || null,

    file_size_bytes:
      file.size,

    image_width:
      imageWidth,

    image_height:
      imageHeight,

    image_format:
      backendImage?.format ||
      file.type
        ?.replace("image/", "")
        ?.toUpperCase() ||
      null,

    quality_score:
      qualityScore,

    quality_status:
      qualityStatus,

    source,

    /*
      ML is not connected yet.

      species,
      predicted_breed,
      confidence,
      top_predictions,
      model_version

      remain NULL in Supabase.
    */

    review_status:
      "pending",
  };


  const {
    data,
    error: databaseError,
  } = await supabase
    .from("detections")
    .insert(
      detectionPayload
    )
    .select()
    .single();


  /* =====================================================
     ROLLBACK STORAGE IF DB INSERT FAILS
     ===================================================== */

  if (databaseError) {
    await supabase.storage
      .from(DETECTION_BUCKET)
      .remove([
        imagePath,
      ]);

    throw databaseError;
  }


  return {
    detection:
      data,

    imagePath,
  };
};


/* =====================================================
   GET CURRENT USER DETECTIONS
   Used later by History page.
   ===================================================== */

export const getUserDetections =
  async () => {
    const {
      data,
      error,
    } = await supabase
      .from("detections")
      .select("*")
      .order(
        "created_at",
        {
          ascending: false,
        }
      );


    if (error) {
      throw error;
    }


    return data || [];
  };


/* =====================================================
   CREATE PRIVATE SIGNED IMAGE URL
   ===================================================== */

export const getDetectionImageUrl =
  async (
    imagePath,
    expiresIn = 3600
  ) => {
    if (!imagePath) {
      return null;
    }


    const {
      data,
      error,
    } = await supabase.storage
      .from(DETECTION_BUCKET)
      .createSignedUrl(
        imagePath,
        expiresIn
      );


    if (error) {
      throw error;
    }


    return data?.signedUrl ||
      null;
  };


/* =====================================================
   DELETE DETECTION
   ===================================================== */

export const deleteDetection =
  async (
    detection
  ) => {
    if (!detection?.id) {
      throw new Error(
        "Detection ID is required."
      );
    }


    if (
      detection.image_path
    ) {
      const {
        error: storageError,
      } = await supabase.storage
        .from(DETECTION_BUCKET)
        .remove([
          detection.image_path,
        ]);


      if (storageError) {
        throw storageError;
      }
    }


    const {
      error,
    } = await supabase
      .from("detections")
      .delete()
      .eq(
        "id",
        detection.id
      );


    if (error) {
      throw error;
    }
  };