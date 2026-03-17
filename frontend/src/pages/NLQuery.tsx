import { useState } from "react";
import { runNLQuery } from "../lib/api";
import type { QueryResult } from "../lib/api";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Send } from "lucide-react";

const EXAMPLE_QUESTIONS = [
  "What are the top 5 product types by number of transactions?",
  "How many transactions were there per month in 2019?",
  "Which store has the most critical stock items?",
  "What is the average stock level per product group?",
];

function isChartable(result: QueryResult) {
  if (result.columns.length !== 2) return false;
  const vals = result.rows.slice(0, 3).map((r) => r[result.columns[1]]);
  return vals.every((v) => typeof v === "number");
}

export default function NLQuery() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(q?: string) {
    const query = q ?? question;
    if (!query.trim()) return;
    if (q) setQuestion(q);
    setLoading(true);
    setResult(null);
    const res = await runNLQuery(query);
    setResult(res);
    setLoading(false);
  }

  const showChart = result && !result.error && isChartable(result);

  return (
    <div>
      <h1 className="text-2xl font-semibold text-white mb-1">Ask a Question</h1>
      <p className="text-gray-400 mb-6">
        Natural language queries powered by Claude — converted to SQL and run live against the database.
      </p>

      {/* Input */}
      <div className="flex gap-3 mb-4">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          placeholder="e.g. What are the top 10 selling products this year?"
          className="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-gray-100 placeholder-gray-600 text-sm focus:outline-none focus:border-brand-500 transition-colors"
        />
        <button
          onClick={() => handleSubmit()}
          disabled={loading || !question.trim()}
          className="bg-brand-500 hover:bg-brand-600 disabled:opacity-40 text-white px-5 py-3 rounded-xl text-sm font-medium flex items-center gap-2 transition-colors"
        >
          <Send size={15} />
          {loading ? "Thinking…" : "Ask"}
        </button>
      </div>

      {/* Example questions */}
      <div className="flex flex-wrap gap-2 mb-8">
        {EXAMPLE_QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => handleSubmit(q)}
            className="text-xs text-gray-400 border border-gray-700 rounded-full px-3 py-1.5 hover:text-gray-200 hover:border-gray-600 transition-colors"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Result */}
      {result && (
        <div className="space-y-4">
          {/* Generated SQL */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">Generated SQL</p>
            <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap">{result.sql}</pre>
          </div>

          {result.error ? (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400 text-sm">
              {result.error}
            </div>
          ) : (
            <>
              {/* Chart (if 2-column numeric result) */}
              {showChart && (
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                  <p className="text-sm font-medium text-gray-300 mb-4">{result.question}</p>
                  <ResponsiveContainer width="100%" height={240}>
                    <BarChart data={result.rows as Record<string, number>[]}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey={result.columns[0]} tick={{ fill: "#9ca3af", fontSize: 11 }} />
                      <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} />
                      <Tooltip
                        contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }}
                        itemStyle={{ color: "#818cf8" }}
                      />
                      <Bar dataKey={result.columns[1]} fill="#818cf8" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Table */}
              <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
                <p className="text-xs text-gray-500 uppercase tracking-wide px-4 py-3 border-b border-gray-800">
                  {result.rows.length} row{result.rows.length !== 1 ? "s" : ""}
                </p>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-800">
                        {result.columns.map((col) => (
                          <th key={col} className="text-left px-4 py-2 text-xs text-gray-500 uppercase tracking-wide">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {result.rows.map((row, i) => (
                        <tr key={i} className="border-b border-gray-800/40 hover:bg-gray-800/20">
                          {result.columns.map((col) => (
                            <td key={col} className="px-4 py-2.5 text-gray-300 font-mono text-xs">
                              {String(row[col] ?? "—")}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
