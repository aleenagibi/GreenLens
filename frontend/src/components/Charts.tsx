import { useState } from 'react'

type Point = { label: string; value: number }

const W = 640, H = 230, PAD = { l: 10, r: 10, t: 18, b: 14 }

/** Smoothed area/line chart with hover read-out. Pure SVG, no dependency. */
export function AreaChart({ data, format }: { data: Point[]; format: (v: number) => string }) {
  const [hover, setHover] = useState<number | null>(null)
  if (data.length < 2) return <p className="chart-empty">Needs at least two responses to draw a trend.</p>

  const max = Math.max(...data.map((d) => d.value), 1e-6)
  const step = (W - PAD.l - PAD.r) / (data.length - 1)
  const x = (i: number) => PAD.l + i * step
  const y = (v: number) => PAD.t + (H - PAD.t - PAD.b) * (1 - v / max)

  const line = data.reduce((d, p, i) => {
    if (i === 0) return `M${x(0)} ${y(p.value)}`
    const mx = (x(i - 1) + x(i)) / 2
    return `${d} C${mx} ${y(data[i - 1].value)}, ${mx} ${y(p.value)}, ${x(i)} ${y(p.value)}`
  }, '')
  const area = `${line} L${x(data.length - 1)} ${H - PAD.b} L${x(0)} ${H - PAD.b} Z`

  const onMove = (e: React.PointerEvent<SVGSVGElement>) => {
    const r = e.currentTarget.getBoundingClientRect()
    const px = ((e.clientX - r.left) / r.width) * W
    setHover(Math.max(0, Math.min(data.length - 1, Math.round((px - PAD.l) / step))))
  }

  const h = hover ?? data.length - 1
  return (
    <div className="area-wrap">
      <svg viewBox={`0 0 ${W} ${H}`} onPointerMove={onMove} onPointerLeave={() => setHover(null)} role="img" aria-label="Carbon per response over time">
        <defs>
          <linearGradient id="ag" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#a6d934" stopOpacity="0.45" />
            <stop offset="1" stopColor="#a6d934" stopOpacity="0" />
          </linearGradient>
        </defs>
        {[0.25, 0.5, 0.75, 1].map((f) => (
          <line key={f} x1={PAD.l} x2={W - PAD.r} y1={PAD.t + (H - PAD.t - PAD.b) * f} y2={PAD.t + (H - PAD.t - PAD.b) * f} stroke="#2a312d" strokeDasharray="3 5" />
        ))}
        <path d={area} fill="url(#ag)" className="area-fill" />
        <path d={line} fill="none" stroke="#a6d934" strokeWidth="3" strokeLinecap="round" pathLength={1} className="area-line" />
        <line x1={x(h)} x2={x(h)} y1={PAD.t} y2={H - PAD.b} stroke="#a6d934" strokeOpacity="0.35" />
        <circle cx={x(h)} cy={y(data[h].value)} r="6" fill="#121513" stroke="#d4ff3f" strokeWidth="3" />
      </svg>
      <div className="tip" style={{ left: `${Math.min(88, Math.max(12, (x(h) / W) * 100))}%` }}>
        {format(data[h].value)}<small>{data[h].label}</small>
      </div>
    </div>
  )
}


/** Compact bar chart showing the carbon estimate for each recorded response. */
export function CarbonBarChart({ data, format }: { data: Point[]; format: (v: number) => string }) {
  const [hover, setHover] = useState<number | null>(null)
  if (!data.length) return <p className="chart-empty">No response-level carbon data yet.</p>
  const visible = data.slice(-12)
  const max = Math.max(...visible.map((item) => item.value), 0.000001)
  const W = 640, H = 220, left = 28, right = 12, top = 22, bottom = 42
  const plotH = H - top - bottom
  const slot = (W - left - right) / visible.length
  const barW = Math.min(30, slot * 0.58)
  const active = hover === null ? visible.length - 1 : hover
  return (
    <div className="carbon-bars">
      <div className="carbon-bars-readout">
        <strong>{format(visible[active].value)}</strong>
        <span>{visible[active].label}</span>
      </div>
      <div className="carbon-bars-scroll">
        <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Bar chart of carbon per response">
          {[0, .25, .5, .75, 1].map((fraction) => {
            const y = top + plotH * (1 - fraction)
            return <g key={fraction}><line x1={left} x2={W-right} y1={y} y2={y} className="carbon-bar-grid" /><text x={left-7} y={y+3} textAnchor="end" className="carbon-bar-tick">{(max*fraction).toFixed(3)}</text></g>
          })}
          {visible.map((item, index) => {
            const height = Math.max(2, (item.value / max) * plotH)
            const x = left + slot * index + (slot - barW) / 2
            const y = top + plotH - height
            return <g key={`${item.label}-${index}`} onPointerEnter={() => setHover(index)} onPointerLeave={() => setHover(null)}>
              <rect x={x} y={y} width={barW} height={height} rx="5" className={active === index ? 'carbon-bar active' : 'carbon-bar'} />
              <text x={x+barW/2} y={H-17} textAnchor="middle" className="carbon-bar-label">{item.label.length > 8 ? item.label.slice(0,8) : item.label}</text>
              <rect x={left+slot*index} y={top} width={slot} height={plotH} fill="transparent" />
            </g>
          })}
        </svg>
      </div>
    </div>
  )
}

