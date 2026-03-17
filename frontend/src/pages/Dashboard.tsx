import { useEffect, useState } from "react";
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import {
  fetchSalesSummary, fetchTopProducts,
  fetchAnomalySummary, fetchReplenishmentSummary,
} from "../lib/api";
import type { MonthlySale, TopProduct, AnomalySummaryRow, ReplenishmentSummaryRow } from "../lib/api";

function StatCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</p>
      <p className="text-2xl font-semibold text-white">{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  );
}

export default function Dashboard() {
  const [sales, setSales] = useState<MonthlySale[]>([]);
  const [topProducts, setTopProducts] = useState<TopProduct[]>([]);
  const [anomalySummary, setAnomalySummary] = useState<AnomalySummaryRow[]>([]);
  const [replSummary, setReplSummary] = useState<ReplenishmentSummaryRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchSalesSummary(),
      fetchTopProducts(8),
      fetchAnomalySummary(),
      fetchReplenishmentSummary(),
    ]).then(([s, tp, as, rs]) => {
      setSales([...s.monthly_sales].reverse());
      setTopProducts(tp.top_products);
      setAnomalySummary(as.summary);
      setReplSummary(rs.summary);
      setLoading(false);
    });
  }, []);

  const totalTx = sales.reduce((a, b) => a + b.transactions, 0);
  const highAnomalies = anomalySummary.find((r) => r.severity === "high")?.count ?? 0;
  const criticalItems = replSummary.filter((r) => r.status === "critical").reduce((a, b) => a + b.item_count, 0);
  const reorderItems = replSummary.filter((r) => r.status === "reorder").reduce((a, b) => a + b.item_count, 0);

  const chartSales = sales.map((r) => ({
    month: new Date(r.month).toLocaleDateString("en-AU", { month: "short", year: "2-digit" }),
    transactions: r.transactions,
  }));

  const chartProducts = topProducts.map((p) => ({
    name: p.product_type_name,
    units: p.units_sold,
  }));

  if (loading) {
    return <div className="text-gray-500 text-sm pt-10">Loading dashboard…</div>;
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-white mb-1">Dashboard</h1>
      <p className="text-gray-400 mb-6">Inventory health across all stores.</p>

      {/* Stat cards */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
        <StatCard label="Transactions (12 mo)" value={totalTx.toLocaleString()} sub="H&M dataset" />
        <StatCard label="High Severity Anomalies" value={highAnomalies.toLocaleString()} sub="Loss prevention" />
        <StatCard label="Critical Stock Items" value={criticalItems.toLocaleString()} sub="Stock out risk" />
        <StatCard label="Items at Reorder Point" value={reorderItems.toLocaleString()} sub="Order now" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <p className="text-sm font-medium text-gray-300 mb-4">Monthly Transactions</p>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartSales}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="month" tick={{ fill: "#6b7280", fontSize: 11 }} />
              <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
              <Tooltip
                contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }}
                labelStyle={{ color: "#d1d5db" }}
                itemStyle={{ color: "#818cf8" }}
                formatter={(v) => [(v as number).toLocaleString(), "Transactions"]}
              />
              <Line type="monotone" dataKey="transactions" stroke="#818cf8" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <p className="text-sm font-medium text-gray-300 mb-4">Top Products by Units Sold</p>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartProducts} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" horizontal={false} />
              <XAxis type="number" tick={{ fill: "#6b7280", fontSize: 11 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
              <YAxis type="category" dataKey="name" tick={{ fill: "#9ca3af", fontSize: 11 }} width={90} />
              <Tooltip
                contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }}
                itemStyle={{ color: "#34d399" }}
                formatter={(v) => [(v as number).toLocaleString(), "Units sold"]}
              />
              <Bar dataKey="units" fill="#34d399" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
