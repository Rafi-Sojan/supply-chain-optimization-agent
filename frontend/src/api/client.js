const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json();
}

export const api = {
  summary: () => request("/dashboard/summary"),
  dataStatus: () => request("/data/status"),
  products: () => request("/products"),
  supplierRanking: () => request("/suppliers/ranking"),
  reorderPlan: () => request("/inventory/reorder-plan"),
  forecast: (payload = { horizon_months: 1, method: "linear_trend" }) =>
    request("/forecast/demand", { method: "POST", body: JSON.stringify(payload) }),
  optimize: (payload = { scenario_name: "Base Case" }) =>
    request("/optimize/warehouse-allocation", { method: "POST", body: JSON.stringify(payload) }),
  runScenario: (payload) =>
    request("/scenarios/run", { method: "POST", body: JSON.stringify(payload) }),
};
