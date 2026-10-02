import {
  CheckCircle2,
  AlertTriangle,
  Image,
  Sun,
  Focus,
  Gauge,
} from "lucide-react";

function QualityRow({
  icon: Icon,
  label,
  value,
  passed,
}) {
  return (
    <div className="quality-row">
      <div className="quality-row-left">
        <div className="quality-row-icon">
          <Icon size={16} />
        </div>

        <span>{label}</span>
      </div>

      <div className="quality-row-right">
        <strong>{value}</strong>

        {passed ? (
          <CheckCircle2
            size={16}
            className="quality-pass"
          />
        ) : (
          <AlertTriangle
            size={16}
            className="quality-warning"
          />
        )}
      </div>
    </div>
  );
}

function ImageQualityPanel({ quality }) {
  if (!quality) {
    return null;
  }

  return (
    <div className="image-quality-panel">
      <div className="quality-header">
        <div>
          <span>IMAGE QUALITY CHECK</span>
          <h3>Pre-analysis validation</h3>
        </div>

        <div
          className={`quality-score ${
            quality.suitable
              ? "quality-score-good"
              : "quality-score-warning"
          }`}
        >
          <Gauge size={16} />
          {quality.score}%
        </div>
      </div>

      <QualityRow
        icon={Image}
        label="Resolution"
        value={`${quality.width} × ${quality.height}`}
        passed={quality.resolutionGood}
      />

      <QualityRow
        icon={Sun}
        label="Brightness"
        value={quality.brightnessLabel}
        passed={quality.brightnessGood}
      />

      <QualityRow
        icon={Focus}
        label="Sharpness"
        value={quality.sharpnessLabel}
        passed={quality.sharpnessGood}
      />

      <div
        className={`quality-result ${
          quality.suitable
            ? "quality-result-good"
            : "quality-result-warning"
        }`}
      >
        {quality.suitable ? (
          <>
            <CheckCircle2 size={18} />

            <div>
              <strong>
                Suitable for analysis
              </strong>

              <p>
                Image passed all frontend
                quality checks.
              </p>
            </div>
          </>
        ) : (
          <>
            <AlertTriangle size={18} />

            <div>
              <strong>
                Image quality may be poor
              </strong>

              <p>
                Retake or upload a clearer
                image for better predictions.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default ImageQualityPanel;