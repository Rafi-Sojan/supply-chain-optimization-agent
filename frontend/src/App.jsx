import { BarChart3, Boxes, Factory, Gauge, LineChart, Route } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "./api/client.js";
import Forecasting from "./pages/Forecasting.jsx";
import Inventory from "./pages/Inventory.jsx";
import Optimization from "./pages/Optimization.jsx";
import Overview from "./pages/Overview.jsx";
import Scenarios from "./pages/Scenarios.jsx";
import Suppliers from "./pages/Suppliers.jsx";

const tabs = [
  { id: "overview", label: "Overview", icon: Gauge },
  { id: "forecast", label: "Forecasting", icon: LineChart },
  { id: "inventory", label: "Inventory", icon: Boxes },
  { id: "suppliers", label: "Suppliers", icon: Factory },
  { id: "optimization", label: "Optimization", icon: Route },
  { id: "scenarios", label: "Scenarios", icon: BarChart3 },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("overview");
  const [summary, setSummary] = useState(null);
  const [dataStatus, setDataStatus] = useState(null);
  const [forecastMethod, setForecastMethod] = useState("random_forest");
  const [forecasts, setForecasts] = useState([]);
  const [reorderPlan, setReorderPlan] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [optimization, setOptimization] = useState(null);
  const [routeNetwork, setRouteNetwork] = useState(null);
  const [scenario, setScenario] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      setError("");
      const requests = [
        ["summary", api.summary(), setSummary],
        ["data status", api.dataStatus(), setDataStatus],
        ["forecast", api.forecast({ horizon_months: 1, method: forecastMethod }), setForecasts],
        ["inventory", api.reorderPlan(), setReorderPlan],
        ["suppliers", api.supplierRanking(), setSuppliers],
        ["optimization", api.optimize({ scenario_name: "Base Case" }), setOptimization],
        ["route network", api.routeNetwork(), setRouteNetwork],
      ];

      requests.forEach(([label, promise, setter]) => {
        promise.then(setter).catch((requestError) => {
          setError((current) => [current, `${label}: ${requestError.message}`].filter(Boolean).join("; "));
        });
      });
    }

    loadDashboard();
  }, [forecastMethod]);

  const runScenario = async (payload) => {
    try {
      setScenario(await api.runScenario(payload));
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  const panels = {
    overview: <Overview summary={summary} dataStatus={dataStatus} />,
    forecast: <Forecasting forecasts={forecasts} method={forecastMethod} onMethodChange={setForecastMethod} />,
    inventory: <Inventory reorderPlan={reorderPlan} />,
    suppliers: <Suppliers suppliers={suppliers} />,
    optimization: <Optimization optimization={optimization} routeNetwork={routeNetwork} />,
    scenarios: <Scenarios scenario={scenario} onRunScenario={runScenario} />,
  };

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span>SC</span>
          <div>
            <strong>Supply Chain</strong>
            <small>Optimization Platform</small>
          </div>
        </div>
        <nav>
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                className={activeTab === tab.id ? "active" : ""}
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                type="button"
              >
                <Icon size={18} />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <h1>Supply Chain Optimization Platform</h1>
            <p>Forecast demand, rank suppliers, optimize warehouse allocation, and simulate disruptions.</p>
          </div>
        </header>
        {error ? <div className="error-banner">{error}</div> : null}
        {panels[activeTab]}
      </section>
    </main>
  );
}
