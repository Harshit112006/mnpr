import { useState } from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";

import {
  ArrowRight,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  User,
  Building2,
  BriefcaseBusiness,
  CheckCircle2,
  AlertCircle,
  LoaderCircle,
} from "lucide-react";

import {
  signUpUser,
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


function Signup() {
  const navigate = useNavigate();

  const [showPassword, setShowPassword] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [googleLoading, setGoogleLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  const [formData, setFormData] =
    useState({
      name: "",
      email: "",
      organization: "",
      role: "",
      password: "",
      confirmPassword: "",
    });


  const handleChange = (event) => {
    setFormData({
      ...formData,

      [event.target.name]:
        event.target.value,
    });

    setError("");
    setSuccess("");
  };


  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");


    if (
      !formData.name ||
      !formData.email ||
      !formData.password ||
      !formData.role
    ) {
      setError(
        "Please complete all required fields."
      );

      return;
    }


    if (
      formData.password !==
      formData.confirmPassword
    ) {
      setError(
        "Passwords do not match."
      );

      return;
    }


    if (formData.password.length < 6) {
      setError(
        "Password must contain at least 6 characters."
      );

      return;
    }


    try {
      setLoading(true);

      const data =
        await signUpUser({
          name: formData.name,
          email: formData.email,
          password: formData.password,
          organization:
            formData.organization,
          role: formData.role,
        });


      if (data.session) {
        navigate(
          "/dashboard",
          {
            replace: true,
          }
        );

        return;
      }


      setSuccess(
        "Account created successfully. Please check your email and confirm your account before signing in."
      );


      setFormData({
        name: "",
        email: "",
        organization: "",
        role: "",
        password: "",
        confirmPassword: "",
      });

    } catch (signupError) {
      console.error(
        "Signup error:",
        signupError
      );

      setError(
        signupError.message ||
        "Unable to create account."
      );

    } finally {
      setLoading(false);
    }
  };


  const handleGoogleSignup = async () => {
    try {
      setError("");
      setSuccess("");
      setGoogleLoading(true);

      await signInWithGoogle();

    } catch (googleError) {
      console.error(
        "Google signup error:",
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
    <div className="auth-card">

      <div className="auth-heading">

        <span>
          CREATE ACCOUNT
        </span>

        <h2>
          Join BreedVision AI
        </h2>

        <p>
          Create your account to access
          intelligent livestock management tools.
        </p>

      </div>


      <form onSubmit={handleSubmit}>

        <div className="input-group">

          <label>
            Full name
          </label>

          <div className="input-wrapper">

            <User size={19} />

            <input
              type="text"
              name="name"
              placeholder="Enter your full name"
              value={formData.name}
              onChange={handleChange}
              required
            />

          </div>

        </div>


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

          <label>
            Organization
          </label>

          <div className="input-wrapper">

            <Building2 size={19} />

            <input
              type="text"
              name="organization"
              placeholder="Farm / Institution / Organization"
              value={
                formData.organization
              }
              onChange={handleChange}
            />

          </div>

        </div>


        <div className="input-group">

          <label>
            Role
          </label>

          <div className="input-wrapper">

            <BriefcaseBusiness
              size={19}
            />

            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              required
            >

              <option value="">
                Select your role
              </option>

              <option value="field_worker">
                Field Worker
              </option>

              <option value="farmer">
                Farmer
              </option>

              <option value="veterinarian">
                Veterinarian
              </option>

              <option value="researcher">
                Researcher
              </option>

              <option value="student">
                Student / Research Team
              </option>

            </select>

          </div>

        </div>


        <div className="input-group">

          <label>
            Password
          </label>

          <div className="input-wrapper">

            <LockKeyhole
              size={19}
            />

            <input
              type={
                showPassword
                  ? "text"
                  : "password"
              }
              name="password"
              placeholder="Create a strong password"
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


        <div className="input-group">

          <label>
            Confirm password
          </label>

          <div className="input-wrapper">

            <LockKeyhole
              size={19}
            />

            <input
              type={
                showPassword
                  ? "text"
                  : "password"
              }
              name="confirmPassword"
              placeholder="Re-enter your password"
              value={
                formData.confirmPassword
              }
              onChange={handleChange}
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

              Creating Account...
            </>
          ) : (
            <>
              Create Account

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
          onClick={handleGoogleSignup}
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

          Already have an account?

          <Link to="/login">
            Sign in
          </Link>

        </p>

      </form>

    </div>
  );
}


export default Signup;