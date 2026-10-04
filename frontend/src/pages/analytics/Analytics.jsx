import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  AlertCircle,
  BarChart3,
  Beef,
  Bell,
  ClipboardCheck,
  LoaderCircle,
  RefreshCw,
  ScanSearch,
  Users,
} from "lucide-react";

import {
  getOperationalAnalytics,
} from "../../services/phase9/analyticsService";

import "../../styles/Phase9.css";


function Distribution({
  title,
  rows,
}) {

  const max =
    Math.max(
      1,
      ...rows.map(
        (
          row
        ) =>
          row.count
      )
    );


  return (
    <section className="analytics-panel">

      <h2>
        {title}
      </h2>


      {
        rows.length ===
        0 ? (

          <p className="analytics-empty">
            No real data available yet.
          </p>

        ) : (

          <div className="analytics-bars">

            {
              rows.map(
                (
                  row
                ) => (

                  <div
                    key={row.label}
                    className="analytics-bar-row"
                  >

                    <div>
                      <span>
                        {row.label}
                      </span>

                      <strong>
                        {row.count}
                      </strong>
                    </div>


                    <div className="analytics-track">

                      <div
                        className="analytics-fill"
                        style={{
                          width:
                            `${(
                              row.count /
                              max
                            ) * 100}%`,
                        }}
                      />

                    </div>

                  </div>

                )
              )
            }

          </div>

        )
      }

    </section>
  );
}


function Analytics() {

  const [data, setData] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  const loadAnalytics =
    useCallback(async () => {

      try {

        setLoading(true);
        setError("");

        setData(
          await getOperationalAnalytics()
        );

      }

      catch (
        analyticsError
      ) {

        setError(
          analyticsError.message ||
          "Unable to load analytics."
        );

      }

      finally {

        setLoading(false);

      }

    }, []);


  useEffect(() => {
    loadAnalytics();
  }, [
    loadAnalytics,
  ]);


  if (loading) {
    return (
      <div className="phase9-loading">
        <LoaderCircle
          className="phase9-spinner"
          size={32}
        />
        <h3>
          Computing real analytics
        </h3>
      </div>
    );
  }


  if (!data) {

    return (
      <div className="phase9-error">
        <AlertCircle size={17} />
        {error || "Analytics unavailable."}
      </div>
    );
  }


  const summary =
    data.summary;


  return (
    <div className="phase9-page">

      <section className="phase9-header">

        <div>
          <span className="phase9-eyebrow">
            REAL OPERATIONAL DATA
          </span>

          <h1>
            Analytics
          </h1>

          <p>
            Statistics below are calculated
            from the current user's actual
            Supabase records.
          </p>
        </div>


        <button
          className="phase9-secondary"
          onClick={
            loadAnalytics
          }
        >
          <RefreshCw size={16} />
          Refresh
        </button>

      </section>


      {error && (
        <div className="phase9-error">
          {error}
        </div>
      )}


      <section className="phase9-summary-grid">

        <div className="phase9-summary-card">
          <ScanSearch size={21} />
          <div>
            <span>Detections</span>
            <strong>
              {summary.detections}
            </strong>
          </div>
        </div>


        <div className="phase9-summary-card">
          <Users size={21} />
          <div>
            <span>Farmers</span>
            <strong>
              {summary.farmers}
            </strong>
          </div>
        </div>


        <div className="phase9-summary-card">
          <Beef size={21} />
          <div>
            <span>Animals</span>
            <strong>
              {summary.animals}
            </strong>
          </div>
        </div>


        <div className="phase9-summary-card">
          <ClipboardCheck size={21} />
          <div>
            <span>Reviews</span>
            <strong>
              {summary.reviews}
            </strong>
          </div>
        </div>


        <div className="phase9-summary-card">
          <Bell size={21} />
          <div>
            <span>Unread Alerts</span>
            <strong>
              {summary.unread_alerts}
            </strong>
          </div>
        </div>


        <div className="phase9-summary-card">
          <BarChart3 size={21} />
          <div>
            <span>Avg. Confidence</span>
            <strong>
              {
                summary.average_confidence !==
                null
                  ? `${(
                      summary.average_confidence *
                      100
                    ).toFixed(2)}%`
                  : "—"
              }
            </strong>
          </div>
        </div>

      </section>


      <section className="analytics-grid">

        <Distribution
          title="Detected Species"
          rows={
            data.detection_species
          }
        />

        <Distribution
          title="Detected Breeds"
          rows={
            data.detection_breeds
          }
        />

        <Distribution
          title="Animal Registry"
          rows={
            data.animal_species
          }
        />

        <Distribution
          title="Review Decisions"
          rows={
            data.review_decisions
          }
        />

        <Distribution
          title="Alert Status"
          rows={
            data.alert_statuses
          }
        />

      </section>

    </div>
  );
}


export default Analytics;