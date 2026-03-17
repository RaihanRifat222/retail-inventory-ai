export default function Dashboard() {
  return (
    <div>
      <h1 className="text-2xl font-semibold text-white mb-1">Dashboard</h1>
      <p className="text-gray-400 mb-8">Overview of inventory health across all stores.</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {[
          { label: "Total SKUs", value: "105,542" },
          { label: "Stores", value: "3" },
          { label: "Transactions", value: "31.7M" },
          { label: "Stock Levels", value: "1.65M" },
        ].map(({ label, value }) => (
          <div key={label} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</p>
            <p className="text-2xl font-semibold text-white">{value}</p>
          </div>
        ))}
      </div>

      <div className="mt-8 bg-gray-900 border border-gray-800 rounded-xl p-6">
        <p className="text-sm text-gray-500">
          Charts coming in Day 8 — Analytics Dashboard.
        </p>
      </div>
    </div>
  );
}