export const MODEL_COLORS = [
  '#638F78',
  '#8DB49A',
  '#B2C5A9',
  '#C5A879',
  '#7FA6A0',
  '#B58F91',
  '#879BB0',
  '#A99C83',
  '#77958A',
  '#C0B5A4',
]

/** Centred model distribution donut; the expandable legend lives in InsightsPage. */
export function Donut({ data }: { data: Point[] }) {
  const total = data.reduce((sum, item) => sum + item.value, 0)
  if (!total) return <p className="chart-empty">No responses yet.</p>

  const R = 52
  const C = 2 * Math.PI * R
  let accumulated = 0

  return (
    <div className="donut">
      <svg viewBox="0 0 140 140" role="img" aria-label="Share of successful responses by model">
        <g transform="rotate(-90 70 70)">
          <circle cx="70" cy="70" r={R} fill="none" stroke="#E5ECE4" strokeWidth="16" />
          {data.map((item, index) => {
            const length = (item.value / total) * C
            const segment = Math.max(length - 2, 0)
            const circle = (
              <circle
                key={item.label}
                cx="70" cy="70" r={R}
                fill="none"
                stroke={MODEL_COLORS[index % MODEL_COLORS.length]}
                strokeWidth="16"
                strokeDasharray={`${segment} ${C - segment}`}
                strokeDashoffset={-accumulated}
                className="seg"
                style={{ animationDelay: `${index * 80}ms` }}
              />
            )
            accumulated += length
            return circle
          })}
        </g>
        <text x="70" y="68" textAnchor="middle" className="donut-num">{total}</text>
        <text x="70" y="86" textAnchor="middle" className="donut-cap">responses</text>
      </svg>
    </div>
  )
}

type HeatmapCell = {
  model: string
  task_type: string
  count: number
  average_carbon_g: number
  average_latency_ms: number
}

