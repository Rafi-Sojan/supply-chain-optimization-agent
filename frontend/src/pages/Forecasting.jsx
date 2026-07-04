import DataTable from "../components/DataTable.jsx";

const methods = [
  { id: "linear_trend", label: "Trend" },
  { id: "moving_average", label: "Moving Avg" },
  { id: "linear_regression", label: "Linear Regression" },
  { id: "random_forest", label: "Random Forest" },
  { id: "xgboost", label: "XGBoost" },
];

const columns = [
  { key: "product_id", label: "Product" },
  { key: "region", label: "Region" },
  { key: "previous_month_demand", label: "Previous" },
  { key: "forecasted_demand", label: "Forecast" },
  { key: "trend_percentage", label: "Trend %", render: (row) => `${row.trend_percentage}%` },
  { key: "risk_level", label: "Risk" },
  { key: "model_type", label: "Model" },
  { key: "mape", label: "MAPE", render: (row) => (row.mape == null ? "n/a" : `${row.mape}%`) },
];

export default function Forecasting({ forecasts, method, onMethodChange }) {
  return (
    <section className="module-panel">
      <div className="module-header">
        <h2>Demand Forecasting</h2>
        <p>Explainable statistical forecasts and ML models by product and customer region.</p>
      </div>
      <div className="method-tabs" aria-label="Forecast method">
        {methods.map((item) => (
          <button
            className={method === item.id ? "active" : ""}
            key={item.id}
            onClick={() => onMethodChange(item.id)}
            type="button"
          >
            {item.label}
          </button>
        ))}
      </div>
      <DataTable rows={forecasts} columns={columns} />
    </section>
  );
}
