import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  Download,
  FileJson,
  FileSpreadsheet,
  FileText,
  LoaderCircle,
  RefreshCw,
} from "lucide-react";

import {
  buildOperationsReport,
  downloadDetectionsCsv,
  downloadOperationsJson,
} from "../../services/phase9/reportService";

import "../../styles/Phase9.css";


function Reports() {

  const [report, setReport] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [exporting, setExporting] =
    useState(false);

  const [error, setError] =
    useState("");


  const loadReport =
    useCallback(async () => {

      try {

        setLoading(true);
        setError("");

        setReport(
          await buildOperationsReport()
        );

      }

      catch (
        reportError
      ) {

        setError(
          reportError.message ||
          "Unable to build report."
        );

      }

      finally {

        setLoading(false);

      }

    }, []);


  useEffect(() => {
    loadReport();
  }, [
    loadReport,
  ]);


  const exportFile =
    async (
      callback
    ) => {

      try {

        setExporting(true);
        setError("");

        await callback();

      }

      catch (
        exportError
      ) {

        setError(
          exportError.message ||
          "Export failed."
        );

      }

      finally {

        setExporting(false);

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
          Building operational report
        </h3>
      </div>
    );
  }


  const summary =
    report?.summary ||
    {};


  return (
    <div className="phase9-page">

      <section className="phase9-header">

        <div>
          <span className="phase9-eyebrow">
            DATA EXPORT
          </span>

          <h1>
            Reports
          </h1>

          <p>
            Export your actual BreedVision
            operational data without generated
            or placeholder metrics.
          </p>
        </div>


        <button
          className="phase9-secondary"
          onClick={
            loadReport
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
          <FileText size={21} />
          <div>
            <span>Detections</span>
            <strong>
              {summary.detections || 0}
            </strong>
          </div>
        </div>


        <div className="phase9-summary-card">
          <FileText size={21} />
          <div>
            <span>Farmers</span>
            <strong>
              {summary.farmers || 0}
            </strong>
          </div>
        </div>


        <div className="phase9-summary-card">
          <FileText size={21} />
          <div>
            <span>Animals</span>
            <strong>
              {summary.animals || 0}
            </strong>
          </div>
        </div>


        <div className="phase9-summary-card">
          <FileText size={21} />
          <div>
            <span>Reviews</span>
            <strong>
              {summary.reviews || 0}
            </strong>
          </div>
        </div>

      </section>


      <section className="report-grid">

        <article className="report-card">

          <FileJson size={30} />

          <h2>
            Complete JSON Report
          </h2>

          <p>
            Includes summary statistics,
            distributions and current
            operational records.
          </p>

          <button
            className="phase9-primary"
            disabled={
              exporting
            }
            onClick={() =>
              exportFile(
                downloadOperationsJson
              )
            }
          >
            <Download size={16} />
            Download JSON
          </button>

        </article>


        <article className="report-card">

          <FileSpreadsheet size={30} />

          <h2>
            Detection CSV
          </h2>

          <p>
            Export detection metadata,
            prediction information and
            review/link status.
          </p>

          <button
            className="phase9-primary"
            disabled={
              exporting
            }
            onClick={() =>
              exportFile(
                downloadDetectionsCsv
              )
            }
          >
            <Download size={16} />
            Download CSV
          </button>

        </article>

      </section>


      <section className="analytics-panel">

        <span className="phase9-eyebrow">
          REPORT METADATA
        </span>

        <h2>
          Current report snapshot
        </h2>

        <div className="phase9-detail-grid">

          <div>
            <span>
              Generated
            </span>

            <strong>
              {
                report?.generated_at
                  ? new Date(
                      report.generated_at
                    ).toLocaleString(
                      "en-IN"
                    )
                  : "—"
              }
            </strong>
          </div>


          <div>
            <span>
              Review Required
            </span>

            <strong>
              {
                summary.review_required ||
                0
              }
            </strong>
          </div>


          <div>
            <span>
              Alerts
            </span>

            <strong>
              {summary.alerts || 0}
            </strong>
          </div>

        </div>

      </section>

    </div>
  );
}


export default Reports;