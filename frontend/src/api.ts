// Thin API client. Uses relative /api URLs proxied to FastAPI in dev.
import type {
  PortfolioAsset,
  Scenario,
  ScenarioComparison,
  StressResult,
} from "./types";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail: unknown;
    try {
      detail = (await res.json()).detail;
    } catch {
      detail = res.statusText;
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return res.json() as Promise<T>;
}

export const api = {
  scenarios: () => fetch("/api/scenarios").then((r) => handle<Scenario[]>(r)),

  samplePortfolio: () =>
    fetch("/api/portfolio/sample").then((r) => handle<PortfolioAsset[]>(r)),

  uploadPortfolio: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return fetch("/api/portfolio/upload", { method: "POST", body: form }).then((r) =>
      handle<PortfolioAsset[]>(r),
    );
  },

  runStress: (scenario: Scenario, portfolio: PortfolioAsset[]) =>
    fetch("/api/stress/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario, portfolio }),
    }).then((r) => handle<StressResult>(r)),

  compare: (scenarios: Scenario[], portfolio: PortfolioAsset[]) =>
    fetch("/api/stress/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenarios, portfolio }),
    }).then((r) => handle<ScenarioComparison[]>(r)),
};
