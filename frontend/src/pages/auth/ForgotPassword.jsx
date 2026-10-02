import { useState } from "react";
import { Link } from "react-router-dom";

import {
  ArrowLeft,
  Mail,
  AlertCircle,
  CheckCircle2,
  LoaderCircle,
} from "lucide-react";

import {
  sendPasswordResetEmail,
} from "../../services/authService";


function ForgotPassword() {
  const [email, setEmail] =
    useState("");

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

    if (!email) {
      setError(
        "Please enter your email address."
      );

      return;
    }

    try {
      setLoading(true);

      await sendPasswordResetEmail(email);

      setSuccess(
        "If an account exists for this email, a password reset link has been sent."
      );

    } catch (resetError) {
      console.error(
        "Password reset error:",
        resetError
      );

      setError(
        resetError.message ||
        "Unable to send password reset email."
      );

    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="auth-card">

      <div className="auth-heading">

        <span>
          ACCOUNT RECOVERY
        </span>

        <h2>
          Forgot your password?
        </h2>

        <p>
          Enter your registered email address.
          BreedVision will send you a secure
          password recovery link.
        </p>

      </div>


      <form onSubmit={handleSubmit}>

        <div className="input-group">

          <label>
            Email address
          </label>

          <div className="input-wrapper">

            <Mail size={19} />

            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(event) => {
                setEmail(
                  event.target.value
                );

                setError("");
                setSuccess("");
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

              Sending Link...
            </>
          ) : (
            <>
              Send Reset Link
            </>
          )}

        </button>


        <p className="auth-footer">

          <Link to="/login">

            <ArrowLeft size={16} />

            Back to Sign In

          </Link>

        </p>

      </form>

    </div>
  );
}


export default ForgotPassword;