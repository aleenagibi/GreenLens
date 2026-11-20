import type { Answer } from './types'

export const uid = () => Math.random().toString(36).slice(2) + Date.now().toString(36)

export function modelName(model?: string | null, display?: string | null): string {
  if (display) return display
  if (!model) return 'Unknown model'
  const clean = model.includes('/') ? model.split('/').pop() ?? model : model
  return clean.replace(/:free$/i, '').replace(/[-_]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

export const fmtLatency = (ms: number) => (ms < 1000 ? `${Math.round(ms)} ms` : `${(ms / 1000).toFixed(1)} s`)
export const fmtCarbon = (v: number) => `${v.toFixed(v < 0.01 ? 4 : 2)} g`
export const fmtEnergy = (v: number) => `${v.toFixed(v < 0.01 ? 4 : 2)} Wh`

/** Estimated carbon of the ideal vs the selected model, and what was avoided. */
export function routeCarbon(a: Answer) {
  const ideal = a.comparison.find((c) => c.ideal)?.estimated_carbon_g ?? 0
  const selected = a.comparison.find((c) => c.selected)?.estimated_carbon_g ?? 0
  const saved = Math.max(0, ideal - selected)
  return { ideal, selected, saved, pct: saved > 0 ? Math.round((saved / ideal) * 100) : null }
}

/** Impact scale shared by every colour that carries meaning in the UI. */
export function impact(g: number) {
  if (g < 0.5) return { label: 'Low impact', color: 'var(--lo)' }
  if (g < 2) return { label: 'Moderate impact', color: 'var(--mid)' }
  return { label: 'Higher impact', color: 'var(--hi)' }
}