import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const colors = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2", "#db2777", "#475569"];

function sumBy(rows, keySelector, valueSelector) {
  const totals = new Map();
  rows.forEach((row) => {
    const key = keySelector(row);
    totals.set(key, (totals.get(key) ?? 0) + Number(valueSelector(row) ?? 0));
  });
  return [...totals.entries()].map(([name, value]) => ({ name, value }));
}

function topRows(rows, key, limit = 12) {
  return [...rows].sort((a, b) => Number(b[key] ?? 0) - Number(a[key] ?? 0)).slice(0, limit);
}

function riskData(rows, key) {
  return sumBy(rows, (row) => row[key] ?? "Unknown", () => 1).sort((a, b) => b.value - a.value);
}

export function ChartFrame({ title, subtitle, children }) {
  return (
    <section className="chart-frame">
      <div className="chart-title">
        <h3>{title}</h3>
        {subtitle ? <p>{subtitle}</p> : null}
      </div>
      {children}
    </section>
  );
}

export function DatasetRowsChart({ dataStatus }) {
  const rows = Object.entries(dataStatus?.row_counts ?? {}).map(([name, value]) => ({ name, rows: value }));
  return (
    <ChartFrame title="Dataset Coverage" subtitle={dataStatus?.dataset_name ?? "Active CSV rows"}>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" interval={0} angle={-18} textAnchor="end" height={70} />
          <YAxis />
          <Tooltip />
          <Bar dataKey="rows" fill="#2563eb" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}

export function ForecastChart({ forecasts }) {
  const rows = topRows(forecasts, "forecasted_demand").map((row) => ({
    name: `${row.product_id}/${String(row.region).replace(" - DataCo Customer", "")}`,
    previous: row.previous_month_demand,
    forecast: row.forecasted_demand,
  }));
  return (
    <ChartFrame title="Forecast vs Previous Demand" subtitle="Top forecasted product-customer pairs">
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" interval={0} angle={-22} textAnchor="end" height={82} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="previous" fill="#94a3b8" radius={[4, 4, 0, 0]} />
          <Line dataKey="forecast" stroke="#2563eb" strokeWidth={3} dot={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}

export function ForecastRiskChart({ forecasts }) {
  return <RiskPie title="Forecast Risk Mix" rows={riskData(forecasts, "risk_level")} />;
}

export function InventoryChart({ reorderPlan }) {
  const rows = topRows(reorderPlan, "recommended_reorder_quantity").map((row) => ({
    name: `${row.warehouse_id}/${row.product_id}`,
    available: row.available_inventory,
    reorderPoint: row.reorder_point,
    reorderQty: row.recommended_reorder_quantity,
  }));
  return (
    <ChartFrame title="Inventory Position" subtitle="Largest reorder recommendations">
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" interval={0} angle={-22} textAnchor="end" height={82} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="available" fill="#16a34a" radius={[4, 4, 0, 0]} />
          <Bar dataKey="reorderQty" fill="#f59e0b" radius={[4, 4, 0, 0]} />
          <Line dataKey="reorderPoint" stroke="#dc2626" strokeWidth={3} dot={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}

export function InventoryRiskChart({ reorderPlan }) {
  return <RiskPie title="Stockout Risk Mix" rows={riskData(reorderPlan, "stockout_risk")} />;
}

export function SupplierScoreChart({ suppliers }) {
  const rows = topRows(suppliers, "score").map((row) => ({
    name: row.product_id,
    score: row.score,
    reliability: row.reliability_score,
  }));
  return (
    <ChartFrame title="Supplier Scorecard" subtitle="Score and reliability by product supplier">
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" interval={0} angle={-22} textAnchor="end" height={78} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="score" fill="#2563eb" radius={[4, 4, 0, 0]} />
          <Line dataKey="reliability" stroke="#16a34a" strokeWidth={3} dot={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}

export function SupplierCostReliabilityChart({ suppliers }) {
  const rows = suppliers.map((row) => ({
    name: row.product_id,
    unitCost: row.unit_cost,
    reliability: row.reliability_score,
    score: row.score,
  }));
  return (
    <ChartFrame title="Cost vs Reliability" subtitle="Each point is a supplier-product pair">
      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="unitCost" name="Unit Cost" type="number" />
          <YAxis dataKey="reliability" name="Reliability" type="number" />
          <Tooltip cursor={{ strokeDasharray: "3 3" }} />
          <Scatter data={rows} fill="#7c3aed" name="Suppliers" />
        </ScatterChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}

export function OptimizationCostChart({ optimization }) {
  const rows = sumBy(optimization?.allocations ?? [], (row) => row.warehouse_id, (row) => row.total_cost)
    .sort((a, b) => b.value - a.value)
    .map((row) => ({ ...row, cost: Number(row.value.toFixed(2)) }));
  return (
    <ChartFrame title="Cost by Warehouse" subtitle="Allocated transportation cost">
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="cost" fill="#2563eb" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}

export function AllocationQuantityChart({ optimization }) {
  const rows = sumBy(optimization?.allocations ?? [], (row) => row.product_id, (row) => row.quantity)
    .sort((a, b) => b.value - a.value)
    .slice(0, 12);
  return (
    <ChartFrame title="Allocated Quantity by Product" subtitle="Top products in the optimized plan">
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" interval={0} angle={-22} textAnchor="end" height={78} />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value" fill="#16a34a" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}

export function RouteNetworkChart({ routeNetwork }) {
  const nodes = routeNetwork?.nodes ?? [];
  const edges = routeNetwork?.edges ?? [];
  if (!nodes.length) {
    return (
      <ChartFrame title="Route Network" subtitle="No route network loaded">
        <div className="empty-state">No route nodes available.</div>
      </ChartFrame>
    );
  }

  const width = 760;
  const height = 340;
  const lats = nodes.map((node) => Number(node.latitude));
  const lons = nodes.map((node) => Number(node.longitude));
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLon = Math.min(...lons);
  const maxLon = Math.max(...lons);
  const scaleX = (lon) => 30 + ((Number(lon) - minLon) / Math.max(1, maxLon - minLon)) * (width - 60);
  const scaleY = (lat) => height - 30 - ((Number(lat) - minLat) / Math.max(1, maxLat - minLat)) * (height - 60);
  const byId = new Map(nodes.map((node) => [node.node_id, node]));

  return (
    <ChartFrame title="Route Network" subtitle={`${nodes.length} nodes and ${edges.length} delivery edges`}>
      <div className="network-wrap">
        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Route network map">
          {edges.slice(0, 260).map((edge, index) => {
            const start = byId.get(edge.from_node);
            const end = byId.get(edge.to_node);
            if (!start || !end) return null;
            return (
              <line
                key={`${edge.from_node}-${edge.to_node}-${index}`}
                x1={scaleX(start.longitude)}
                y1={scaleY(start.latitude)}
                x2={scaleX(end.longitude)}
                y2={scaleY(end.latitude)}
                stroke="#cbd5e1"
                strokeWidth="1"
              />
            );
          })}
          {nodes.map((node) => {
            const isWarehouse = String(node.node_id).startsWith("WH_");
            return (
              <g key={node.node_id}>
                <circle
                  cx={scaleX(node.longitude)}
                  cy={scaleY(node.latitude)}
                  r={isWarehouse ? 7 : 4}
                  fill={isWarehouse ? "#2563eb" : "#16a34a"}
                  stroke="#ffffff"
                  strokeWidth="2"
                />
                {isWarehouse ? (
                  <text x={scaleX(node.longitude) + 9} y={scaleY(node.latitude) + 4} fontSize="11" fill="#334155">
                    {node.node_id.replace("WH_", "")}
                  </text>
                ) : null}
              </g>
            );
          })}
        </svg>
      </div>
    </ChartFrame>
  );
}

export function RiskPie({ title, rows }) {
  return (
    <ChartFrame title={title} subtitle="Count by category">
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie data={rows} dataKey="value" nameKey="name" innerRadius={58} outerRadius={92} paddingAngle={2}>
            {rows.map((entry, index) => (
              <Cell key={entry.name} fill={colors[index % colors.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}
