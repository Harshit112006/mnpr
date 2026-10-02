import { supabase } from "../lib/supabaseClient";

/* =====================================================
   SIGN UP
   ===================================================== */

export const signUpUser = async ({
  name,
  email,
  password,
  organization,
  role,
}) => {
  const { data, error } =
    await supabase.auth.signUp({
      email,
      password,

      options: {
        data: {
          full_name: name,
          organization,
          role,
        },
      },
    });

  if (error) {
    throw error;
  }

  return data;
};


/* =====================================================
   SIGN IN
   ===================================================== */

export const signInUser = async ({
  email,
  password,
}) => {
  const { data, error } =
    await supabase.auth.signInWithPassword({
      email,
      password,
    });

  if (error) {
    throw error;
  }

  return data;
};