/** Model × task heatmap from persisted successful inference aggregates. */
export function TaskHeatmap({ data }: { data: HeatmapCell[] }) {
  const [metric, setMetric] = useState<'carbon' | 'latency'>('carbon')
  const models = [...new Set(data.map((item) => item.model))]
  const tasks = [...new Set(data.map((item) => item.task_type))]
  const valueFor = (item: HeatmapCell) =>
    metric === 'carbon' ? item.average_carbon_g : item.average_latency_ms
  const max = Math.max(...data.map(valueFor), 0.000001)
  const cells = new Map(data.map((item) => [`${item.model}::${item.task_type}`, item]))

  if (!data.length) return <p className="chart-empty">Not enough recorded model/task data yet.</p>

  return (
    <div className="task-heatmap">
      <div className="heatmap-controls">
        <span>Average per inference</span>
        <div>
          <button className={metric === 'carbon' ? 'active' : ''} onClick={() => setMetric('carbon')}>Carbon</button>
          <button className={metric === 'latency' ? 'active' : ''} onClick={() => setMetric('latency')}>Latency</button>
        </div>
      </div>
      <div className="heatmap-scroll">
        <div className="heatmap-grid" style={{ gridTemplateColumns: `minmax(120px, 1.2fr) repeat(${tasks.length}, minmax(76px, 1fr))` }}>
          <span className="heatmap-corner">MODEL / TASK</span>
          {tasks.map((task) => <span className="heatmap-task" key={task}>{task.replaceAll('_', ' ')}</span>)}
          {models.map((model) => (
            <div className="heatmap-row" key={model} style={{ display: 'contents' }}>
              <span className="heatmap-model" title={model}>{model.split('/').pop()}</span>
              {tasks.map((task) => {
                const item = cells.get(`${model}::${task}`)
                if (!item) return <span className="heatmap-cell missing" key={task} title="No recorded inference" />
                const value = valueFor(item)
                const intensity = Math.max(0.12, value / max)
                const readableText = intensity >= 0.58 ? '#14200a' : '#f1f5ef'
                return (
                  <span
                    key={task}
                    className="heatmap-cell"
                    style={{ background: `rgba(166, 217, 52, ${0.12 + intensity * 0.72})`, color: readableText }}
                    title={`${model} · ${task} · ${metric === 'carbon' ? `${value.toFixed(5)} g CO₂e` : `${value.toFixed(0)} ms`} average · ${item.count} runs`}
                  >
                    <b>{metric === 'carbon' ? value.toFixed(3) : value.toFixed(0)}</b>
                    <small>{item.count} runs</small>
                  </span>
                )
              })}
            </div>
          ))}
        </div>
      </div>
      <p className="heatmap-note">Hover over a cell to see its exact average and sample count. Brighter cells indicate higher values. Missing cells have no recorded observations.</p>
    </div>
  )
}

/** Carbon comparison across comparable, successful routing decisions. */
export function CarbonWaterfall({
  data,
}: {
  data: {
    ideal_carbon_g: number
    selected_carbon_g: number
    savings_carbon_g: number
    comparable_requests: number
  }
}) {
  const { ideal_carbon_g: ideal, selected_carbon_g: selected, savings_carbon_g: savings, comparable_requests: count } = data
  if (!count) return <p className="chart-empty">No comparable ideal/selected carbon estimates have been recorded yet.</p>

  const max = Math.max(ideal, selected, 0.000001)
  const width = 100
  const idealWidth = Math.max(0, ideal / max * width)
  const selectedWidth = Math.max(0, selected / max * width)
  const savedPercent = ideal > 0 ? (savings / ideal) * 100 : 0
  const positive = savings >= 0

  return (
    <div className="carbon-waterfall">
      <div className="waterfall-summary">
        <div>
          <span>{positive ? 'Estimated carbon avoided' : 'Additional carbon emitted'}</span>
          <strong className={positive ? 'saving-positive' : 'saving-negative'}>
            {Math.abs(savings).toFixed(5)} <small>g CO₂e</small>
          </strong>
        </div>
        <span className={`waterfall-percent ${positive ? 'saving-positive' : 'saving-negative'}`}>
          {savedPercent > 0 ? '+' : ''}{savedPercent.toFixed(1)}%
        </span>
      </div>

      <div className="waterfall-bars">
        <div className="waterfall-row">
          <div className="waterfall-label"><span>Ideal model</span><b>{ideal.toFixed(5)} g</b></div>
          <div className="waterfall-track"><i className="waterfall-ideal" style={{ width: `${idealWidth}%` }} /></div>
        </div>
        <div className="waterfall-connector"><span>↓ {positive ? 'Carbon reduction' : 'Carbon increase'}</span></div>
        <div className="waterfall-row">
          <div className="waterfall-label"><span>Selected model</span><b>{selected.toFixed(5)} g</b></div>
          <div className="waterfall-track"><i className="waterfall-selected" style={{ width: `${selectedWidth}%` }} /></div>
        </div>
      </div>
      <div className="waterfall-footer">
        <span>{count} comparable successful routes</span>
        <span>Aggregated estimates</span>
      </div>
    </div>
  )
}



type ModelPerformance = {
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
}

