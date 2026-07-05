import { useState } from "react";
import CostBarChart from "../charts/CostBarChart.jsx";
import { ChartFrame } from "../charts/Visualizations.jsx";

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
          <div className="visual-grid">
            <ChartFrame title="Scenario Cost Comparison" subtitle="Base plan vs changed assumptions">
              <CostBarChart data={costData} bare />
            </ChartFrame>
            <ChartFrame title="Scenario Impact" subtitle="Cost change and allocation movement">
              <div className="impact-metrics">
                <div>
                  <span>Cost Difference</span>
                  <strong>Rs. {scenario.cost_difference.toLocaleString()}</strong>
                </div>
                <div>
                  <span>Percentage Change</span>
                  <strong>{scenario.percentage_change}%</strong>
                </div>
                <div>
                  <span>Changed Allocations</span>
                  <strong>{scenario.changed_allocation_count}</strong>
                </div>
                <div>
                  <span>Risk</span>
                  <strong>{scenario.risk_level}</strong>
                </div>
              </div>
            </ChartFrame>
          </div>
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
