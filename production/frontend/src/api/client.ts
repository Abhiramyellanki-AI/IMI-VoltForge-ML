/**
 * IMI API Client — Typed fetch wrappers for all backend endpoints.
 * Base URL is determined by VITE_API_URL env variable (defaults to localhost:8000).
 */

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ─── Types ───────────────────────────────────────────────────────────────────

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  ensemble_loaded: boolean;
  dataset_rows: number;
}

export interface PredictRequest {
  smiles: string;
  processing_temp_c: number;
  crystallinity: number;
}
export interface PredictResponse {
  predicted_eb: number;
  model_used: string;
  smiles: string;
  processing_temp_c: number;
  crystallinity: number;
}

export interface InverseDesignRequest {
  smiles: string;
  target_eb: number;
  max_iter?: number;
}
export interface InverseDesignResponse {
  success: boolean;
  smiles: string;
  target_eb: number;
  optimal_temp_c: number | null;
  optimal_crystallinity: number | null;
  predicted_eb: number | null;
  absolute_error: number | null;
  optimizer_message: string;
  model_used: string;
}

export interface ConditionalSearchRequest {
  target_eb: number;
  polymer_class: string;
  top_k?: number;
}
export interface CandidatePolymer {
  rank: number;
  smiles: string;
  polymer_class: string;
  target_eb_dataset: number;
  eb_delta: number;
  processing_temp_c: number;
  crystallinity: number;
}
export interface ConditionalSearchResponse {
  query_target_eb: number;
  query_polymer_class: string;
  candidates: CandidatePolymer[];
  total_found: number;
}

export interface TelemetryInput {
  smiles: string;
  temperature: number;
  pressure_bar: number;
}
export interface TwinPredictionResponse {
  smiles: string;
  temperature: number;
  pressure_bar: number;
  estimated_crystallinity: number;
  predicted_eb: number;
  good_fit: boolean;
  model_used: string;
}
export interface CorrectionRequest {
  smiles: string;
  current_eb: number;
  desired_eb: number;
  current_temp: number;
  current_cryst: number;
}
export interface CorrectionResponse {
  delta_temp_c: number;
  delta_crystallinity: number;
  recommended_temp_c: number;
  recommended_crystallinity: number;
  projected_eb: number;
  projected_error: number;
}
export interface SimulateResponse {
  simulated: boolean;
  smiles: string;
  temperature: number;
  pressure_bar: number;
  estimated_crystallinity: number;
  predicted_eb: number;
  good_fit: boolean;
}

export interface GenerativeDesignRequest {
  target_eb: number;
  generations?: number;
  pop_size?: number;
}
export interface GenerativeDesignResponse {
  target_eb: number;
  best_smiles: string;
  predicted_eb: number;
  absolute_error: number;
  generations_run: number;
}

// ─── API Functions ────────────────────────────────────────────────────────────

export const api = {
  health: ()                              => apiFetch<HealthResponse>('/health'),
  predict: (body: PredictRequest)        => apiFetch<PredictResponse>('/api/predict', { method: 'POST', body: JSON.stringify(body) }),
  inverseDesign: (body: InverseDesignRequest) => apiFetch<InverseDesignResponse>('/api/inverse-design', { method: 'POST', body: JSON.stringify(body) }),
  conditionalSearch: (body: ConditionalSearchRequest) => apiFetch<ConditionalSearchResponse>('/api/conditional-search', { method: 'POST', body: JSON.stringify(body) }),
  twinPredict: (body: TelemetryInput)    => apiFetch<TwinPredictionResponse>('/api/twin/predict', { method: 'POST', body: JSON.stringify(body) }),
  twinCorrect: (body: CorrectionRequest) => apiFetch<CorrectionResponse>('/api/twin/correct', { method: 'POST', body: JSON.stringify(body) }),
  twinSimulate: ()                       => apiFetch<SimulateResponse>('/api/twin/simulate'),
  generativeDesign: (body: GenerativeDesignRequest) => apiFetch<GenerativeDesignResponse>('/api/generative-design', { method: 'POST', body: JSON.stringify(body) }),
};
