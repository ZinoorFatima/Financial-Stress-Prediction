// Results dashboard: KPIs, charts, and per-asset detail for one stress run.
import type { StressResult } from "../types";
import { fmtCurrency, fmtPct, fmtSignedCurrency } from "../format";
import { Plot } from "./Plot";

function Kpi({
  label,
  value,
  delta,
  worse,
}: {
  label: string;
  value: string;
  delta?: string;
  worse?: boolean;
}) {
  return (
    <div className="kpi">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
      {delta && <div className={`delta ${worse ? "up" : "down"}`}>{delta}</div>}
    </div>
  );
}

export function ResultsDashboard({ result }: { result: StressResult }) {
  const elIncreasePct =
    result.total_base_expected_loss > 0
      ? result.total_expected_loss_change / result.total_base_expected_loss
      : 0;

  // Waterfall: base EL -> +ΔEL by asset class -> stressed EL.
  const wfClasses = result.by_asset_class;

  // Top movers by EL change.
  const movers = [...result.assets]
    .sort((a, b) => b.expected_loss_change - a.expected_loss_change)
    .slice(0, 10);

  return (
    <div>
      <div className="kpi-grid">
        <Kpi label="Total exposure" value={fmtCurrency(result.total_exposure)} />
        <Kpi
          label="Stressed expected loss"
          value={fmtCurrency(result.total_stressed_expected_loss)}
          delta={`${fmtSignedCurrency(result.total_expected_loss_change)} (${fmtPct(
            elIncreasePct,
            0,
          )})`}
          worse={result.total_expected_loss_change > 0}
        />
        <Kpi
          label="Stressed loss ratio"
          value={fmtPct(result.stressed_loss_ratio)}
        />
        <Kpi
          label="Portfolio value change"
          value={fmtSignedCurrency(result.total_value_change)}
          worse={result.total_value_change < 0}
        />
      </div>

      <div className="chart-grid">
        <div className="panel">
          <Plot
            title="Expected loss: base vs. stressed by asset class"
            data={[
              {
                type: "bar",
                name: "Base EL",
                x: wfClasses.map((b) => b.key),
                y: wfClasses.map((b) => b.base_expected_loss),
                marker: { color: "#818cf8" },
              },
              {
                type: "bar",
                name: "Stressed EL",
                x: wfClasses.map((b) => b.key),
                y: wfClasses.map((b) => b.stressed_expected_loss),
                marker: { color: "#f87171" },
              },
            ]}
            layout={{ barmode: "group" }}
          />
        </div>

        <div className="panel">
          <Plot
            title="Exposure by currency"
            data={[
              {
                type: "pie",
                labels: result.by_currency.map((b) => b.key),
                values: result.by_currency.map((b) => b.exposure),
                hole: 0.5,
                textinfo: "label+percent",
              },
            ]}
          />
        </div>

        <div className="panel">
          <Plot
            title="Expected-loss increase by asset class"
            data={[
              {
                type: "bar",
                orientation: "h",
                x: wfClasses.map((b) => b.expected_loss_change),
                y: wfClasses.map((b) => b.key),
                marker: { color: "#fbbf24" },
              },
            ]}
          />
        </div>

        <div className="panel">
          <Plot
            title="Value change by currency"
            data={[
              {
                type: "bar",
                x: result.by_currency.map((b) => b.key),
                y: result.by_currency.map((b) => b.value_change),
                marker: {
                  color: result.by_currency.map((b) =>
                    b.value_change < 0 ? "#f87171" : "#34d399",
                  ),
                },
              },
            ]}
          />
        </div>
      </div>

      <div className="panel">
        <h2>Top 10 movers by expected-loss increase</h2>
        <table>
          <thead>
            <tr>
              <th>Asset</th>
              <th>Class</th>
              <th>Ccy</th>
              <th>Base EL</th>
              <th>Stressed EL</th>
              <th>Δ EL</th>
              <th>Stressed PD</th>
              <th>Stressed LGD</th>
              <th>Value Δ</th>
            </tr>
          </thead>
          <tbody>
            {movers.map((a) => (
              <tr key={a.asset_id}>
                <td>{a.asset_id}</td>
                <td>{a.asset_class}</td>
                <td>{a.currency}</td>
                <td>{fmtCurrency(a.base_expected_loss)}</td>
                <td>{fmtCurrency(a.stressed_expected_loss)}</td>
                <td style={{ color: a.expected_loss_change > 0 ? "#f87171" : "#34d399" }}>
                  {fmtSignedCurrency(a.expected_loss_change)}
                </td>
                <td>{fmtPct(a.stressed_pd)}</td>
                <td>{fmtPct(a.stressed_lgd)}</td>
                <td style={{ color: a.value_change < 0 ? "#f87171" : "#34d399" }}>
                  {fmtSignedCurrency(a.value_change)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
