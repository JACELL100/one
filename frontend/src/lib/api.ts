// Typed client for the one8 FitLab FastAPI backend.

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export type FitBadge = "snug" | "true" | "roomy";
export type GaitProfileKind = "neutral" | "cushion" | "stability";

export interface Measurement {
  length_mm: number;
  width_mm: number;
  confidence: number;
  method: string;
  notes?: string | null;
}

export interface FootScanResponse {
  measurement: Measurement;
  manual_fallback_recommended: boolean;
}

export interface Product {
  id: string;
  name: string;
  tagline: string;
  price_inr: number;
  image_url: string;
  sport: string;
  surface: string;
  cushioning: string;
  support: string;
  width_class: string;
}

export interface Goals {
  sport: "running" | "training" | "lifestyle" | "court";
  surface: "road" | "trail" | "track" | "gym" | "mixed";
  cushioning: "firm" | "balanced" | "plush";
  use_case: "daily" | "race" | "recovery" | "allday";
}

export interface GaitResult {
  gait_profile: GaitProfileKind;
  cadence_spm?: number | null;
  confidence: number;
  descriptor: string;
}

export interface Recommendation {
  product_id: string;
  name: string;
  price_inr: number;
  image_url: string;
  size_label: string;
  fit: FitBadge;
  match_score: number;
  rationale: string;
}

export interface RecommendResponse {
  recommendations: Recommendation[];
  ranker: string;
}

async function jsonOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return (await res.json()) as T;
}

export async function getCatalog(): Promise<Product[]> {
  const res = await fetch(`${API_BASE}/catalog`, { cache: "no-store" });
  const data = await jsonOrThrow<{ products: Product[] }>(res);
  return data.products;
}

export async function scanFoot(file: File): Promise<FootScanResponse> {
  const form = new FormData();
  form.append("image", file);
  const res = await fetch(`${API_BASE}/scan/foot`, {
    method: "POST",
    body: form,
  });
  return jsonOrThrow<FootScanResponse>(res);
}

export async function scanFootManual(
  lengthCm: number,
  widthCm?: number,
): Promise<FootScanResponse> {
  const res = await fetch(`${API_BASE}/scan/foot/manual`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ length_cm: lengthCm, width_cm: widthCm ?? null }),
  });
  return jsonOrThrow<FootScanResponse>(res);
}

export async function recommend(payload: {
  length_mm: number;
  width_mm?: number;
  goals: Goals;
  gait?: GaitResult | null;
  limit?: number;
}): Promise<RecommendResponse> {
  const res = await fetch(`${API_BASE}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return jsonOrThrow<RecommendResponse>(res);
}

export async function scanGait(signals: {
  cadence_spm?: number | null;
  vertical_osc_cm?: number | null;
  pronation_deg?: number | null;
}): Promise<GaitResult> {
  const params = new URLSearchParams();
  if (signals.cadence_spm != null)
    params.set("cadence_spm", String(Math.round(signals.cadence_spm)));
  if (signals.vertical_osc_cm != null)
    params.set("vertical_osc_cm", String(signals.vertical_osc_cm));
  if (signals.pronation_deg != null)
    params.set("pronation_deg", String(signals.pronation_deg));
  const res = await fetch(`${API_BASE}/scan/gait?${params.toString()}`, {
    method: "POST",
  });
  return jsonOrThrow<GaitResult>(res);
}

export interface ScanHistoryItem {
  id: string;
  created_at: string;
  measurement: Measurement;
  goals?: Goals | null;
  gait?: GaitResult | null;
  recommendations: Recommendation[];
}

function authHeaders(token: string): Record<string, string> {
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
}

export async function saveScan(
  token: string,
  payload: {
    measurement: Measurement;
    goals: Goals;
    gait?: GaitResult | null;
    recommendations: Recommendation[];
  },
): Promise<{ id: string }> {
  const res = await fetch(`${API_BASE}/scans`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
  return jsonOrThrow<{ id: string }>(res);
}

export async function listScans(token: string): Promise<ScanHistoryItem[]> {
  const res = await fetch(`${API_BASE}/scans`, {
    headers: authHeaders(token),
    cache: "no-store",
  });
  const data = await jsonOrThrow<{ scans: ScanHistoryItem[] }>(res);
  return data.scans;
}

export async function deleteScan(token: string, id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/scans/${id}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
  if (!res.ok && res.status !== 204) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
}
