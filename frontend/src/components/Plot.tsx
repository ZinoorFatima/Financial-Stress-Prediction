// Plotly wrapper preconfigured with the dark dashboard theme.
import createPlotlyComponent from "react-plotly.js/factory";
import Plotly from "plotly.js-dist-min";
import type { Data, Layout } from "plotly.js";

const PlotlyComponent = createPlotlyComponent(Plotly);

const DARK_LAYOUT: Partial<Layout> = {
  paper_bgcolor: "transparent",
  plot_bgcolor: "transparent",
  font: { color: "#e2e8f0", family: "system-ui, sans-serif", size: 12 },
  margin: { l: 60, r: 20, t: 40, b: 50 },
  legend: { orientation: "h", y: -0.2 },
  xaxis: { gridcolor: "#334155", zerolinecolor: "#334155" },
  yaxis: { gridcolor: "#334155", zerolinecolor: "#334155" },
  colorway: ["#38bdf8", "#818cf8", "#f87171", "#34d399", "#fbbf24"],
};

interface Props {
  data: Data[];
  layout?: Partial<Layout>;
  title?: string;
  height?: number;
}

export function Plot({ data, layout, title, height = 300 }: Props) {
  return (
    <PlotlyComponent
      data={data}
      layout={{
        ...DARK_LAYOUT,
        ...layout,
        title: title ? { text: title, font: { size: 14 } } : undefined,
        height,
        autosize: true,
      }}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: "100%" }}
      useResizeHandler
    />
  );
}
