import MetricCard from "../components/MetricCard.jsx";
import { DatasetRowsChart } from "../charts/Visualizations.jsx";

export default function Overview({ summary, dataStatus }) {
  if (!summary) return <div className="empty-state">Loading dashboard summary...</div>;

  return (
    <div className="page-grid">
      <MetricCard label="Optimized Cost" value={`Rs. ${summary.optimized_cost.toLocaleString()}`} detail={summary.optimization_status} />
      <MetricCard label="Products" value={summary.total_products} detail="Active SKUs" />
      <MetricCard label="Warehouses" value={summary.total_warehouses} detail="Allocation sources" />
      <MetricCard
        label="Data Source"
        value={dataStatus?.dataset_name ?? dataStatus?.source ?? "sample"}
        detail={dataStatus?.valid ? "Validated CSVs" : "Validation issue"}
      />
      <MetricCard label="High Risk Inventory" value={summary.high_risk_inventory_items} detail="Needs reorder review" />
      <section className="wide-panel">
        <h2>Executive Recommendation</h2>
        <p>{summary.recommendation}</p>
        {summary.best_supplier ? (
          <p>
            Best supplier: <strong>{summary.best_supplier.supplier_name}</strong> with score{" "}
            <strong>{summary.best_supplier.score}</strong>.
          </p>
        ) : null}
        {dataStatus?.errors?.length ? <p>Data issue: {dataStatus.errors.join("; ")}</p> : null}
      </section>
      <DatasetRowsChart dataStatus={dataStatus} />
    </div>
  );
}
