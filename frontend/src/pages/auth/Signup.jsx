import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

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

import { signUpUser } from "../../services/authService";

function Signup() {
  const navigate = useNavigate();

  const [showPassword, setShowPassword] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  const [formData, setFormData] = useState({
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

      /*
        If email confirmation is enabled,
        Supabase usually returns a user
        but no active session.

        If confirmation is disabled,
        session can be immediately available.
      */

      if (data.session) {
        navigate("/dashboard");
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

        {/* FULL NAME */}

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


        {/* EMAIL */}

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


        {/* ORGANIZATION */}

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


        {/* ROLE */}

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


        {/* PASSWORD */}

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


        {/* CONFIRM PASSWORD */}

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


        {/* ERROR */}

        {error && (
          <div className="auth-message auth-error-message">
            <AlertCircle size={17} />

            <span>
              {error}
            </span>
          </div>
        )}


        {/* SUCCESS */}

        {success && (
          <div className="auth-message auth-success-message">
            <CheckCircle2 size={17} />

            <span>
              {success}
            </span>
          </div>
        )}


        {/* SUBMIT */}

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

              Creating Account...
            </>
          ) : (
            <>
              Create Account

              <ArrowRight
                size={19}
              />
            </>
          )}
        </button>


        <div className="separator">
          <span />
          <p>OR</p>
          <span />
        </div>


        <button
          className="google-button"
          type="button"
        >
          Continue with Google
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