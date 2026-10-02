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
/* =====================================================
   SIGN OUT
   ===================================================== */

export const signOutUser = async () => {
  const { error } =
    await supabase.auth.signOut();

  if (error) {
    throw error;
  }
};

/* =====================================================
   RESET PASSWORD REQUEST
   ===================================================== */

export const sendPasswordResetEmail = async (
  email
) => {
  const { data, error } =
    await supabase.auth.resetPasswordForEmail(
      email,
      {
        redirectTo:
          `${window.location.origin}/reset-password`,
      }
    );

  if (error) {
    throw error;
  }

  return data;
};
/* =====================================================
   UPDATE PASSWORD
   ===================================================== */

export const updateUserPassword = async (
  newPassword
) => {
  const { data, error } =
    await supabase.auth.updateUser({
      password: newPassword,
    });

  if (error) {
    throw error;
  }

  return data;
};