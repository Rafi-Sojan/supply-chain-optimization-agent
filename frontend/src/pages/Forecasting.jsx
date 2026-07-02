import DataTable from "../components/DataTable.jsx";

const columns = [
  { key: "product_id", label: "Product" },
  { key: "region", label: "Region" },
  { key: "previous_month_demand", label: "Previous" },
  { key: "forecasted_demand", label: "Forecast" },
  { key: "trend_percentage", label: "Trend %", render: (row) => `${row.trend_percentage}%` },
  { key: "risk_level", label: "Risk" },
];

export default function Forecasting({ forecasts }) {
  return (
    <section className="module-panel">
      <div className="module-header">
        <h2>Demand Forecasting</h2>
        <p>Linear trend forecasts by product and customer region.</p>
      </div>
      <DataTable rows={forecasts} columns={columns} />
    </section>
  );
}
