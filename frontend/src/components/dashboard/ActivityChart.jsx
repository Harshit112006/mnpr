import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const activityData = [
  { day: "Mon", predictions: 0 },
  { day: "Tue", predictions: 0 },
  { day: "Wed", predictions: 0 },
  { day: "Thu", predictions: 0 },
  { day: "Fri", predictions: 0 },
  { day: "Sat", predictions: 0 },
  { day: "Sun", predictions: 0 },
];

function ActivityChart() {
  return (
    <div className="dashboard-panel activity-panel">
      <div className="panel-header">
        <div>
          <h3>Prediction Activity</h3>
          <p>Breed identification requests over the last 7 days</p>
        </div>

        <span className="panel-badge">7 DAYS</span>
      </div>

      <div className="activity-chart">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={activityData}>
            <defs>
              <linearGradient
                id="predictionGradient"
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop
                  offset="0%"
                  stopColor="#2dd881"
                  stopOpacity={0.32}
                />

                <stop
                  offset="100%"
                  stopColor="#2dd881"
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>

            <CartesianGrid
              stroke="rgba(255,255,255,0.05)"
              vertical={false}
            />

            <XAxis
              dataKey="day"
              axisLine={false}
              tickLine={false}
              tick={{
                fill: "#6f8378",
                fontSize: 11,
              }}
            />

            <YAxis
              allowDecimals={false}
              axisLine={false}
              tickLine={false}
              tick={{
                fill: "#6f8378",
                fontSize: 11,
              }}
            />

            <Tooltip
              contentStyle={{
                background: "#0b1c15",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: "10px",
                color: "#ffffff",
              }}
            />

            <Area
              type="monotone"
              dataKey="predictions"
              stroke="#2dd881"
              strokeWidth={2}
              fill="url(#predictionGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="empty-chart-note">
        Activity will appear after the first breed prediction.
      </div>
    </div>
  );
}

export default ActivityChart;