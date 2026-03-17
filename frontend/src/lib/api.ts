const BASE = "/api";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json();
}

// --- Sales ---
export interface MonthlySale {
  month: string;
  transactions: number;
  total_revenue: number;
}
export const fetchSalesSummary = () =>
  get<{ monthly_sales: MonthlySale[] }>("/sales/summary");

export interface TopProduct {
  article_id: string;
  product_type_name: string;
  colour_group_name: string;
  units_sold: number;
}
export const fetchTopProducts = (limit = 10) =>
  get<{ top_products: TopProduct[] }>(`/sales/top-products?limit=${limit}`);

// --- Anomalies ---
export interface Anomaly {
  article_id: string;
  product_type_name: string;
  product_group_name: string;
  colour_group_name: string;
  store_name: string;
  store_id: number;
  total_stock: number;
  expected_stock: number;
  stock_delta: number;
  delta_pct: number;
  anomaly_score: number;
  severity: "high" | "medium" | "low";
  predicted_at: string;
}
export const fetchAnomalies = (params?: { store_id?: number; severity?: string; limit?: number }) => {
  const q = new URLSearchParams();
  if (params?.store_id) q.set("store_id", String(params.store_id));
  if (params?.severity) q.set("severity", params.severity);
  if (params?.limit) q.set("limit", String(params.limit));
  return get<{ total: number; anomalies: Anomaly[] }>(`/anomalies/?${q}`);
};

export interface AnomalySummaryRow {
  severity: string;
  count: number;
  avg_delta: number;
  avg_delta_pct: number;
}
export const fetchAnomalySummary = () =>
  get<{ summary: AnomalySummaryRow[] }>("/anomalies/summary");

// --- Replenishment ---
export interface ReplenishmentItem {
  article_id: string;
  product_type_name: string;
  product_group_name: string;
  colour_group_name: string;
  retail_price: number;
  store_name: string;
  store_id: number;
  total_stock: number;
  avg_daily_velocity: number;
  days_of_stock_remaining: number;
  reorder_point: number;
  suggested_order_qty: number;
  status: "critical" | "reorder" | "ok";
}
export const fetchReplenishment = (params?: { store_id?: number; status?: string; limit?: number }) => {
  const q = new URLSearchParams();
  if (params?.store_id) q.set("store_id", String(params.store_id));
  if (params?.status) q.set("status", params.status);
  if (params?.limit) q.set("limit", String(params.limit));
  return get<{ total: number; items: ReplenishmentItem[] }>(`/replenishment/?${q}`);
};

export interface ReplenishmentSummaryRow {
  store_name: string;
  store_id: number;
  status: string;
  item_count: number;
  total_units_to_order: number;
  avg_days_remaining: number;
}
export const fetchReplenishmentSummary = () =>
  get<{ summary: ReplenishmentSummaryRow[] }>("/replenishment/summary");

// --- NL Query ---
export interface QueryResult {
  question: string;
  sql: string;
  columns: string[];
  rows: Record<string, unknown>[];
  error?: string;
}
export const runNLQuery = (question: string) =>
  post<QueryResult>("/query/", { question });
