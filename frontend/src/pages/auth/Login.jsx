import { useState } from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";

import { motion } from "framer-motion";

import {
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  ArrowRight,
  AlertCircle,
  LoaderCircle,
} from "lucide-react";

import {
  signInUser,
  signInWithGoogle,
} from "../../services/authService";


function GoogleIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      width="20"
      height="20"
      aria-hidden="true"
    >
      <path
        fill="#4285F4"
        d="M21.35 11.1h-9.18v3.71h5.29c-.23 1.19-.91 2.2-1.93 2.88v2.4h3.12c1.83-1.68 2.88-4.16 2.88-7.09 0-.66-.06-1.3-.18-1.9z"
      />

      <path
        fill="#34A853"
        d="M12.17 21.5c2.61 0 4.8-.86 6.4-2.34l-3.12-2.4c-.86.58-1.97.93-3.28.93-2.51 0-4.64-1.7-5.4-3.98H3.55v2.47A9.67 9.67 0 0012.17 21.5z"
      />

      <path
        fill="#FBBC05"
        d="M6.77 13.71a5.82 5.82 0 010-3.72V7.52H3.55a9.68 9.68 0 000 8.66l3.22-2.47z"
      />

      <path
        fill="#EA4335"
        d="M12.17 6.02c1.42 0 2.7.49 3.7 1.45l2.77-2.77C16.96 3.13 14.78 2.2 12.17 2.2a9.67 9.67 0 00-8.62 5.32l3.22 2.47c.76-2.28 2.89-3.97 5.4-3.97z"
      />
    </svg>
  );
}


function Login() {
  const navigate = useNavigate();

  const [showPassword, setShowPassword] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [googleLoading, setGoogleLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [formData, setFormData] =
    useState({
      email: "",
      password: "",
    });


  const handleChange = (event) => {
    setFormData({
      ...formData,

      [event.target.name]:
        event.target.value,
    });

    setError("");
  };


  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (
      !formData.email ||
      !formData.password
    ) {
      setError(
        "Please enter your email and password."
      );

      return;
    }

    try {
      setLoading(true);

      const data =
        await signInUser({
          email: formData.email,
          password: formData.password,
        });


      if (!data.session) {
        setError(
          "Login failed. Please verify your account and try again."
        );

        return;
      }


      navigate(
        "/dashboard",
        {
          replace: true,
        }
      );

    } catch (loginError) {
      console.error(
        "Login error:",
        loginError
      );

      setError(
        loginError.message ||
        "Unable to sign in."
      );

    } finally {
      setLoading(false);
    }
  };


  const handleGoogleLogin = async () => {
    try {
      setError("");
      setGoogleLoading(true);

      await signInWithGoogle();

    } catch (googleError) {
      console.error(
        "Google login error:",
        googleError
      );

      setError(
        googleError.message ||
        "Unable to continue with Google."
      );

      setGoogleLoading(false);
    }
  };


  return (
    <motion.div
      className="auth-card"
      initial={{
        opacity: 0,
        scale: 0.97,
      }}
      animate={{
        opacity: 1,
        scale: 1,
      }}
      transition={{
        duration: 0.4,
      }}
    >

      <div className="auth-heading">

        <span>
          WELCOME BACK
        </span>

        <h2>
          Sign in to BreedVision
        </h2>

        <p>
          Access intelligent breed detection,
          livestock analytics and reports.
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
              name="email"
              placeholder="you@example.com"
              value={formData.email}
              onChange={handleChange}
              required
            />

          </div>

        </div>


        <div className="input-group">

          <div className="label-row">

            <label>
              Password
            </label>

            <Link to="/forgot-password">
              Forgot password?
            </Link>

          </div>


          <div className="input-wrapper">

            <LockKeyhole size={19} />

            <input
              type={
                showPassword
                  ? "text"
                  : "password"
              }
              name="password"
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleChange}
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


        <div className="login-options">

          <label className="remember-me">

            <input
              type="checkbox"
            />

            <span>
              Remember me
            </span>

          </label>

        </div>


        {error && (
          <div className="auth-message auth-error-message">

            <AlertCircle size={17} />

            <span>
              {error}
            </span>

          </div>
        )}


        <button
          className="primary-auth-button"
          type="submit"
          disabled={
            loading ||
            googleLoading
          }
        >

          {loading ? (
            <>
              <LoaderCircle
                size={18}
                className="auth-loader"
              />

              Signing In...
            </>
          ) : (
            <>
              Sign In

              <ArrowRight size={19} />
            </>
          )}

        </button>


        <div className="separator">

          <span />

          <p>
            OR
          </p>

          <span />

        </div>


        <button
          className="google-button"
          type="button"
          onClick={handleGoogleLogin}
          disabled={
            loading ||
            googleLoading
          }
        >

          {googleLoading ? (
            <>
              <LoaderCircle
                size={18}
                className="auth-loader"
              />

              Connecting to Google...
            </>
          ) : (
            <>
              <GoogleIcon />

              Continue with Google
            </>
          )}

        </button>


        <p className="auth-footer">

          Don't have an account?

          <Link to="/signup">
            Create account
          </Link>

        </p>

      </form>

    </motion.div>
  );
}


export default Login;