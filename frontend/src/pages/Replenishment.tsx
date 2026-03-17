import { useEffect, useState } from "react";
import { fetchReplenishment, fetchReplenishmentSummary } from "../lib/api";
import type { ReplenishmentItem, ReplenishmentSummaryRow } from "../lib/api";

const STATUS_STYLES: Record<string, string> = {
  critical: "bg-red-500/15 text-red-400 border-red-500/30",
  reorder: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
  ok: "bg-green-500/15 text-green-400 border-green-500/30",
};

const STORES = [
  { id: 0, label: "All Stores" },
  { id: 1, label: "Sydney CBD" },
  { id: 2, label: "Melbourne CBD" },
  { id: 3, label: "Brisbane CBD" },
];

export default function Replenishment() {
  const [items, setItems] = useState<ReplenishmentItem[]>([]);
  const [summary, setSummary] = useState<ReplenishmentSummaryRow[]>([]);
  const [storeId, setStoreId] = useState(0);
  const [status, setStatus] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const params = {
      store_id: storeId || undefined,
      status: status !== "all" ? status : undefined,
      limit: 100,
    };
    Promise.all([fetchReplenishment(params), fetchReplenishmentSummary()]).then(([r, s]) => {
      setItems(r.items);
      setSummary(s.summary);
      setLoading(false);
    });
  }, [storeId, status]);

  // Aggregate summary by store for the cards
  const storeCards = STORES.slice(1).map((store) => {
    const rows = summary.filter((r) => r.store_id === store.id);
    const critical = rows.find((r) => r.status === "critical")?.item_count ?? 0;
    const reorder = rows.find((r) => r.status === "reorder")?.item_count ?? 0;
    const units = rows.reduce((a, b) => a + (b.total_units_to_order ?? 0), 0);
    return { ...store, critical, reorder, units };
  });

  return (
    <div>
      <h1 className="text-2xl font-semibold text-white mb-1">Replenishment</h1>
      <p className="text-gray-400 mb-6">Auto-generated purchase orders based on 14-day lead time + 7-day safety buffer.</p>

      {/* Store summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        {storeCards.map((store) => (
          <div key={store.id} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <p className="text-sm font-medium text-gray-300 mb-3">{store.label}</p>
            <div className="flex gap-4">
              <div>
                <p className="text-xs text-red-400 mb-0.5">Critical</p>
                <p className="text-xl font-semibold text-white">{store.critical.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-yellow-400 mb-0.5">Reorder</p>
                <p className="text-xl font-semibold text-white">{store.reorder.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-0.5">Units to order</p>
                <p className="text-xl font-semibold text-white">{store.units.toLocaleString()}</p>
              </div>
            </div>
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
          {["all", "critical", "reorder"].map((s) => (
            <button
              key={s}
              onClick={() => setStatus(s)}
              className={`px-3 py-2 text-sm rounded-lg border transition-colors capitalize ${
                status === s
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
                <th className="text-right px-4 py-3">Days Left</th>
                <th className="text-right px-4 py-3">Suggest Order</th>
                <th className="text-right px-4 py-3">Retail Price</th>
                <th className="text-left px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, i) => (
                <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                  <td className="px-4 py-3 text-gray-200">
                    {item.product_type_name}
                    <span className="text-gray-500 ml-1 text-xs">· {item.colour_group_name}</span>
                  </td>
                  <td className="px-4 py-3 text-gray-400">{item.store_name}</td>
                  <td className="px-4 py-3 text-right text-gray-300">{item.total_stock}</td>
                  <td className={`px-4 py-3 text-right font-mono ${item.days_of_stock_remaining < 14 ? "text-red-400" : "text-gray-300"}`}>
                    {item.days_of_stock_remaining.toFixed(0)}d
                  </td>
                  <td className="px-4 py-3 text-right text-gray-200 font-medium">
                    {item.suggested_order_qty.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-400">
                    ${item.retail_price?.toFixed(2) ?? "—"}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-block px-2 py-0.5 rounded-full text-xs border capitalize ${STATUS_STYLES[item.status]}`}>
                      {item.status}
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
