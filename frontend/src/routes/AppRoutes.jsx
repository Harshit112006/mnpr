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
import History from "../pages/history/History";
import Settings from "../pages/settings/Settings";

import Farmers from "../pages/farmers/Farmers";
import Animals from "../pages/animals/Animals";
import ReviewCenter from "../pages/review/ReviewCenter";
import Analytics from "../pages/analytics/Analytics";
import Reports from "../pages/reports/Reports";
import Alerts from "../pages/alerts/Alerts";


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


      <Route
        element={
          <AuthLayout />
        }
      >

        <Route
          path="/reset-password"
          element={<ResetPassword />}
        />

      </Route>


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


      <Route
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >

        <Route
          path="/dashboard"
          element={<Dashboard />}
        />

        <Route
          path="/detection"
          element={<Detection />}
        />

        <Route
          path="/animals"
          element={<Animals />}
        />

        <Route
          path="/farmers"
          element={<Farmers />}
        />

        <Route
          path="/history"
          element={<History />}
        />

        <Route
          path="/review"
          element={<ReviewCenter />}
        />

        <Route
          path="/analytics"
          element={<Analytics />}
        />

        <Route
          path="/reports"
          element={<Reports />}
        />


        {/* Phase 10 remains intentionally separate. */}

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
          element={<Alerts />}
        />

        <Route
          path="/settings"
          element={<Settings />}
        />

      </Route>


      <Route
        path="/"
        element={
          <Navigate
            to="/login"
            replace
          />
        }
      />


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