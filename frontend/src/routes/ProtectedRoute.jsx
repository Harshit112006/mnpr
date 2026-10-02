import { Navigate } from "react-router-dom";

import {
  LoaderCircle,
} from "lucide-react";

import {
  useAuth,
} from "../context/AuthContext";


function ProtectedRoute({
  children,
  allowIncompleteProfile = false,
}) {
  const {
    isAuthenticated,
    loading,
    profile,
    profileLoading,
  } = useAuth();


  /* =====================================================
     WAIT FOR AUTH + PROFILE
     ===================================================== */

  if (
    loading ||
    profileLoading
  ) {
    return (
      <div className="auth-route-loader">

        <LoaderCircle
          size={30}
          className="auth-route-spinner"
        />

        <h3>
          Restoring your session
        </h3>

        <p>
          Loading your BreedVision profile...
        </p>

      </div>
    );
  }


  /* =====================================================
     NOT LOGGED IN
     ===================================================== */

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }


  /* =====================================================
     PROFILE COMPLETION REQUIRED
     ===================================================== */

  const profileIncomplete =
    !profile ||
    !profile.role ||
    profile.role === "user";


  if (
    profileIncomplete &&
    !allowIncompleteProfile
  ) {
    return (
      <Navigate
        to="/complete-profile"
        replace
      />
    );
  }


  /* =====================================================
     PROFILE ALREADY COMPLETE

     Prevent completed users from manually opening
     /complete-profile
     ===================================================== */

  if (
    allowIncompleteProfile &&
    !profileIncomplete
  ) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    );
  }


  return children;
}


export default ProtectedRoute;