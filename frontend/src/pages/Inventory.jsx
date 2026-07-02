import DataTable from "../components/DataTable.jsx";

const columns = [
  { key: "warehouse_id", label: "Warehouse" },
  { key: "product_id", label: "Product" },
  { key: "available_inventory", label: "Available" },
  { key: "reorder_point", label: "Reorder Point" },
  { key: "safety_stock", label: "Safety Stock" },
  { key: "recommended_reorder_quantity", label: "Reorder Qty" },
  { key: "stockout_risk", label: "Stockout Risk" },
];

export default function Inventory({ reorderPlan }) {
  return (
    <section className="module-panel">
      <div className="module-header">
        <h2>Inventory Reorder Planning</h2>
        <p>Safety stock and reorder point recommendations using demand volatility and lead time.</p>
      </div>
      <DataTable rows={reorderPlan} columns={columns} />
    </section>
  );
}
