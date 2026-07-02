import { useState } from "react";
import CostBarChart from "../charts/CostBarChart.jsx";

export default function Scenarios({ scenario, onRunScenario }) {
  const [form, setForm] = useState({
    scenario_name: "Fuel cost +20%",
    demand_multiplier: 1,
    fuel_cost_multiplier: 1.2,
    supplier_reliability_multiplier: 1,
    disabled_warehouses: [],
  });

  const costData = scenario
    ? [
        { name: "Base", cost: scenario.base_cost },
        { name: "Scenario", cost: scenario.scenario_cost },
      ]
    : [];

  return (
    <section className="module-panel">
      <div className="module-header">
        <h2>What-if Simulation</h2>
        <p>Compare base case against demand, fuel cost, reliability, and warehouse disruption scenarios.</p>
      </div>

      <form
        className="scenario-form"
        onSubmit={(event) => {
          event.preventDefault();
          onRunScenario(form);
        }}
      >
        <label>
          Scenario
          <input value={form.scenario_name} onChange={(event) => setForm({ ...form, scenario_name: event.target.value })} />
        </label>
        <label>
          Demand multiplier
          <input
            type="number"
            step="0.1"
            value={form.demand_multiplier}
            onChange={(event) => setForm({ ...form, demand_multiplier: Number(event.target.value) })}
          />
        </label>
        <label>
          Fuel cost multiplier
          <input
            type="number"
            step="0.1"
            value={form.fuel_cost_multiplier}
            onChange={(event) => setForm({ ...form, fuel_cost_multiplier: Number(event.target.value) })}
          />
        </label>
        <button type="submit">Run Scenario</button>
      </form>

      {scenario ? (
        <div className="scenario-results">
          <CostBarChart data={costData} />
          <div className="result-strip">
            <strong>Change: Rs. {scenario.cost_difference.toLocaleString()}</strong>
            <span>{scenario.percentage_change}%</span>
            <span>Risk: {scenario.risk_level}</span>
            <span>{scenario.recommendation}</span>
          </div>
        </div>
      ) : null}
    </section>
  );
}
