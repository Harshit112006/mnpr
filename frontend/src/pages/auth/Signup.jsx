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
} from "lucide-react";

function Signup() {
  const navigate = useNavigate();

  const [showPassword, setShowPassword] = useState(false);
const [formData, setFormData] = useState({
  name: "",
  email: "",
  organization: "",
  role: "",
  password: "",
});

  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    // Supabase registration will be integrated later.
    navigate("/dashboard");
  };

  return (
    <div className="auth-card">
      <div className="auth-heading">
        <span>CREATE ACCOUNT</span>

        <h2>Join BreedVision AI</h2>

        <p>
          Create your account to access intelligent livestock management tools.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label>Full name</label>

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
          <label>Email address</label>

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
          <label>Organization</label>

          <div className="input-wrapper">
            <Building2 size={19} />

            <input
              type="text"
              name="organization"
              placeholder="Farm / Institution / Organization"
              value={formData.organization}
              onChange={handleChange}
            />
          </div>
        </div>
        <div className="input-group">
  <label>Role</label>

  <div className="input-wrapper">
    <BriefcaseBusiness size={19} />

    <select
      name="role"
      value={formData.role}
      onChange={handleChange}
      required
    >
      <option value="">Select your role</option>
      <option value="field_worker">Field Worker</option>
      <option value="farmer">Farmer</option>
      <option value="veterinarian">Veterinarian</option>
      <option value="researcher">Researcher</option>
      <option value="student">Student / Research Team</option>
    </select>
  </div>
</div>

        <div className="input-group">
          <label>Password</label>

          <div className="input-wrapper">
            <LockKeyhole size={19} />

            <input
              type={showPassword ? "text" : "password"}
              name="password"
              placeholder="Create a strong password"
              value={formData.password}
              onChange={handleChange}
              required
            />

            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <EyeOff size={19} /> : <Eye size={19} />}
            </button>
          </div>
        </div>

        <button className="primary-auth-button" type="submit">
          Create Account
          <ArrowRight size={19} />
        </button>

        <div className="separator">
          <span></span>
          <p>OR</p>
          <span></span>
        </div>

        <button className="google-button" type="button">
          Continue with Google
        </button>

        <p className="auth-footer">
          Already have an account?
          <Link to="/login"> Sign in</Link>
        </p>
      </form>
    </div>
  );
}

export default Signup;