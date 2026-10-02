import { useState } from "react";
import {
  useNavigate,
} from "react-router-dom";

import {
  Eye,
  EyeOff,
  LockKeyhole,
  AlertCircle,
  CheckCircle2,
  LoaderCircle,
} from "lucide-react";

import {
  updateUserPassword,
} from "../../services/authService";


function ResetPassword() {
  const navigate = useNavigate();

  const [password, setPassword] =
    useState("");

  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [showPassword, setShowPassword] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");


  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!password || !confirmPassword) {
      setError(
        "Please complete both password fields."
      );

      return;
    }

    if (password.length < 6) {
      setError(
        "Password must contain at least 6 characters."
      );

      return;
    }

    if (password !== confirmPassword) {
      setError(
        "Passwords do not match."
      );

      return;
    }

    try {
      setLoading(true);

      await updateUserPassword(
        password
      );

      setSuccess(
        "Password updated successfully. Redirecting to your dashboard..."
      );

      setTimeout(() => {
        navigate(
          "/dashboard",
          {
            replace: true,
          }
        );
      }, 1500);

    } catch (updateError) {
      console.error(
        "Password update error:",
        updateError
      );

      setError(
        updateError.message ||
        "Unable to update your password."
      );

    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="auth-card">

      <div className="auth-heading">

        <span>
          SECURE PASSWORD RESET
        </span>

        <h2>
          Create a new password
        </h2>

        <p>
          Choose a new password for your
          BreedVision AI account.
        </p>

      </div>


      <form onSubmit={handleSubmit}>

        <div className="input-group">

          <label>
            New password
          </label>

          <div className="input-wrapper">

            <LockKeyhole size={19} />

            <input
              type={
                showPassword
                  ? "text"
                  : "password"
              }
              placeholder="Enter new password"
              value={password}
              onChange={(event) => {
                setPassword(
                  event.target.value
                );

                setError("");
              }}
              required
            />

            <button
              type="button"
              className="password-toggle"
              onClick={() =>
                setShowPassword(
                  !showPassword
                )
              }
            >

              {showPassword ? (
                <EyeOff size={19} />
              ) : (
                <Eye size={19} />
              )}

            </button>

          </div>

        </div>


        <div className="input-group">

          <label>
            Confirm new password
          </label>

          <div className="input-wrapper">

            <LockKeyhole size={19} />

            <input
              type={
                showPassword
                  ? "text"
                  : "password"
              }
              placeholder="Re-enter new password"
              value={confirmPassword}
              onChange={(event) => {
                setConfirmPassword(
                  event.target.value
                );

                setError("");
              }}
              required
            />

          </div>

        </div>


        {error && (
          <div className="auth-message auth-error-message">

            <AlertCircle size={17} />

            <span>
              {error}
            </span>

          </div>
        )}


        {success && (
          <div className="auth-message auth-success-message">

            <CheckCircle2 size={17} />

            <span>
              {success}
            </span>

          </div>
        )}


        <button
          className="primary-auth-button"
          type="submit"
          disabled={loading}
        >

          {loading ? (
            <>
              <LoaderCircle
                size={18}
                className="auth-loader"
              />

              Updating Password...
            </>
          ) : (
            <>
              Update Password
            </>
          )}

        </button>

      </form>

    </div>
  );
}


export default ResetPassword;