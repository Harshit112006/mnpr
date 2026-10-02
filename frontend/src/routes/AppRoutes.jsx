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

import Dashboard from "../pages/dashboard/Dashboard";
import Detection from "../pages/detection/Detection";


function PlaceholderPage({ title }) {
  return (
    <div className="placeholder-page">
      <span>
        BREEDVISION AI
      </span>

      <h1>
        {title}
      </h1>

      <p>
        This module will be developed in the next phase.
      </p>
    </div>
  );
}


function AppRoutes() {
  return (
    <Routes>

      {/* =====================================================
          PUBLIC AUTHENTICATION ROUTES
          Logged-in users are redirected to /dashboard
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
          element={<Login />}
        />

        <Route
          path="/signup"
          element={<Signup />}
        />

        <Route
          path="/forgot-password"
          element={<ForgotPassword />}
        />
      </Route>


      {/* =====================================================
          PASSWORD RECOVERY ROUTE

          IMPORTANT:
          This route is intentionally NOT wrapped inside
          PublicRoute because Supabase creates a temporary
          recovery session when the user clicks the password
          reset email link.
      ===================================================== */}

      <Route element={<AuthLayout />}>
        <Route
          path="/reset-password"
          element={<ResetPassword />}
        />
      </Route>


      {/* =====================================================
          PROTECTED BREEDVISION APPLICATION
          Authentication required
      ===================================================== */}

      <Route
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >

        {/* Dashboard */}

        <Route
          path="/dashboard"
          element={<Dashboard />}
        />


        {/* AI Detection */}

        <Route
          path="/detection"
          element={<Detection />}
        />


        {/* Animals */}

        <Route
          path="/animals"
          element={
            <PlaceholderPage
              title="Animals"
            />
          }
        />


        {/* Farmers */}

        <Route
          path="/farmers"
          element={
            <PlaceholderPage
              title="Farmers"
            />
          }
        />


        {/* Detection History */}

        <Route
          path="/history"
          element={
            <PlaceholderPage
              title="Detection History"
            />
          }
        />


        {/* Human Review Center */}

        <Route
          path="/review"
          element={
            <PlaceholderPage
              title="Review Center"
            />
          }
        />


        {/* Analytics */}

        <Route
          path="/analytics"
          element={
            <PlaceholderPage
              title="Analytics"
            />
          }
        />


        {/* Reports */}

        <Route
          path="/reports"
          element={
            <PlaceholderPage
              title="Reports"
            />
          }
        />


        {/* AI Assistant */}

        <Route
          path="/assistant"
          element={
            <PlaceholderPage
              title="AI Assistant"
            />
          }
        />


        {/* Alerts */}

        <Route
          path="/alerts"
          element={
            <PlaceholderPage
              title="Alerts"
            />
          }
        />


        {/* Settings */}

        <Route
          path="/settings"
          element={
            <PlaceholderPage
              title="Settings"
            />
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