/** Historical performance radar based on models that actually answered prompts. */
export function ModelRadar({ data }: { data: ModelPerformance[] }) {
  const [selectedModel, setSelectedModel] = useState(data[0]?.model ?? '')
  const selected = data.find((item) => item.model === selectedModel) ?? data[0]

  if (!data.length) {
    return (
      <div className="radar-empty">
        <strong>No completed model inferences are available yet.</strong>
        <span>Models will appear after they successfully answer prompts and their inference metrics are recorded.</span>
      </div>
    )
  }

  const axes = [
    { key: 'reliability_score' as const, label: 'Reliability' },
    { key: 'carbon_efficiency_score' as const, label: 'Carbon efficiency' },
    { key: 'energy_efficiency_score' as const, label: 'Energy efficiency' },
    { key: 'latency_performance_score' as const, label: 'Latency performance' },
  ]
  const cx = 190
  const cy = 155
  const radius = 108
  const angle = (index: number) => -Math.PI / 2 + (Math.PI * 2 * index) / axes.length
  const point = (index: number, value: number) => ({
    x: cx + Math.cos(angle(index)) * radius * (Math.max(0, Math.min(10, value)) / 10),
    y: cy + Math.sin(angle(index)) * radius * (Math.max(0, Math.min(10, value)) / 10),
  })
  const complete = axes.every((axis) => selected?.[axis.key] !== null && selected?.[axis.key] !== undefined)
  const polygon = complete
    ? axes.map((axis, index) => {
        const p = point(index, selected?.[axis.key] as number)
        return `${p.x},${p.y}`
      }).join(' ')
    : ''

  return (
    <div className="model-radar">
      <div className="radar-controls">
        <label htmlFor="radar-model-select">Compare model</label>
        <select
          id="radar-model-select"
          value={selected?.model ?? ''}
          onChange={(event) => setSelectedModel(event.target.value)}
        >
          {data.map((item) => (
            <option key={item.model} value={item.model}>{item.model}</option>
          ))}
        </select>
      </div>

      <div className="radar-content">
        <svg viewBox="-95 0 570 315" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Historical inference performance radar chart">
          {[2, 4, 6, 8, 10].map((level) => {
            const points = axes.map((_, index) => {
              const p = point(index, level)
              return `${p.x},${p.y}`
            }).join(' ')
            return <polygon key={level} points={points} className="radar-grid" />
          })}
          {axes.map((axis, index) => {
            const end = point(index, 10)
            return (
              <g key={axis.key}>
                <line x1={cx} y1={cy} x2={end.x} y2={end.y} className="radar-axis" />
                <text
                  x={cx + Math.cos(angle(index)) * 145}
                  y={cy + Math.sin(angle(index)) * 145}
                  className="radar-axis-label"
                  textAnchor={index === 1 ? 'start' : index === 3 ? 'end' : 'middle'}
                  dominantBaseline="middle"
                >
                  {axis.label}
                </text>
              </g>
            )
          })}
          {complete && <polygon points={polygon} className="radar-shape" />}
          {axes.map((axis, index) => {
            const value = selected?.[axis.key]
            if (value === null || value === undefined) return null
            const p = point(index, value)
            return <circle key={axis.key} cx={p.x} cy={p.y} r="5" className="radar-point" />
          })}
          <text x={cx} y={cy + 4} textAnchor="middle" className="radar-center-label">0–10</text>
        </svg>

        <div className="radar-values">
          {axes.map((axis) => {
            const value = selected?.[axis.key]
            return (
              <div className="radar-value-row" key={axis.key}>
                <span>{axis.label}</span>
                <strong>{value == null ? 'Unavailable' : `${value.toFixed(2)} / 10`}</strong>
                <small>
                  {axis.key === 'reliability_score'
                    ? `${selected?.successful_responses} successful / ${selected?.attempts} attempts`
                    : `${selected?.successful_responses} successful responses`}
                </small>
              </div>
            )
          })}
        </div>
      </div>

      <div className="radar-observed-metrics">
        <span>Avg. carbon <b>{selected.average_carbon_g == null ? '—' : `${selected.average_carbon_g.toFixed(5)} g CO₂e`}</b></span>
        <span>Avg. energy <b>{selected.average_energy_wh == null ? '—' : `${selected.average_energy_wh.toFixed(5)} Wh`}</b></span>
        <span>Avg. latency <b>{selected.average_latency_ms == null ? '—' : `${selected.average_latency_ms.toFixed(0)} ms`}</b></span>
      </div>

      <p className="radar-note">
        Based on actual persisted inference records for models that answered prompts. Scores are relative to the best observed model in this dataset (10 = best); lower average carbon, energy and latency produce higher efficiency scores. Reliability is the success rate. These are historical comparisons, not absolute benchmark scores.
      </p>
    </div>
  )
}
