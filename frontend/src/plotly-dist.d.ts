// plotly.js-dist-min ships no types; it re-exports the plotly.js runtime.
declare module "plotly.js-dist-min" {
  const Plotly: typeof import("plotly.js");
  export default Plotly;
}
