import { useEffect, useState } from 'react'
import { fetchInsights } from '../api'
import type { InsightsData, ModelCatalog } from '../types'
import { fmtCarbon, fmtEnergy, fmtLatency, modelName } from '../utils'
import { Tile } from '../components/Inspector'
import { CarbonBarChart, Donut, ModelRadar, MODEL_COLORS } from '../components/Charts'

type Props = { catalog: ModelCatalog | null }

const insightsLedEquivalent = (energyWh: number) => {
  const minutes = (energyWh / 10) * 60
  if (!Number.isFinite(minutes) || minutes < 0) return 'LED equivalent unavailable'
  if (minutes < 1) return `About ${(minutes * 60).toFixed(1)} seconds of a 10 W LED bulb`
  if (minutes < 60) return `About ${minutes.toFixed(1)} minutes of a 10 W LED bulb`
  return `About ${(minutes / 60).toFixed(2)} hours of a 10 W LED bulb`
}


export default function InsightsPage({ catalog }: Props) {
  const [stats, setStats] = useState<InsightsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCarbonDetails, setShowCarbonDetails] = useState(false)
  const [showModelDetails, setShowModelDetails] = useState(false)

  useEffect(() => {
    let active = true
    setLoading(true)
    fetchInsights()
      .then((data) => { if (active) { setStats(data); setError(null) } })
      .catch((err) => { if (active) setError(err instanceof Error ? err.message : 'Could not load Insights.') })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [])

  if (loading) {
  return (
    <section className="page-scroll insights-loading">
      <div className="insights-brand-loader">
        <div className="insights-loader-logo">
          <img src="/logo.png" alt="GreenLens" />
        </div>

        <h2>Green<span>Lens</span></h2>

        <p className="insights-loader-tagline">
          SUSTAINABLE AI, INTELLIGENTLY ROUTED
        </p>

        <div className="insights-loader-progress">
          <span />
        </div>

        <small>Retrieving your sustainability insights...</small>
      </div>
    </section>
  )
}

  if (error) {
    return <section className="page-scroll"><div className="card empty-card"><h2>Insights unavailable</h2><p>{error}</p><p className="fine">Check that the GreenLens backend is running and the /stats endpoint is reachable.</p></div></section>
  }

  if (!stats || stats.total_requests === 0) {
    return <section className="page-scroll"><div className="card empty-card"><h2>No inference data yet</h2><p>Successful requests recorded by the GreenLens backend will appear here.</p></div></section>
  }

  const modelNames = new Map((catalog?.models ?? []).map((model) => [model.model_id, model.display_name || model.model_id]))
  const modelUsage = stats.model_usage.map((item) => ({
    label: modelName(item.model, modelNames.get(item.model)),
    value: item.count,
  }))
  const series = stats.carbon_series.map((item) => ({ label: item.label, value: item.value }))
  const decisionsByDate = stats.recent_decisions.reduce((groups, decision) => {
    const date = decision.created_at ? new Date(decision.created_at) : null
    const key = !date || Number.isNaN(date.getTime()) ? 'unknown' : `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
    const existing = groups.get(key)
    if (existing) existing.push(decision)
    else groups.set(key, [decision])
    return groups
  }, new Map<string, typeof stats.recent_decisions>())
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  const dateGroups = Array.from(decisionsByDate.entries()).map(([key, decisions]) => {
    const date = key === 'unknown' || !decisions[0].created_at ? null : new Date(decisions[0].created_at)
    const day = date ? new Date(date.getFullYear(), date.getMonth(), date.getDate()) : null
    const label = !day ? 'Date unavailable'
      : day.getTime() === today.getTime() ? 'Today'
      : day.getTime() === yesterday.getTime() ? 'Yesterday'
      : day.toLocaleDateString(undefined, { day: 'numeric', month: 'long', year: 'numeric' })
    return { key, label, decisions }
  })

  return (
    <section className="page-scroll">
      <div className="tiles four">
        <Tile delay={0} label="Requests" value={String(stats.total_requests)} unit="" note={`${stats.successful_requests} Successful `} />
        <Tile delay={60} label="Energy" value={fmtEnergy(stats.total_energy_wh).split(' ')[0]} unit="Wh" note="Estimate" />
        <Tile delay={120} label="Carbon" value={fmtCarbon(stats.total_carbon_g).split(' ')[0]} unit="g CO₂e" note="Estimate" />
       
      </div>

      <section className="card insights-impact-card">
        <div className="insights-impact-heading">
          <div><h3>What GreenLens has estimated</h3><p>Environmental footprint across successful recorded inferences</p></div>
          <span>{stats.successful_requests.toLocaleString()} inferences</span>
        </div>
        <div className="insights-impact-grid">
          <div className="insights-impact-item energy-impact">
            <span className="impact-icon">⚡</span><span className="impact-label">Electricity consumed</span>
            <strong>{fmtEnergy(stats.total_energy_wh)}</strong>
            <small>{insightsLedEquivalent(stats.total_energy_wh)}</small>
          </div>
          <div className="insights-impact-item carbon-impact">
            <span className="impact-icon">☁</span><span className="impact-label">GHG emissions</span>
            <strong>{fmtCarbon(stats.total_carbon_g)}</strong>
            <small>Estimated greenhouse gases, expressed as CO₂ equivalent</small>
          </div>
          {/* <div className="insights-impact-item water-impact">
            <span className="impact-icon">💧</span><span className="impact-label">Water consumption</span>
            <strong>{stats.total_water_l != null ? `${(stats.total_water_l * 1000).toFixed(stats.total_water_l < 0.001 ? 3 : 2)} mL` : 'Not available'}</strong>
            <small>{stats.total_water_l != null ? insightsWaterEquivalent(stats.total_water_l) : 'No recorded inference returned EcoLogits WCF yet'}</small>
          </div> */}
        </div>
        
      </section>

      <div className="insights-chart-grid">
        <div className="insight-chart-card carbon-card">
          <div className="card-head">
            <div><h3>Carbon per response</h3><p>Estimated CO₂e for each of the latest responses</p></div>
            <span>Last {series.length} requests · Avg latency {fmtLatency(stats.average_latency_ms)}</span>
          </div>
          <CarbonBarChart data={series} format={fmtCarbon} />
          {showCarbonDetails && (
            <div className="insight-detail-list" aria-label="Carbon per response details">
              {[...series].reverse().map((item, index) => (
                <div key={`${item.label}-${index}`}><span>{item.label}</span><strong>{fmtCarbon(item.value)}</strong></div>
              ))}
            </div>
          )}
          <button className="insight-view-more" type="button" onClick={() => setShowCarbonDetails((value) => !value)}>
            {showCarbonDetails ? 'Hide details' : 'View more'} <span>{showCarbonDetails ? '−' : '+'}</span>
          </button>
        </div>

        <div className={`insight-chart-card models-card ${showModelDetails ? 'is-expanded' : ''}`}>
          <div className="card-head">
            <div><h3>Models used</h3><p>Share of successful responses by model</p></div>
            <span>{modelUsage.length} models</span>
          </div>
          <Donut data={modelUsage} />

          {showModelDetails && (
            <div className="insight-detail-list" aria-label="Model usage details">
              {[...modelUsage].sort((a, b) => b.value - a.value).map((item) => {
                const colorIndex = modelUsage.findIndex((model) => model.label === item.label)
                return (
                  <div key={item.label}>
                    <span className="model-detail-name"><i style={{ backgroundColor: MODEL_COLORS[colorIndex % MODEL_COLORS.length] }} />{item.label}</span>
                    <strong>{item.value} responses</strong>
                  </div>
                )
              })}
            </div>
          )}
          <button className="insight-view-more" type="button" onClick={() => setShowModelDetails((value) => !value)}>
            {showModelDetails ? 'Hide details' : 'View more'} <span>{showModelDetails ? '−' : '+'}</span>
          </button>
        </div>
      </div>

      <div className="insight-chart-card radar-card">
        <div className="card-head">
          <div><h3>Model performance</h3><p>Compare reliability, carbon, energy and latency performance</p></div>
          <span>Actual inference history</span>
        </div>
        <ModelRadar data={stats.model_performance ?? []} />
      </div>

      <div className="card">
        <h3>Recent routing decisions</h3>
        <div className="rows">
          {dateGroups.map((group) => (
            <div key={group.key}>
              <h4 style={{ margin: '16px 0 8px', color: 'var(--muted)', fontSize: 12, fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                {group.label}
              </h4>
              {group.decisions.map((decision) => (
                <div className="row" key={decision.id}>
                  <span className="row-main">
                    <strong>{decision.prompt}</strong>
                    <small>
                      {decision.ideal_model ? modelName(decision.ideal_model, modelNames.get(decision.ideal_model)) : 'Ideal model unavailable'}
                      {' → '}
                      {modelName(decision.actual_model, modelNames.get(decision.actual_model))}
                    </small>
                    <small>
                      {decision.selected_is_free === true ? 'Free model' : 'Paid model'}
                      {decision.fallback_used ? ' · Fallback used' : ''}
                    </small>
                  </span>
                  <span className="row-meta">
                    {fmtCarbon(decision.carbon_g)}
                    <small>Carbon · {decision.water_l != null ? `${(decision.water_l * 1000).toFixed(3)} mL water · ` : ''}Fit {Number.isFinite(decision.fit_score) ? decision.fit_score.toFixed(1) : '—'} · {decision.task_type}</small>
                  </span>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>  
    </section>
  )
}
