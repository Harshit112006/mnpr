import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import { supabase } from "../lib/supabaseClient";


const AuthContext = createContext(null);


export function AuthProvider({ children }) {
  const [session, setSession] = useState(null);

  const [user, setUser] = useState(null);

  const [loading, setLoading] = useState(true);


  useEffect(() => {
    let mounted = true;

    const loadSession = async () => {
      const {
        data: { session },
        error,
      } = await supabase.auth.getSession();

      if (!mounted) {
        return;
      }

      if (error) {
        console.error(
          "Unable to restore Supabase session:",
          error
        );
      }

      setSession(session);

      setUser(
        session?.user ?? null
      );

      setLoading(false);
    };


    loadSession();


    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        if (!mounted) {
          return;
        }

        setSession(session);

        setUser(
          session?.user ?? null
        );

        setLoading(false);
      }
    );


    return () => {
      mounted = false;

      subscription.unsubscribe();
    };
  }, []);


  const value = {
    session,
    user,
    loading,
    isAuthenticated: Boolean(user),
  };


  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider."
    );
  }

  return context;
}