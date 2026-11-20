import { useState } from 'react'
import type { Candidate } from '../types'
import { fmtCarbon, impact, modelName } from '../utils'

const W = 360, H = 250, P = { l: 36, r: 14, t: 14, b: 36 }, INSET = 10

/** Every candidate model plotted as carbon (x, log scale) vs task fit (y). Top-left is best. */
export default function ModelMap({ cands, sample = false }: { cands: Candidate[]; sample?: boolean }) {
  const [hi, setHi] = useState<number | null>(null)
  const pts = cands.filter((c) => c.estimated_carbon_g != null)
  if (pts.length < 2) return <p className="map-empty">Not enough carbon data to plot these models.</p>

  const lx = (c: number) => Math.log10(Math.max(c, 1e-4))
  const xs = pts.map((p) => lx(p.estimated_carbon_g!))
  const fs = pts.map((p) => p.fit_score)
  const [x0, x1] = [Math.min(...xs), Math.max(...xs)]
  const [f0, f1] = [Math.min(...fs), Math.max(...fs)]
  const sx = (c: number) => P.l + INSET + ((lx(c) - x0) / (x1 - x0 || 1)) * (W - P.l - P.r - INSET * 2)
  const sy = (f: number) => H - P.b - INSET - ((f - f0) / (f1 - f0 || 1)) * (H - P.t - P.b - INSET * 2)

  // frontier: cheapest-first, keep a point only if it beats the fit of everything cheaper
  const frontier: Candidate[] = []
  let best = -Infinity
  for (const p of [...pts].sort((a, b) => a.estimated_carbon_g! - b.estimated_carbon_g!)) {
    if (p.fit_score > best) { frontier.push(p); best = p.fit_score }
  }
  const path = frontier.map((p, i) => `${i ? 'L' : 'M'}${sx(p.estimated_carbon_g!)} ${sy(p.fit_score)}`).join(' ')

  const ideal = pts.find((p) => p.ideal)
  const sel = pts.find((p) => p.selected)
  const shown = hi != null ? pts[hi] : sel ?? ideal

  return (
    <div className="map">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Candidate models by estimated carbon and task fit">
        <rect x={P.l} y={P.t} width={(W - P.l - P.r) * 0.45} height={(H - P.t - P.b) * 0.45} className="map-zone" />
        <text x={P.l + 8} y={P.t + 16} className="map-note">low carbon, high fit</text>
        <line x1={P.l} y1={H - P.b} x2={W - P.r} y2={H - P.b} className="map-axis" />
        <line x1={P.l} y1={P.t} x2={P.l} y2={H - P.b} className="map-axis" />
        <text x={(W + P.l) / 2} y={H - 8} textAnchor="middle" className="map-label">estimated carbon (log scale) →</text>
        <text transform={`translate(11 ${(H - P.b + P.t) / 2}) rotate(-90)`} textAnchor="middle" className="map-label">task fit →</text>

        <path d={path} className="map-frontier" pathLength={1} />
        {ideal && sel && ideal !== sel && (
          <line x1={sx(ideal.estimated_carbon_g!)} y1={sy(ideal.fit_score)} x2={sx(sel.estimated_carbon_g!)} y2={sy(sel.fit_score)} className="map-link" />
        )}
        {pts.map((p, i) => {
          const cx = sx(p.estimated_carbon_g!), cy = sy(p.fit_score)
          const col = impact(p.estimated_carbon_g!).color
          return (
            <g key={`${p.rank}-${p.model}`} className="map-dot" style={{ animationDelay: `${i * 35}ms` }}
              onPointerEnter={() => setHi(i)} onPointerLeave={() => setHi(null)}>
              {p.ideal && <circle cx={cx} cy={cy} r="11" className="map-ideal" />}
              <circle cx={cx} cy={cy} r={p.selected ? 7 : 4.5} style={{ fill: p.selected ? col : undefined }} className={p.selected ? 'dot-sel' : 'dot'} />
              <title>{modelName(p.model, p.display_name)}: fit {p.fit_score.toFixed(1)}, {fmtCarbon(p.estimated_carbon_g!)}</title>
            </g>
          )
        })}
      </svg>

      <div className="map-legend">
        <span><i className="lg sel" /> Selected</span>
        <span><i className="lg ideal" /> Ideal</span>
        <span><i className="lg front" /> Best fit per carbon</span>
      </div>
      {shown && !sample && (
        <p className="map-read"><strong>{modelName(shown.model, shown.display_name)}</strong> · fit {shown.fit_score.toFixed(1)} · {fmtCarbon(shown.estimated_carbon_g!)}</p>
      )}
      {sample && <p className="fine">Sample landscape. Send a message to see the models considered for your task.</p>}
    </div>
  )
}