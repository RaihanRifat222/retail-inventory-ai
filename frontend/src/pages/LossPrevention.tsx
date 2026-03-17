import { useEffect, useState } from "react";
import { fetchAnomalies, fetchAnomalySummary } from "../lib/api";
import type { Anomaly, AnomalySummaryRow } from "../lib/api";

const SEVERITY_STYLES: Record<string, string> = {
  high: "bg-red-500/15 text-red-400 border-red-500/30",
  medium: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
  low: "bg-blue-500/15 text-blue-400 border-blue-500/30",
};

const STORES = [
  { id: 0, label: "All Stores" },
  { id: 1, label: "Sydney CBD" },
  { id: 2, label: "Melbourne CBD" },
  { id: 3, label: "Brisbane CBD" },
];

const SEVERITIES = ["all", "high", "medium", "low"];

export default function LossPrevention() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [summary, setSummary] = useState<AnomalySummaryRow[]>([]);
  const [storeId, setStoreId] = useState(0);
  const [severity, setSeverity] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const params = {
      store_id: storeId || undefined,
      severity: severity !== "all" ? severity : undefined,
      limit: 100,
    };
    Promise.all([fetchAnomalies(params), fetchAnomalySummary()]).then(([a, s]) => {
      setAnomalies(a.anomalies);
      setSummary(s.summary);
      setLoading(false);
    });
  }, [storeId, severity]);

  return (
    <div>
      <h1 className="text-2xl font-semibold text-white mb-1">Loss Prevention</h1>
      <p className="text-gray-400 mb-6">Isolation Forest anomaly detection on stock deltas.</p>

      {/* Summary cards */}
      <div className="flex gap-4 mb-6 flex-wrap">
        {summary.map((row) => (
          <div key={row.severity} className={`border rounded-xl px-5 py-4 ${SEVERITY_STYLES[row.severity]}`}>
            <p className="text-xs uppercase tracking-wide mb-1 capitalize">{row.severity} severity</p>
            <p className="text-2xl font-semibold">{row.count.toLocaleString()}</p>
            <p className="text-xs mt-0.5">avg delta {row.avg_delta_pct.toFixed(1)}%</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-5 flex-wrap">
        <select
          value={storeId}
          onChange={(e) => setStoreId(Number(e.target.value))}
          className="bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg px-3 py-2"
        >
          {STORES.map((s) => (
            <option key={s.id} value={s.id}>{s.label}</option>
          ))}
        </select>

        <div className="flex gap-1">
          {SEVERITIES.map((s) => (
            <button
              key={s}
              onClick={() => setSeverity(s)}
              className={`px-3 py-2 text-sm rounded-lg border transition-colors capitalize ${
                severity === s
                  ? "bg-brand-500/20 border-brand-500/50 text-brand-500"
                  : "border-gray-700 text-gray-400 hover:text-gray-200 hover:border-gray-600"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        {loading ? (
          <p className="text-gray-500 text-sm p-6">Loading…</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-gray-500 text-xs uppercase tracking-wide">
                <th className="text-left px-4 py-3">Product</th>
                <th className="text-left px-4 py-3">Store</th>
                <th className="text-right px-4 py-3">Stock</th>
                <th className="text-right px-4 py-3">Expected</th>
                <th className="text-right px-4 py-3">Delta %</th>
                <th className="text-left px-4 py-3">Severity</th>
              </tr>
            </thead>
            <tbody>
              {anomalies.map((a, i) => (
                <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                  <td className="px-4 py-3 text-gray-200">
                    {a.product_type_name}
                    <span className="text-gray-500 ml-1 text-xs">· {a.colour_group_name}</span>
                  </td>
                  <td className="px-4 py-3 text-gray-400">{a.store_name}</td>
                  <td className="px-4 py-3 text-right text-gray-300">{a.total_stock}</td>
                  <td className="px-4 py-3 text-right text-gray-400">{a.expected_stock}</td>
                  <td className={`px-4 py-3 text-right font-mono ${a.stock_delta < 0 ? "text-red-400" : "text-gray-300"}`}>
                    {a.delta_pct.toFixed(1)}%
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-block px-2 py-0.5 rounded-full text-xs border capitalize ${SEVERITY_STYLES[a.severity]}`}>
                      {a.severity}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
