import { supabase } from "../lib/supabaseClient";


/* =====================================================
   GET USER PROFILE
   ===================================================== */

export const getUserProfile = async (userId) => {
  if (!userId) {
    throw new Error("User ID is required.");
  }

  const { data, error } = await supabase
    .from("profiles")
    .select(`
      id,
      email,
      full_name,
      role,
      organization,
      avatar_url,
      created_at,
      updated_at
    `)
    .eq("id", userId)
    .single();

  if (error) {
    throw error;
  }

  return data;
};


/* =====================================================
   UPDATE USER PROFILE
   ===================================================== */

export const updateUserProfile = async (
  userId,
  updates
) => {
  if (!userId) {
    throw new Error("User ID is required.");
  }

  const allowedUpdates = {
    full_name: updates.full_name,
    role: updates.role,
    organization: updates.organization,
    avatar_url: updates.avatar_url,
  };

  const cleanedUpdates = Object.fromEntries(
    Object.entries(allowedUpdates).filter(
      ([, value]) => value !== undefined
    )
  );

  const { data, error } = await supabase
    .from("profiles")
    .update(cleanedUpdates)
    .eq("id", userId)
    .select(`
      id,
      email,
      full_name,
      role,
      organization,
      avatar_url,
      created_at,
      updated_at
    `)
    .single();

  if (error) {
    throw error;
  }

  return data;
};