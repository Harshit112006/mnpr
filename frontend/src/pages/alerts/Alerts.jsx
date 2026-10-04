import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  AlertTriangle,
  Bell,
  Check,
  LoaderCircle,
  RefreshCw,
  Trash2,
  X,
} from "lucide-react";

import {
  deleteAlert,
  dismissAlert,
  getAlerts,
  markAlertAsRead,
  markAllAlertsAsRead,
} from "../../services/phase9/alertService";

import "../../styles/Phase9.css";


function Alerts() {

  const [alerts, setAlerts] =
    useState([]);

  const [filter, setFilter] =
    useState("all");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  const loadAlerts =
    useCallback(async () => {

      try {

        setLoading(true);
        setError("");

        setAlerts(
          await getAlerts()
        );

      }

      catch (
        loadError
      ) {

        setError(
          loadError.message ||
          "Unable to load alerts."
        );

      }

      finally {

        setLoading(false);

      }

    }, []);


  useEffect(() => {
    loadAlerts();
  }, [
    loadAlerts,
  ]);


  const visibleAlerts =
    useMemo(() => {

      if (
        filter ===
        "all"
      ) {
        return alerts;
      }


      return alerts.filter(
        (
          alert
        ) =>
          alert.status ===
          filter
      );

    }, [
      alerts,
      filter,
    ]);


  const runAction =
    async (
      action
    ) => {

      try {
        setError("");
        await action();
        await loadAlerts();
      }

      catch (
        actionError
      ) {

        setError(
          actionError.message ||
          "Alert action failed."
        );
      }
    };


  if (loading) {

    return (
      <div className="phase9-loading">
        <LoaderCircle
          className="phase9-spinner"
          size={32}
        />
        <h3>
          Loading alerts
        </h3>
      </div>
    );
  }


  return (
    <div className="phase9-page">

      <section className="phase9-header">

        <div>
          <span className="phase9-eyebrow">
            OPERATIONS CENTER
          </span>

          <h1>
            Alerts
          </h1>

          <p>
            Review warnings generated from
            real detection workflow events.
          </p>
        </div>


        <div className="phase9-actions">

          <button
            className="phase9-secondary"
            onClick={
              loadAlerts
            }
          >
            <RefreshCw size={16} />
            Refresh
          </button>


          <button
            className="phase9-primary"
            onClick={() =>
              runAction(
                markAllAlertsAsRead
              )
            }
          >
            <Check size={16} />
            Mark all read
          </button>

        </div>

      </section>


      <section className="phase9-summary-grid">

        <div className="phase9-summary-card">
          <Bell size={21} />
          <div>
            <span>Total</span>
            <strong>
              {alerts.length}
            </strong>
          </div>
        </div>


        <div className="phase9-summary-card">
          <AlertTriangle size={21} />
          <div>
            <span>Unread</span>
            <strong>
              {
                alerts.filter(
                  (
                    alert
                  ) =>
                    alert.status ===
                    "unread"
                ).length
              }
            </strong>
          </div>
        </div>

      </section>


      {error && (
        <div className="phase9-error">
          {error}
        </div>
      )}


      <section className="phase9-toolbar">

        <div className="phase9-tabs">

          {
            [
              "all",
              "unread",
              "read",
              "dismissed",
            ].map(
              (
                item
              ) => (
                <button
                  key={item}
                  type="button"
                  className={
                    filter === item
                      ? "active"
                      : ""
                  }
                  onClick={() =>
                    setFilter(
                      item
                    )
                  }
                >
                  {item}
                </button>
              )
            )
          }

        </div>

      </section>


      {
        visibleAlerts.length ===
        0 ? (

          <div className="phase9-empty">
            <Bell size={35} />
            <h2>
              No alerts
            </h2>
          </div>

        ) : (

          <div className="alert-list">

            {
              visibleAlerts.map(
                (
                  alert
                ) => (

                  <article
                    key={alert.id}
                    className={`alert-card ${alert.severity}`}
                  >

                    <div className="alert-icon">
                      <AlertTriangle size={20} />
                    </div>


                    <div className="alert-content">

                      <div className="alert-heading">

                        <div>
                          <span>
                            {
                              alert.alert_type
                                ?.replaceAll(
                                  "_",
                                  " "
                                )
                                .toUpperCase()
                            }
                          </span>

                          <h3>
                            {alert.title}
                          </h3>
                        </div>


                        <span className={`phase9-status ${alert.status}`}>
                          {alert.status}
                        </span>

                      </div>


                      <p>
                        {alert.message}
                      </p>


                      <small>
                        {
                          new Date(
                            alert.created_at
                          ).toLocaleString(
                            "en-IN"
                          )
                        }
                      </small>


                      <div className="phase9-card-actions">

                        {
                          alert.status ===
                          "unread" && (

                            <button
                              onClick={() =>
                                runAction(
                                  () =>
                                    markAlertAsRead(
                                      alert.id
                                    )
                                )
                              }
                            >
                              <Check size={15} />
                              Mark read
                            </button>

                          )
                        }


                        {
                          alert.status !==
                          "dismissed" && (

                            <button
                              onClick={() =>
                                runAction(
                                  () =>
                                    dismissAlert(
                                      alert.id
                                    )
                                )
                              }
                            >
                              <X size={15} />
                              Dismiss
                            </button>

                          )
                        }


                        <button
                          className="danger"
                          onClick={() =>
                            runAction(
                              () =>
                                deleteAlert(
                                  alert.id
                                )
                            )
                          }
                        >
                          <Trash2 size={15} />
                          Delete
                        </button>

                      </div>

                    </div>

                  </article>

                )
              )
            }

          </div>

        )
      }

    </div>
  );
}


export default Alerts;