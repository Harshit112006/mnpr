import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import AuthLayout from "../layouts/AuthLayout";
import DashboardLayout from "../layouts/DashboardLayout";

import Login from "../pages/auth/Login";
import Signup from "../pages/auth/Signup";
import ForgotPassword from "../pages/auth/ForgotPassword";
import Detection from "../pages/detection/Detection";
import Dashboard from "../pages/dashboard/Dashboard";

function PlaceholderPage({ title }) {
  return (
    <div className="placeholder-page">
      <span>BREEDVISION AI</span>

      <h1>{title}</h1>

      <p>
        This module will be developed in the next phase.
      </p>
    </div>
  );
}

function AppRoutes() {
  return (
    <Routes>

      {/* Authentication Routes */}

      <Route element={<AuthLayout />}>
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


      {/* BreedVision Dashboard */}

      <Route element={<DashboardLayout />}>

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
          element={
            <PlaceholderPage title="Animals" />
          }
        />

        <Route
          path="/farmers"
          element={
            <PlaceholderPage title="Farmers" />
          }
        />

        <Route
          path="/history"
          element={
            <PlaceholderPage title="Detection History" />
          }
        />

        <Route
          path="/review"
          element={
            <PlaceholderPage title="Review Center" />
          }
        />

        <Route
          path="/analytics"
          element={
            <PlaceholderPage title="Analytics" />
          }
        />

        <Route
          path="/reports"
          element={
            <PlaceholderPage title="Reports" />
          }
        />

        <Route
          path="/assistant"
          element={
            <PlaceholderPage title="AI Assistant" />
          }
        />

        <Route
          path="/alerts"
          element={
            <PlaceholderPage title="Alerts" />
          }
        />

        <Route
          path="/settings"
          element={
            <PlaceholderPage title="Settings" />
          }
        />

      </Route>


      {/* Redirects */}

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