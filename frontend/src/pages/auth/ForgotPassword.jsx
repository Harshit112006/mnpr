import { Link } from "react-router-dom";
import { ArrowLeft, Mail } from "lucide-react";

function ForgotPassword() {
  return (
    <div className="auth-card">
      <div className="auth-heading">
        <span>ACCOUNT RECOVERY</span>

        <h2>Forgot your password?</h2>

        <p>
          Enter your registered email address and we'll send you password
          recovery instructions.
        </p>
      </div>

      <form>
        <div className="input-group">
          <label>Email address</label>

          <div className="input-wrapper">
            <Mail size={19} />

            <input
              type="email"
              placeholder="you@example.com"
              required
            />
          </div>
        </div>

        <button className="primary-auth-button" type="submit">
          Send Reset Link
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