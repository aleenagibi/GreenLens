export type Candidate = {
  rank: number
  model: string
  display_name?: string | null
  provider?: string | null
  is_free: boolean
  fit_score: number
  capability_score?: number | null
  capability_source?: string
  carbon_score?: number | null
  latency_score?: number | null
  complexity_score?: number | null
  estimated_energy_wh?: number | null
  estimated_carbon_g?: number | null
  carbon_source?: string | null
  carbon_available?: boolean
  capability_available?: boolean
  selected?: boolean
  ideal?: boolean
}

export type ModelCatalogModel = {
  model_id: string
  display_name?: string | null
  provider?: string | null
  context_length?: number | null
  is_free: boolean
  prompt_price?: number | null
  completion_price?: number | null
  input_modalities: string[]
  output_modalities: string[]
  supports_reasoning: boolean
}

export type RegisteredProvider = {
  name: string
  display_name: string
  default_model: string
  capabilities: Record<string, number>
  supports_streaming: boolean
  supports_vision: boolean
}

export type ModelCatalog = {
  source: string
  retrieved_at: string
  model_count: number
  models: ModelCatalogModel[]
  providers: RegisteredProvider[]
}

export type InsightsData = {
  total_requests: number
  successful_requests: number
  total_energy_wh: number
  total_carbon_g: number
  total_water_l: number | null
  water_estimated_requests: number
  avoided_carbon_g: number
  average_latency_ms: number
  free_model_requests: number
  comparable_routing_requests: number
  model_usage: { model: string; count: number }[]
  model_performance: {
    model: string
    attempts: number
    successful_responses: number
    reliability_score: number | null
    carbon_efficiency_score: number | null
    energy_efficiency_score: number | null
    latency_performance_score: number | null
    average_carbon_g: number | null
    average_energy_wh: number | null
    average_latency_ms: number | null
  }[]
  task_model_heatmap: {
    model: string
    task_type: string
    count: number
    average_carbon_g: number
    average_latency_ms: number
  }[]
  carbon_waterfall: {
    ideal_carbon_g: number
    selected_carbon_g: number
    savings_carbon_g: number
    comparable_requests: number
  }
  carbon_series: { label: string; value: number; created_at: string | null }[]
  recent_decisions: {
    id: number
    prompt: string
    provider: string
    actual_model: string
    ideal_model?: string | null
    capability_gap?: number | null
    ideal_estimated_carbon_g?: number | null
    selected_estimated_carbon_g?: number | null
    fallback_used: boolean
    selected_is_free?: boolean | null
    preset: string
    task_type: string
    fit_score: number
    latency_ms: number
    energy_wh: number
    carbon_g: number
    water_l?: number | null
    sustainability_source?: string | null
    created_at: string | null
  }[]
}

export type BackendRoutingDetails = {
  provider: string
  usage: { prompt_tokens: number; completion_tokens: number; total_tokens: number }
  benchmark: {
    latency_ms: number
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
    provider: string
    model: string
    success: boolean
  }
  sustainability: { energy_wh: number; carbon_g: number; green_score: number; water_l?: number | null; source?: string }
  routing: {
    ideal_model: string
    ideal_display_name?: string | null
    ideal_is_free: boolean
    selected_model: string
    selected_display_name?: string | null
    selected_is_free: boolean
    capability_gap?: number | null
    fit_score: number
    used_free_alternative: boolean
    reason: string
    summary: string
    comparison: Candidate[]
    preset: string
    ideal_estimated_carbon_g?: number | null
    selected_estimated_carbon_g?: number | null
    carbon_savings_g?: number | null
    carbon_savings_percent?: number | null
    selection_basis?: string | null
    candidate_count?: number | null
  }
  pipeline: {
    task?: {
      task_type?: string
      complexity?: { level: string; score: number; factors: string[] }
      embedding_dimensions?: number
    }
    selection?: Record<string, unknown>
    explanation?: { summary?: string }
  }
  inference?: {
    selected_model: string
    actual_model: string
    fallback_used: boolean
    fallback_reason?: string | null
    attempts: { model: string; success: boolean; error?: string }[]
  } | null
  context?: {
    context_window_tokens: number
    context_budget_tokens: number
    input_tokens_estimated: number
    input_tokens_actual?: number | null
    history_messages_received: number
    history_messages_included: number
    history_messages_dropped: number
    context_trimmed: boolean
    context_metadata_available: boolean
  } | null
}

/** Compact, storable version of one backend response. */
export type Answer = {
  content: string
  model: string // model that actually answered
  taskType: string
  latencyMs: number
  carbonG: number
  energyWh: number
  waterL?: number | null
  sustainabilitySource?: string
  fitScore: number
  idealModel: string
  selectedModel: string
  idealIsFree: boolean
  selectedIsFree: boolean
  reason: string
  comparison: Candidate[]
  context?: BackendRoutingDetails['context']
  routingDetails?: BackendRoutingDetails
}

export type Turn = {
  id: string
  prompt: string
  ts: string
  answer?: Answer
  error?: string
  pending?: boolean
}

export type Chat = {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  turns: Turn[]
}

export type Page = 'chat' | 'insights' | 'how'
