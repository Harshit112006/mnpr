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
        "You must be signed in to manage farmers."
      );
    }


    return user;
  };


const buildFarmerPayload = (
  farmer
) => {

  const fullName =
    cleanOptionalText(
      farmer?.full_name
    );


  if (!fullName) {

    throw new Error(
      "Farmer name is required."
    );
  }


  return {

    full_name:
      fullName,

    phone:
      cleanOptionalText(
        farmer?.phone
      ),

    email:
      cleanOptionalText(
        farmer?.email
      ),

    village:
      cleanOptionalText(
        farmer?.village
      ),

    district:
      cleanOptionalText(
        farmer?.district
      ),

    state:
      cleanOptionalText(
        farmer?.state
      ),

    postal_code:
      cleanOptionalText(
        farmer?.postal_code
      ),

    notes:
      cleanOptionalText(
        farmer?.notes
      ),
  };
};


export const createFarmer =
  async (
    farmer
  ) => {

    const user =
      await getCurrentUser();


    const payload = {
      user_id:
        user.id,

      ...buildFarmerPayload(
        farmer
      ),
    };


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "farmers"
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


export const getFarmers =
  async () => {

    await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "farmers"
        )
        .select(
          "*"
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


export const getFarmerById =
  async (
    farmerId
  ) => {

    if (!farmerId) {

      throw new Error(
        "Farmer ID is required."
      );
    }


    await getCurrentUser();


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "farmers"
        )
        .select(
          "*"
        )
        .eq(
          "id",
          farmerId
        )
        .single();


    if (error) {
      throw error;
    }


    return data;
  };


export const updateFarmer =
  async (
    farmerId,
    updates
  ) => {

    if (!farmerId) {

      throw new Error(
        "Farmer ID is required."
      );
    }


    await getCurrentUser();


    const payload =
      buildFarmerPayload(
        updates
      );


    const {
      data,
      error,
    } =
      await supabase
        .from(
          "farmers"
        )
        .update(
          payload
        )
        .eq(
          "id",
          farmerId
        )
        .select()
        .single();


    if (error) {
      throw error;
    }


    return data;
  };


export const deleteFarmer =
  async (
    farmerId
  ) => {

    if (!farmerId) {

      throw new Error(
        "Farmer ID is required."
      );
    }


    await getCurrentUser();


    const {
      error,
    } =
      await supabase
        .from(
          "farmers"
        )
        .delete()
        .eq(
          "id",
          farmerId
        );


    if (error) {
      throw error;
    }


    return {
      success:
        true,

      farmerId,
    };
  };


export const searchFarmers =
  async (
    query
  ) => {

    await getCurrentUser();


    const cleanedQuery =
      String(
        query || ""
      ).trim();


    if (!cleanedQuery) {

      return getFarmers();
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
          "farmers"
        )
        .select(
          "*"
        )
        .or(
          [
            `full_name.ilike.%${safeQuery}%`,
            `phone.ilike.%${safeQuery}%`,
            `village.ilike.%${safeQuery}%`,
            `district.ilike.%${safeQuery}%`,
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