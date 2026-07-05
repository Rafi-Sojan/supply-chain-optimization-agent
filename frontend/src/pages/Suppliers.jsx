import DataTable from "../components/DataTable.jsx";
import { SupplierCostReliabilityChart, SupplierScoreChart } from "../charts/Visualizations.jsx";

const columns = [
  { key: "supplier_name", label: "Supplier" },
  { key: "product_id", label: "Product" },
  { key: "unit_cost", label: "Unit Cost" },
  { key: "lead_time_days", label: "Lead Time" },
  { key: "reliability_score", label: "Reliability" },
  { key: "score", label: "Score" },
  { key: "risk_level", label: "Risk" },
];

export default function Suppliers({ suppliers }) {
  return (
    <section className="module-panel">
      <div className="module-header">
        <h2>Supplier Ranking</h2>
        <p>Weighted scoring across cost, reliability, lead time, capacity, quality, and delay risk.</p>
      </div>
      <div className="visual-grid">
        <SupplierScoreChart suppliers={suppliers} />
        <SupplierCostReliabilityChart suppliers={suppliers} />
      </div>
      <DataTable rows={suppliers} columns={columns} />
    </section>
  );
}
