import { useEffect, useState } from "react";
import { api } from "./api";
import type {
  PortfolioAsset,
  Scenario,
  ScenarioComparison,
  StressResult,
} from "./types";
import { ScenarioBuilder } from "./components/ScenarioBuilder";
import { PortfolioPanel } from "./components/PortfolioPanel";
import { ResultsDashboard } from "./components/ResultsDashboard";
import { ComparisonChart } from "./components/ComparisonChart";

const EMPTY_SCENARIO: Scenario = {
  name: "Custom",
  description: "",
  equity_shock: 0,
  rate_shock_bps: 0,
  fx_shocks: {},
  pd_stress_multiplier: 1,
};

export default function App() {
  const [presets, setPresets] = useState<Scenario[]>([]);
  const [scenario, setScenario] = useState<Scenario>(EMPTY_SCENARIO);
  const [portfolio, setPortfolio] = useState<PortfolioAsset[]>([]);
  const [source, setSource] = useState("");
  const [result, setResult] = useState<StressResult | null>(null);
  const [comparison, setComparison] = useState<ScenarioComparison[] | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  // Bootstrap: load presets + sample portfolio, then run a first scenario.
  useEffect(() => {
    (async () => {
      try {
        const [ps, pf] = await Promise.all([api.scenarios(), api.samplePortfolio()]);
        setPresets(ps);
        setPortfolio(pf);
        setSource("sample portfolio (15 positions)");
        const initial = ps.find((p) => p.name === "Severe Recession") ?? ps[0] ?? EMPTY_SCENARIO;
        setScenario(initial);
        setResult(await api.runStress(initial, pf));
      } catch (e) {
        setError(`Failed to reach backend. Is it running on :8000?\n${(e as Error).message}`);
      }
    })();
  }, []);

  const guard = async (fn: () => Promise<void>) => {
    setBusy(true);
    setError("");
    try {
      await fn();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const runStress = () =>
    guard(async () => {
      if (!portfolio.length) throw new Error("Load a portfolio first.");
      setComparison(null);
      setResult(await api.runStress(scenario, portfolio));
    });

  const compareAll = () =>
    guard(async () => {
      if (!portfolio.length) throw new Error("Load a portfolio first.");
      setComparison(await api.compare(presets, portfolio));
    });

  const loadSample = () =>
    guard(async () => {
      const pf = await api.samplePortfolio();
      setPortfolio(pf);
      setSource("sample portfolio (15 positions)");
      setResult(await api.runStress(scenario, pf));
    });

  const upload = (file: File) =>
    guard(async () => {
      const pf = await api.uploadPortfolio(file);
      setPortfolio(pf);
      setSource(`${file.name} (${pf.length} positions)`);
      setComparison(null);
      setResult(await api.runStress(scenario, pf));
    });

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>Stress Testing Tool</h1>
          <div className="sub">
            Define custom equity / rate / FX shocks and simulate portfolio losses
          </div>
        </div>
        <div className="sub">base currency: USD</div>
      </header>

      {error && <div className="error">{error}</div>}

      <div className="layout">
        <div>
          <PortfolioPanel
            portfolio={portfolio}
            source={source}
            onLoadSample={loadSample}
            onUpload={upload}
            busy={busy}
          />
          <ScenarioBuilder
            presets={presets}
            scenario={scenario}
            onChange={setScenario}
            onRun={runStress}
            onCompareAll={compareAll}
            busy={busy}
          />
        </div>

        <div>
          {comparison ? (
            <ComparisonChart data={comparison} />
          ) : result ? (
            <ResultsDashboard result={result} />
          ) : (
            <div className="panel">
              <p className="muted">Loading…</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
