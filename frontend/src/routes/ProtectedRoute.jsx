import { Navigate } from "react-router-dom";

import { LoaderCircle } from "lucide-react";

import { useAuth } from "../context/AuthContext";


function ProtectedRoute({ children }) {
  const {
    isAuthenticated,
    loading,
  } = useAuth();


  if (loading) {
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
          Connecting securely to BreedVision AI...
        </p>
      </div>
    );
  }


  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }


  return children;
}


export default ProtectedRoute;