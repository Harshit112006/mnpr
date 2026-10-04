import {
  supabase,
} from "../../lib/supabaseClient";


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
        "You must be signed in to manage animals."
      );
    }


    return user;
  };


const validateSpecies = (
  species
) => {

  const cleaned =
    cleanOptionalText(
      species
    );


  if (
    cleaned !== "cattle" &&
    cleaned !== "buffalo"
  ) {

    throw new Error(
      "Species must be cattle or buffalo."
    );
  }


  return cleaned;
};


const validateSex = (
  sex
) => {

  const cleaned =
    cleanOptionalText(
      sex
    );


  if (!cleaned) {
    return null;
  }


  if (
    ![
      "male",
      "female",
      "unknown",
    ].includes(
      cleaned
    )
  ) {

    throw new Error(
      "Invalid animal sex."
    );
  }


  return cleaned;
};


const buildAnimalPayload = (
  animal
) => {

  return {

    farmer_id:
      cleanOptionalText(
        animal?.farmer_id
      ),

    tag_number:
      cleanOptionalText(
        animal?.tag_number
      ),

    name:
      cleanOptionalText(
        animal?.name
      ),

    species:
      validateSpecies(
        animal?.species
      ),

    verified_breed:
      cleanOptionalText(
        animal?.verified_breed
      ),

    sex:
      validateSex(
        animal?.sex
      ),

    date_of_birth:
      cleanOptionalText(
        animal?.date_of_birth
      ),

    color_markings:
      cleanOptionalText(
        animal?.color_markings
      ),

    notes:
      cleanOptionalText(
        animal?.notes
      ),
  };
};


export const createAnimal =
  async (
    animal
  ) => {

    const user =
      await getCurrentUser();


    const payload = {

      user_id:
        user.id,

      ...buildAnimalPayload(
        animal
      ),
    };


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "animals"
        )
        .insert(
          payload
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
            )
          `
        )
        .single();


    if (error) {
      throw error;
    }


    return data;
  };


export const getAnimals =
  async () => {

    await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "animals"
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


export const getAnimalById =
  async (
    animalId
  ) => {

    if (!animalId) {

      throw new Error(
        "Animal ID is required."
      );
    }


    await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "animals"
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
            )
          `
        )
        .eq(
          "id",
          animalId
        )
        .single();


    if (error) {
      throw error;
    }


    return data;
  };


export const updateAnimal =
  async (
    animalId,
    updates
  ) => {

    if (!animalId) {

      throw new Error(
        "Animal ID is required."
      );
    }


    await getCurrentUser();


    const payload =
      buildAnimalPayload(
        updates
      );


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "animals"
        )
        .update(
          payload
        )
        .eq(
          "id",
          animalId
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
            )
          `
        )
        .single();


    if (error) {
      throw error;
    }


    return data;
  };


export const deleteAnimal =
  async (
    animalId
  ) => {

    if (!animalId) {

      throw new Error(
        "Animal ID is required."
      );
    }


    await getCurrentUser();


    const {
      error,
    } =
      await supabase
        .from(
          "animals"
        )
        .delete()
        .eq(
          "id",
          animalId
        );


    if (error) {
      throw error;
    }


    return {
      success:
        true,

      animalId,
    };
  };


export const getAnimalsByFarmer =
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
          "animals"
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
            )
          `
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


export const searchAnimals =
  async (
    query
  ) => {

    await getCurrentUser();


    const cleanedQuery =
      String(
        query || ""
      ).trim();


    if (!cleanedQuery) {

      return getAnimals();
    }


    const safeQuery =
      cleanedQuery
        .replace(
          /[%_,]/g,
          ""
        );


    if (!safeQuery) {
      return [];
    }


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "animals"
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
            )
          `
        )
        .or(
          [
            `name.ilike.%${safeQuery}%`,
            `tag_number.ilike.%${safeQuery}%`,
            `verified_breed.ilike.%${safeQuery}%`,
          ].join(",")
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