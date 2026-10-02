import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

import { supabase } from "../lib/supabaseClient";

import {
  getUserProfile,
} from "../services/profileService";


const AuthContext =
  createContext(null);


export function AuthProvider({
  children,
}) {
  const [session, setSession] =
    useState(null);

  const [user, setUser] =
    useState(null);

  const [profile, setProfile] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [profileLoading, setProfileLoading] =
    useState(false);


  /* =====================================================
     LOAD PROFILE FROM public.profiles
     ===================================================== */

  const loadProfile = useCallback(
    async (userId) => {
      if (!userId) {
        setProfile(null);

        return null;
      }

      try {
        setProfileLoading(true);

        const profileData =
          await getUserProfile(
            userId
          );

        setProfile(profileData);

        return profileData;

      } catch (profileError) {
        console.error(
          "Unable to load user profile:",
          profileError
        );

        setProfile(null);

        return null;

      } finally {
        setProfileLoading(false);
      }
    },
    []
  );


  /* =====================================================
     MANUALLY REFRESH PROFILE
     ===================================================== */

  const refreshProfile =
    useCallback(async () => {
      if (!user?.id) {
        return null;
      }

      return await loadProfile(
        user.id
      );
    }, [
      user,
      loadProfile,
    ]);


  /* =====================================================
     INITIAL SESSION + AUTH STATE LISTENER
     ===================================================== */

  useEffect(() => {
    let mounted = true;


    const initializeAuth =
      async () => {
        try {
          const {
            data: {
              session:
                currentSession,
            },
            error,
          } =
            await supabase.auth.getSession();


          if (error) {
            throw error;
          }


          if (!mounted) {
            return;
          }


          setSession(
            currentSession
          );

          setUser(
            currentSession?.user ??
              null
          );


          if (
            currentSession?.user?.id
          ) {
            try {
              const profileData =
                await getUserProfile(
                  currentSession.user.id
                );


              if (mounted) {
                setProfile(
                  profileData
                );
              }

            } catch (
              profileError
            ) {
              console.error(
                "Unable to restore user profile:",
                profileError
              );


              if (mounted) {
                setProfile(null);
              }
            }

          } else {
            setProfile(null);
          }

        } catch (authError) {
          console.error(
            "Unable to initialize authentication:",
            authError
          );


          if (mounted) {
            setSession(null);
            setUser(null);
            setProfile(null);
          }

        } finally {
          if (mounted) {
            setLoading(false);
          }
        }
      };


    initializeAuth();


    const {
      data: {
        subscription,
      },
    } =
      supabase.auth.onAuthStateChange(
        (_event, newSession) => {

          if (!mounted) {
            return;
          }


          setSession(
            newSession
          );

          setUser(
            newSession?.user ??
              null
          );


          if (
            newSession?.user?.id
          ) {
            setProfileLoading(
              true
            );


            getUserProfile(
              newSession.user.id
            )
              .then(
                (
                  profileData
                ) => {
                  if (
                    mounted
                  ) {
                    setProfile(
                      profileData
                    );
                  }
                }
              )
              .catch(
                (
                  profileError
                ) => {
                  console.error(
                    "Unable to load profile after authentication change:",
                    profileError
                  );


                  if (
                    mounted
                  ) {
                    setProfile(
                      null
                    );
                  }
                }
              )
              .finally(() => {
                if (mounted) {
                  setProfileLoading(
                    false
                  );
                }
              });

          } else {
            setProfile(null);

            setProfileLoading(
              false
            );
          }


          setLoading(false);
        }
      );


    return () => {
      mounted = false;

      subscription.unsubscribe();
    };

  }, []);


  /* =====================================================
     CONTEXT VALUE
     ===================================================== */

  const value = {
    session,
    user,
    profile,

    loading,
    profileLoading,

    isAuthenticated:
      Boolean(user),

    refreshProfile,
  };


  return (
    <AuthContext.Provider
      value={value}
    >
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth() {
  const context =
    useContext(AuthContext);


  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider."
    );
  }


  return context;
}