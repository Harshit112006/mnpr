import { Outlet } from "react-router-dom";
import { motion } from "framer-motion";
import { BrainCircuit, ScanSearch, ShieldCheck } from "lucide-react";
import BrandLogo from "../components/common/BrandLogo";

function AuthLayout() {
  return (
    <div className="auth-page">
      <div className="auth-background">
        <div className="blob blob-one"></div>
        <div className="blob blob-two"></div>
        <div className="blob blob-three"></div>
      </div>

      <section className="auth-showcase">
        <motion.div
          className="showcase-content"
          initial={{ opacity: 0, x: -40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7 }}
        >
          <BrandLogo />

          <div className="hero-copy">
            <span className="hero-tag">AI-POWERED LIVESTOCK INTELLIGENCE</span>

            <h2>
              Smarter breed
              <br />
              identification for
              <span> smarter livestock.</span>
            </h2>

            <p>
              BreedVision AI combines computer vision, intelligent breed
              recognition and livestock analytics in one professional platform.
            </p>
          </div>

          <div className="feature-grid">
            <div className="feature-item">
              <ScanSearch size={22} />

              <div>
                <h3>AI Detection</h3>
                <p>Identify cattle and buffalo breeds from images.</p>
              </div>
            </div>

            <div className="feature-item">
              <BrainCircuit size={22} />

              <div>
                <h3>Confidence Analysis</h3>
                <p>View AI confidence and alternative predictions.</p>
              </div>
            </div>

            <div className="feature-item">
              <ShieldCheck size={22} />

              <div>
                <h3>Human Verification</h3>
                <p>Review uncertain predictions before registration.</p>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      <section className="auth-form-section">
        <motion.div
          className="auth-form-wrapper"
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Outlet />
        </motion.div>
      </section>
    </div>
  );
}

export default AuthLayout;