import {
  supabase,
} from "../../lib/supabaseClient";


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
        "You must be signed in to link detections."
      );
    }


    return user;
  };


export const getDetectionWithLinks =
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
          "detections"
        )
        .select(
          `
            *,
            farmers (
              id,
              full_name,
              phone,
              village,
              district
            ),
            animals (
              id,
              tag_number,
              name,
              species,
              verified_breed,
              farmer_id
            )
          `
        )
        .eq(
          "id",
          detectionId
        )
        .single();


    if (error) {
      throw error;
    }


    return data;
  };


export const linkDetectionToFarmer =
  async (
    detectionId,
    farmerId
  ) => {

    if (!detectionId) {

      throw new Error(
        "Detection ID is required."
      );
    }


    if (!farmerId) {

      throw new Error(
        "Farmer ID is required."
      );
    }


    await getCurrentUser();


    const {
      data:
        farmer,
      error:
        farmerError,
    } =
      await supabase
        .from(
          "farmers"
        )
        .select(
          "id"
        )
        .eq(
          "id",
          farmerId
        )
        .single();


    if (farmerError) {
      throw farmerError;
    }


    if (!farmer) {

      throw new Error(
        "Farmer not found."
      );
    }


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "detections"
        )
        .update(
          {
            farmer_id:
              farmerId,

            animal_id:
              null,
          }
        )
        .eq(
          "id",
          detectionId
        )
        .select()
        .single();


    if (error) {
      throw error;
    }


    return data;
  };


export const linkDetectionToAnimal =
  async (
    detectionId,
    animalId
  ) => {

    if (!detectionId) {

      throw new Error(
        "Detection ID is required."
      );
    }


    if (!animalId) {

      throw new Error(
        "Animal ID is required."
      );
    }


    await getCurrentUser();


    const {
      data:
        animal,
      error:
        animalError,
    } =
      await supabase
        .from(
          "animals"
        )
        .select(
          `
            id,
            farmer_id,
            species,
            verified_breed
          `
        )
        .eq(
          "id",
          animalId
        )
        .single();


    if (animalError) {
      throw animalError;
    }


    if (!animal) {

      throw new Error(
        "Animal not found."
      );
    }


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "detections"
        )
        .update(
          {
            animal_id:
              animal.id,

            farmer_id:
              animal.farmer_id ||
              null,
          }
        )
        .eq(
          "id",
          detectionId
        )
        .select()
        .single();


    if (error) {
      throw error;
    }


    return data;
  };


export const clearDetectionLinks =
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
          "detections"
        )
        .update(
          {
            farmer_id:
              null,

            animal_id:
              null,
          }
        )
        .eq(
          "id",
          detectionId
        )
        .select()
        .single();


    if (error) {
      throw error;
    }


    return data;
  };


export const getDetectionsByFarmer =
  async (
    farmerId
  ) => {

    if (!farmerId) {
      return [];
    }


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
        .eq(
          "farmer_id",
          farmerId
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


export const getDetectionsByAnimal =
  async (
    animalId
  ) => {

    if (!animalId) {
      return [];
    }


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
        .eq(
          "animal_id",
          animalId
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