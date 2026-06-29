// Portfolio source: load the bundled sample or upload a CSV.
import { useRef } from "react";
import type { PortfolioAsset } from "../types";
import { fmtCurrency } from "../format";

interface Props {
  portfolio: PortfolioAsset[];
  source: string;
  onLoadSample: () => void;
  onUpload: (file: File) => void;
  busy: boolean;
}

export function PortfolioPanel({ portfolio, source, onLoadSample, onUpload, busy }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);

  const totalExposure = portfolio.reduce((s, a) => s + a.exposure_at_default, 0);
  const classes = new Set(portfolio.map((a) => a.asset_class));
  const currencies = new Set(portfolio.map((a) => a.currency));

  return (
    <div className="panel">
      <h2>Portfolio</h2>
      <p className="muted">Source: {source || "none loaded"}</p>

      {portfolio.length > 0 && (
        <table style={{ marginBottom: 12 }}>
          <tbody>
            <tr>
              <td style={{ textAlign: "left" }}>Positions</td>
              <td>{portfolio.length}</td>
            </tr>
            <tr>
              <td style={{ textAlign: "left" }}>Total exposure</td>
              <td>{fmtCurrency(totalExposure)}</td>
            </tr>
            <tr>
              <td style={{ textAlign: "left" }}>Asset classes</td>
              <td>{[...classes].join(", ")}</td>
            </tr>
            <tr>
              <td style={{ textAlign: "left" }}>Currencies</td>
              <td>{[...currencies].join(", ")}</td>
            </tr>
          </tbody>
        </table>
      )}

      <button className="secondary" onClick={onLoadSample} disabled={busy}>
        Load sample portfolio
      </button>
      <button onClick={() => fileRef.current?.click()} disabled={busy}>
        Upload CSV
      </button>
      <input
        ref={fileRef}
        type="file"
        accept=".csv"
        style={{ display: "none" }}
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) onUpload(f);
          e.target.value = "";
        }}
      />
    </div>
  );
}
