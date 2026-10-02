import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import {
  Activity,
  AlertCircle,
  Camera,
  FileImage,
  ImageOff,
  LoaderCircle,
  RefreshCw,
  ScanSearch,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  useAuth,
} from "../../context/AuthContext";

import {
  getDashboardData,
} from "../../services/dashboardDataService";

import "../../styles/DashboardLive.css";


function Dashboard() {
  const navigate =
    useNavigate();


  const {
    profile,
    user,
  } = useAuth();


  const [
    dashboard,
    setDashboard,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");


  /* =====================================================
     USER NAME
     ===================================================== */

  const firstName =
    profile?.full_name
      ?.split(" ")[0] ||
    user?.user_metadata?.name
      ?.split(" ")[0] ||
    "User";


  /* =====================================================
     LOAD REAL DASHBOARD DATA
     ===================================================== */

  const loadDashboard =
    useCallback(async () => {
      try {
        setLoading(true);

        setError("");


        const data =
          await getDashboardData();


        setDashboard(
          data
        );

      } catch (
        dashboardError
      ) {
        console.error(
          "Dashboard data error:",
          dashboardError
        );


        setError(
          dashboardError.message ||
          "Unable to load dashboard data."
        );

      } finally {
        setLoading(false);
      }
    }, []);


  useEffect(() => {
    loadDashboard();
  }, [
    loadDashboard,
  ]);


  /* =====================================================
     HELPERS
     ===================================================== */

  const formatDate = (
    value
  ) => {
    if (!value) {
      return "—";
    }


    return new Date(
      value
    ).toLocaleString(
      "en-IN",
      {
        day: "2-digit",

        month: "short",

        hour: "2-digit",

        minute:
          "2-digit",
      }
    );
  };


  const formatConfidence =
    (
      confidence
    ) => {
      if (
        confidence === null ||
        confidence === undefined
      ) {
        return "—";
      }


      return `${(
        Number(
          confidence
        ) * 100
      ).toFixed(1)}%`;
    };


  if (
    loading &&
    !dashboard
  ) {
    return (
      <div className="live-dashboard-loading">

        <LoaderCircle
          size={30}
          className="live-dashboard-spinner"
        />

        <span>
          Loading real BreedVision data...
        </span>

      </div>
    );
  }


  const data =
    dashboard || {
      totalDetections: 0,

      pendingReviews: 0,

      cameraDetections: 0,

      averageConfidence: null,

      activity: [],

      breedDistribution: [],

      recentDetections: [],
    };


  return (
    <div className="live-dashboard-page">

      {/* =================================================
          HEADER
      ================================================= */}

      <header className="live-dashboard-header">

        <div>

          <span className="live-dashboard-eyebrow">
            BREEDVISION INTELLIGENCE
          </span>

          <h1>
            Welcome back, {firstName}
          </h1>

          <p>
            Your dashboard is now powered by
            real records from your private
            BreedVision workspace.
          </p>

        </div>


        <div className="live-dashboard-actions">

          <button
            type="button"
            className="live-dashboard-button"
            onClick={
              loadDashboard
            }
          >
            <RefreshCw
              size={15}
            />

            Refresh
          </button>


          <button
            type="button"
            className="live-dashboard-button primary"
            onClick={() =>
              navigate(
                "/detection"
              )
            }
          >
            <ScanSearch
              size={15}
            />

            New Detection
          </button>

        </div>

      </header>


      {error && (

        <div className="live-dashboard-error">

          <AlertCircle
            size={16}
          />

          {error}

        </div>

      )}


      {/* =================================================
          REAL KPI CARDS
      ================================================= */}

      <section className="live-dashboard-stats">

        <article className="live-stat-card">

          <div className="live-stat-card-top">

            <div className="live-stat-icon">

              <ScanSearch
                size={18}
              />

            </div>

          </div>

          <span>
            Total Detections
          </span>

          <strong>
            {data.totalDetections}
          </strong>

          <p>
            Real records stored in Supabase
          </p>

        </article>


        <article className="live-stat-card">

          <div className="live-stat-card-top">

            <div className="live-stat-icon">

              <ShieldCheck
                size={18}
              />

            </div>

          </div>

          <span>
            Pending Reviews
          </span>

          <strong>
            {data.pendingReviews}
          </strong>

          <p>
            Awaiting verification
          </p>

        </article>


        <article className="live-stat-card">

          <div className="live-stat-card-top">

            <div className="live-stat-icon">

              <Camera
                size={18}
              />

            </div>

          </div>

          <span>
            Camera Captures
          </span>

          <strong>
            {data.cameraDetections}
          </strong>

          <p>
            Captured through live camera
          </p>

        </article>


        <article className="live-stat-card">

          <div className="live-stat-card-top">

            <div className="live-stat-icon">

              <Sparkles
                size={18}
              />

            </div>

          </div>

          <span>
            Average Confidence
          </span>

          <strong>
            {data.averageConfidence ===
            null
              ? "—"
              : formatConfidence(
                  data.averageConfidence
                )}
          </strong>

          <p>
            {data.averageConfidence ===
            null
              ? "Available after ML integration"
              : "Calculated from real predictions"}
          </p>

        </article>

      </section>


      {/* =================================================
          ACTIVITY + BREEDS
      ================================================= */}

      <section className="live-dashboard-grid">

        <article className="live-dashboard-panel">

          <div className="live-panel-heading">

            <h2>
              Detection Activity
            </h2>

            <span>
              Last 7 days
            </span>

          </div>


          <div className="live-dashboard-chart">

            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <AreaChart
                data={
                  data.activity
                }
              >

                <defs>

                  <linearGradient
                    id="breedVisionActivity"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="5%"
                      stopColor="#2dd881"
                      stopOpacity={
                        0.28
                      }
                    />

                    <stop
                      offset="95%"
                      stopColor="#2dd881"
                      stopOpacity={
                        0
                      }
                    />

                  </linearGradient>

                </defs>


                <CartesianGrid
                  stroke="rgba(255,255,255,0.04)"
                  vertical={
                    false
                  }
                />


                <XAxis
                  dataKey="day"
                  axisLine={
                    false
                  }
                  tickLine={
                    false
                  }
                  tick={{
                    fill:
                      "#607469",

                    fontSize:
                      9,
                  }}
                />


                <YAxis
                  allowDecimals={
                    false
                  }
                  axisLine={
                    false
                  }
                  tickLine={
                    false
                  }
                  width={28}
                  tick={{
                    fill:
                      "#607469",

                    fontSize:
                      9,
                  }}
                />


                <Tooltip
                  content={({
                    active,
                    payload,
                    label,
                  }) => {
                    if (
                      !active ||
                      !payload?.length
                    ) {
                      return null;
                    }


                    return (
                      <div className="live-chart-tooltip">

                        <strong>
                          {label}
                        </strong>

                        <div>
                          {payload[0]
                            .value}
                          {" "}
                          detection
                          {payload[0]
                            .value ===
                          1
                            ? ""
                            : "s"}
                        </div>

                      </div>
                    );
                  }}
                />


                <Area
                  type="monotone"
                  dataKey="detections"
                  stroke="#2dd881"
                  strokeWidth={
                    2
                  }
                  fill="url(#breedVisionActivity)"
                />

              </AreaChart>
            </ResponsiveContainer>

          </div>

        </article>


        <article className="live-dashboard-panel">

          <div className="live-panel-heading">

            <h2>
              Breed Distribution
            </h2>

            <span>
              Real ML results only
            </span>

          </div>


          {data
            .breedDistribution
            .length === 0 ? (

            <div className="live-breed-empty">

              <Activity
                size={29}
              />

              <h3>
                No breed predictions yet
              </h3>

              <p>
                The classifier is not connected,
                so BreedVision will not fabricate
                breed analytics.
              </p>

            </div>

          ) : (

            <div className="live-breed-list">

              {data
                .breedDistribution
                .slice(
                  0,
                  5
                )
                .map(
                  (
                    item
                  ) => (

                    <div
                      className="live-breed-row"
                      key={
                        item.breed
                      }
                    >

                      <span>
                        {item.breed}
                      </span>

                      <strong>
                        {item.count}
                      </strong>

                    </div>

                  )
                )}

            </div>

          )}

        </article>

      </section>


      {/* =================================================
          RECENT DETECTIONS
      ================================================= */}

      <section className="live-dashboard-panel">

        <div className="live-panel-heading">

          <h2>
            Recent Detections
          </h2>

          <button
            type="button"
            className="live-dashboard-button"
            onClick={() =>
              navigate(
                "/history"
              )
            }
          >
            View History
          </button>

        </div>


        {data
          .recentDetections
          .length === 0 ? (

          <div className="live-dashboard-empty">

            <FileImage
              size={29}
            />

            <h3>
              No detections yet
            </h3>

            <p>
              Upload or capture your first
              livestock image to populate
              this dashboard.
            </p>

          </div>

        ) : (

          <div className="live-recent-list">

            {data
              .recentDetections
              .map(
                (
                  detection
                ) => (

                  <div
                    className="live-recent-row"
                    key={
                      detection.id
                    }
                  >

                    <div className="live-recent-image">

                      {detection.signed_url ? (

                        <img
                          src={
                            detection.signed_url
                          }
                          alt={
                            detection.original_filename ||
                            "Detection"
                          }
                        />

                      ) : (

                        <ImageOff
                          size={19}
                        />

                      )}

                    </div>


                    <div className="live-recent-info">

                      <strong>
                        {detection.predicted_breed ||
                          "Awaiting ML prediction"}
                      </strong>

                      <span>
                        {formatDate(
                          detection.created_at
                        )}
                        {" • "}
                        {detection.source ===
                        "camera"
                          ? "Camera"
                          : "Upload"}
                      </span>

                    </div>


                    <span className="live-recent-status">
                      {detection.review_status}
                    </span>

                  </div>

                )
              )}

          </div>

        )}

      </section>

    </div>
  );
}


export default Dashboard;