// Scenario builder: pick a preset or craft custom equity/IR/FX/credit shocks.
import { useState } from "react";
import type { Scenario } from "../types";

interface Props {
  presets: Scenario[];
  scenario: Scenario;
  onChange: (s: Scenario) => void;
  onRun: () => void;
  onCompareAll: () => void;
  busy: boolean;
}

export function ScenarioBuilder({
  presets,
  scenario,
  onChange,
  onRun,
  onCompareAll,
  busy,
}: Props) {
  const [newCcy, setNewCcy] = useState("");
  const [newShock, setNewShock] = useState("");

  const set = (patch: Partial<Scenario>) => onChange({ ...scenario, ...patch });

  const addFx = () => {
    const ccy = newCcy.trim().toUpperCase();
    const val = parseFloat(newShock);
    if (!ccy || Number.isNaN(val)) return;
    set({ fx_shocks: { ...scenario.fx_shocks, [ccy]: val / 100 } });
    setNewCcy("");
    setNewShock("");
  };

  const removeFx = (ccy: string) => {
    const next = { ...scenario.fx_shocks };
    delete next[ccy];
    set({ fx_shocks: next });
  };

  return (
    <div className="panel">
      <h2>Scenario</h2>

      <div className="preset-list">
        {presets.map((p) => (
          <button
            key={p.name}
            className={`chip ${scenario.name === p.name ? "active" : ""}`}
            onClick={() => onChange({ ...p })}
            title={p.description}
          >
            {p.name}
          </button>
        ))}
      </div>

      <label>Scenario name</label>
      <input
        type="text"
        value={scenario.name}
        onChange={(e) => set({ name: e.target.value })}
      />

      <label>Equity shock</label>
      <div className="range-row">
        <span>-60%</span>
        <b>{(scenario.equity_shock * 100).toFixed(0)}%</b>
        <span>+30%</span>
      </div>
      <input
        type="range"
        min={-0.6}
        max={0.3}
        step={0.01}
        value={scenario.equity_shock}
        onChange={(e) => set({ equity_shock: parseFloat(e.target.value) })}
      />

      <label>Interest rate shock (bps)</label>
      <div className="range-row">
        <span>-300</span>
        <b>{scenario.rate_shock_bps.toFixed(0)} bps</b>
        <span>+400</span>
      </div>
      <input
        type="range"
        min={-300}
        max={400}
        step={10}
        value={scenario.rate_shock_bps}
        onChange={(e) => set({ rate_shock_bps: parseFloat(e.target.value) })}
      />

      <label>PD stress multiplier</label>
      <div className="range-row">
        <span>1.0x</span>
        <b>{scenario.pd_stress_multiplier.toFixed(2)}x</b>
        <span>3.0x</span>
      </div>
      <input
        type="range"
        min={1}
        max={3}
        step={0.05}
        value={scenario.pd_stress_multiplier}
        onChange={(e) => set({ pd_stress_multiplier: parseFloat(e.target.value) })}
      />

      <label>FX shocks (vs. base, % per currency)</label>
      {Object.entries(scenario.fx_shocks).map(([ccy, v]) => (
        <div className="fx-row" key={ccy}>
          <span>{ccy}</span>
          <span style={{ textAlign: "right" }}>{(v * 100).toFixed(1)}%</span>
          <button onClick={() => removeFx(ccy)}>✕</button>
        </div>
      ))}
      <div className="fx-row">
        <input
          type="text"
          placeholder="EUR"
          value={newCcy}
          onChange={(e) => setNewCcy(e.target.value)}
        />
        <input
          type="number"
          placeholder="-10"
          value={newShock}
          onChange={(e) => setNewShock(e.target.value)}
        />
        <button onClick={addFx}>+</button>
      </div>

      <button onClick={onRun} disabled={busy}>
        {busy ? "Running…" : "Run stress test"}
      </button>
      <button className="secondary" onClick={onCompareAll} disabled={busy}>
        Compare all presets
      </button>
    </div>
  );
}
