function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
}) {
  return (
    <div className="dashboard-stat-card">
      <div className="stat-card-top">
        <div>
          <p className="stat-card-title">{title}</p>
          <h3>{value}</h3>
        </div>

        <div className="stat-card-icon">
          <Icon size={21} />
        </div>
      </div>

      <p className="stat-card-subtitle">
        {subtitle}
      </p>
    </div>
  );
}

export default StatCard;