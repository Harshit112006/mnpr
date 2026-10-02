import {
  ScanSearch,
  ArrowRight,
} from "lucide-react";

import { Link } from "react-router-dom";

function RecentDetections() {
  return (
    <div className="dashboard-panel recent-detections-panel">
      <div className="panel-header">
        <div>
          <h3>Recent Predictions</h3>
          <p>Latest breed identification results</p>
        </div>

        <Link
          to="/history"
          className="panel-link"
        >
          View all
          <ArrowRight size={15} />
        </Link>
      </div>

      <div className="empty-detection-state">
        <div className="empty-detection-icon">
          <ScanSearch size={27} />
        </div>

        <h4>No predictions yet</h4>

        <p>
          Upload or capture an animal image to create your first
          BreedVision prediction.
        </p>

        <Link
          to="/detection"
          className="secondary-dashboard-button"
        >
          Start Detection
          <ArrowRight size={16} />
        </Link>
      </div>
    </div>
  );
}

export default RecentDetections;