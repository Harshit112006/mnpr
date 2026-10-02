import { Navigate } from "react-router-dom";
import { LoaderCircle } from "lucide-react";

import { useAuth } from "../context/AuthContext";


function PublicRoute({ children }) {
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
          Checking your session
        </h3>

        <p>
          Connecting securely to BreedVision AI...
        </p>
      </div>
    );
  }


  if (isAuthenticated) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    );
  }


  return children;
}


export default PublicRoute;