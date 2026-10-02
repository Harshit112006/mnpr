import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import AuthLayout from "../layouts/AuthLayout";
import DashboardLayout from "../layouts/DashboardLayout";

import ProtectedRoute from "./ProtectedRoute";
import PublicRoute from "./PublicRoute";

import Login from "../pages/auth/Login";
import Signup from "../pages/auth/Signup";
import ForgotPassword from "../pages/auth/ForgotPassword";
import ResetPassword from "../pages/auth/ResetPassword";
import CompleteProfile from "../pages/auth/CompleteProfile";

import Dashboard from "../pages/dashboard/Dashboard";
import Detection from "../pages/detection/Detection";
import Settings from "../pages/settings/Settings";


function PlaceholderPage({
  title,
}) {
  return (
    <div className="placeholder-page">

      <span>
        BREEDVISION AI
      </span>

      <h1>
        {title}
      </h1>

      <p>
        This module will be developed in
        the next phase.
      </p>

    </div>
  );
}


function AppRoutes() {
  return (
    <Routes>

      {/* =====================================================
          PUBLIC AUTHENTICATION
      ===================================================== */}

      <Route
        element={
          <PublicRoute>
            <AuthLayout />
          </PublicRoute>
        }
      >

        <Route
          path="/login"
          element={
            <Login />
          }
        />

        <Route
          path="/signup"
          element={
            <Signup />
          }
        />

        <Route
          path="/forgot-password"
          element={
            <ForgotPassword />
          }
        />

      </Route>


      {/* =====================================================
          PASSWORD RECOVERY
      ===================================================== */}

      <Route
        element={
          <AuthLayout />
        }
      >

        <Route
          path="/reset-password"
          element={
            <ResetPassword />
          }
        />

      </Route>


      {/* =====================================================
          PROFILE COMPLETION
      ===================================================== */}

      <Route
        path="/complete-profile"
        element={
          <ProtectedRoute
            allowIncompleteProfile={
              true
            }
          >
            <CompleteProfile />
          </ProtectedRoute>
        }
      />


      {/* =====================================================
          PROTECTED APPLICATION
      ===================================================== */}

      <Route
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >

        <Route
          path="/dashboard"
          element={
            <Dashboard />
          }
        />


        <Route
          path="/detection"
          element={
            <Detection />
          }
        />


        <Route
          path="/animals"
          element={
            <PlaceholderPage
              title="Animals"
            />
          }
        />


        <Route
          path="/farmers"
          element={
            <PlaceholderPage
              title="Farmers"
            />
          }
        />


        <Route
          path="/history"
          element={
            <PlaceholderPage
              title="Detection History"
            />
          }
        />


        <Route
          path="/review"
          element={
            <PlaceholderPage
              title="Review Center"
            />
          }
        />


        <Route
          path="/analytics"
          element={
            <PlaceholderPage
              title="Analytics"
            />
          }
        />


        <Route
          path="/reports"
          element={
            <PlaceholderPage
              title="Reports"
            />
          }
        />


        <Route
          path="/assistant"
          element={
            <PlaceholderPage
              title="AI Assistant"
            />
          }
        />


        <Route
          path="/alerts"
          element={
            <PlaceholderPage
              title="Alerts"
            />
          }
        />


        <Route
          path="/settings"
          element={
            <Settings />
          }
        />

      </Route>


      {/* =====================================================
          ROOT REDIRECT
      ===================================================== */}

      <Route
        path="/"
        element={
          <Navigate
            to="/login"
            replace
          />
        }
      />


      {/* =====================================================
          UNKNOWN ROUTES
      ===================================================== */}

      <Route
        path="*"
        element={
          <Navigate
            to="/login"
            replace
          />
        }
      />

    </Routes>
  );
}


export default AppRoutes;