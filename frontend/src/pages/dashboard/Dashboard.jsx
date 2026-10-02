import {
  Beef,
  ScanSearch,
  ClipboardCheck,
  Gauge,
  ArrowUpRight,
  Camera,
  Upload,
  BrainCircuit,
  Database,
  ShieldCheck,
} from "lucide-react";

import { Link } from "react-router-dom";

import StatCard from "../../components/dashboard/StatCard";
import ActivityChart from "../../components/dashboard/ActivityChart";
import RecentDetections from "../../components/dashboard/RecentDetections";

function Dashboard() {
  return (
    <div className="dashboard-page">

      {/* =========================
          WELCOME HEADER
      ========================== */}

      <section className="dashboard-welcome">
        <div>
          <span className="dashboard-eyebrow">
            BREEDVISION AI COMMAND CENTER
          </span>

          <h1>
            Welcome back, Harshit.
          </h1>

          <p>
            Monitor breed predictions, livestock records and AI
            verification activity from one workspace.
          </p>
        </div>

        <Link
          to="/detection"
          className="primary-dashboard-button"
        >
          <ScanSearch size={18} />
          New Detection
          <ArrowUpRight size={16} />
        </Link>
      </section>


      {/* =========================
          STATISTICS
      ========================== */}

      <section className="dashboard-stat-grid">

        <StatCard
          title="Registered Animals"
          value="0"
          subtitle="No animals registered yet"
          icon={Beef}
        />

        <StatCard
          title="Total Predictions"
          value="0"
          subtitle="No detection activity yet"
          icon={ScanSearch}
        />

        <StatCard
          title="Pending Reviews"
          value="0"
          subtitle="No cases require verification"
          icon={ClipboardCheck}
        />

        <StatCard
          title="Average Confidence"
          value="—"
          subtitle="Available after model predictions"
          icon={Gauge}
        />

      </section>


      {/* =========================
          QUICK DETECTION
      ========================== */}

      <section className="quick-detection-banner">

        <div className="quick-detection-content">

          <div className="quick-detection-icon">
            <BrainCircuit size={29} />
          </div>

          <div>
            <span>BREED IDENTIFICATION</span>

            <h2>
              Identify cattle and buffalo breeds using AI
            </h2>

            <p>
              Upload an animal image or capture one using your device
              camera. BreedVision will return the predicted breed,
              confidence score and alternative predictions.
            </p>
          </div>

        </div>

        <div className="quick-detection-actions">

          <Link
            to="/detection"
            className="quick-action-primary"
          >
            <Upload size={18} />
            Upload Image
          </Link>

          <Link
            to="/detection"
            className="quick-action-secondary"
          >
            <Camera size={18} />
            Open Camera
          </Link>

        </div>

      </section>


      {/* =========================
          ANALYTICS AREA
      ========================== */}

      <section className="dashboard-main-grid">

        <ActivityChart />

        <div className="dashboard-panel model-status-panel">

          <div className="panel-header">
            <div>
              <h3>AI System Status</h3>
              <p>BreedVision model infrastructure</p>
            </div>

            <span className="status-badge-development">
              DEVELOPMENT
            </span>
          </div>

          <div className="model-status-list">

            <div className="model-status-item">

              <div className="model-status-icon">
                <ScanSearch size={19} />
              </div>

              <div>
                <h4>Animal Detector</h4>
                <p>YOLO detector</p>
              </div>

              <span className="model-status-pending">
                Pending
              </span>

            </div>


            <div className="model-status-item">

              <div className="model-status-icon">
                <BrainCircuit size={19} />
              </div>

              <div>
                <h4>Breed Classifier</h4>
                <p>EfficientNet pipeline</p>
              </div>

              <span className="model-status-pending">
                Pending
              </span>

            </div>


            <div className="model-status-item">

              <div className="model-status-icon">
                <Database size={19} />
              </div>

              <div>
                <h4>Database</h4>
                <p>Supabase integration</p>
              </div>

              <span className="model-status-pending">
                Pending
              </span>

            </div>


            <div className="model-status-item">

              <div className="model-status-icon">
                <ShieldCheck size={19} />
              </div>

              <div>
                <h4>Human Verification</h4>
                <p>Low-confidence review workflow</p>
              </div>

              <span className="model-status-pending">
                Pending
              </span>

            </div>

          </div>

        </div>

      </section>


      {/* =========================
          RECENT RESULTS
      ========================== */}

      <section className="dashboard-bottom-grid">

        <RecentDetections />


        <div className="dashboard-panel breed-overview-panel">

          <div className="panel-header">
            <div>
              <h3>Breed Distribution</h3>
              <p>Detected breeds across registered predictions</p>
            </div>
          </div>

          <div className="breed-empty-state">

            <div className="breed-empty-circle">
              <Beef size={28} />
            </div>

            <h4>No breed data available</h4>

            <p>
              Distribution analytics will populate automatically
              when verified predictions are stored.
            </p>

          </div>

        </div>

      </section>

    </div>
  );
}

export default Dashboard;