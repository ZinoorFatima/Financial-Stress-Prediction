// Side-by-side comparison of stressed expected loss across scenarios.
import type { ScenarioComparison } from "../types";
import { fmtCurrency, fmtPct } from "../format";
import { Plot } from "./Plot";

export function ComparisonChart({ data }: { data: ScenarioComparison[] }) {
  return (
    <div className="panel">
      <h2>Scenario comparison</h2>
      <Plot
        title="Stressed expected loss by scenario"
        data={[
          {
            type: "bar",
            x: data.map((d) => d.scenario_name),
            y: data.map((d) => d.total_stressed_expected_loss),
            marker: { color: "#38bdf8" },
            text: data.map((d) => fmtCurrency(d.total_stressed_expected_loss)),
            textposition: "auto",
          },
        ]}
      />
      <table>
        <thead>
          <tr>
            <th>Scenario</th>
            <th>Stressed EL</th>
            <th>Δ EL</th>
            <th>Value Δ</th>
            <th>Loss ratio</th>
          </tr>
        </thead>
        <tbody>
          {data.map((d) => (
            <tr key={d.scenario_name}>
              <td>{d.scenario_name}</td>
              <td>{fmtCurrency(d.total_stressed_expected_loss)}</td>
              <td style={{ color: d.total_expected_loss_change > 0 ? "#f87171" : "#34d399" }}>
                {fmtCurrency(d.total_expected_loss_change)}
              </td>
              <td style={{ color: d.total_value_change < 0 ? "#f87171" : "#34d399" }}>
                {fmtCurrency(d.total_value_change)}
              </td>
              <td>{fmtPct(d.stressed_loss_ratio)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
