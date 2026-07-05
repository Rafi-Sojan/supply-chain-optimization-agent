import DataTable from "../components/DataTable.jsx";
import { AllocationQuantityChart, OptimizationCostChart, RouteNetworkChart } from "../charts/Visualizations.jsx";

const columns = [
  { key: "warehouse_id", label: "Warehouse" },
  { key: "customer_id", label: "Customer" },
  { key: "product_id", label: "Product" },
  { key: "quantity", label: "Quantity" },
  { key: "unit_shipping_cost", label: "Unit Cost" },
  { key: "total_cost", label: "Total Cost" },
];

export default function Optimization({ optimization, routeNetwork }) {
  return (
    <section className="module-panel">
      <div className="module-header">
        <h2>Warehouse Allocation Optimization</h2>
        <p>Cost-minimizing allocation subject to demand and inventory constraints.</p>
      </div>
      {optimization ? (
        <>
          <div className="result-strip">
            <strong>Total cost: Rs. {optimization.total_cost.toLocaleString()}</strong>
            <span>Status: {optimization.status}</span>
            <span>{optimization.recommendation}</span>
          </div>
          <div className="visual-grid">
            <OptimizationCostChart optimization={optimization} />
            <AllocationQuantityChart optimization={optimization} />
          </div>
          <div className="visual-grid single">
            <RouteNetworkChart routeNetwork={routeNetwork} />
          </div>
          <DataTable rows={optimization.allocations} columns={columns} />
        </>
      ) : (
        <div className="empty-state">Loading optimization result...</div>
      )}
    </section>
  );
}
