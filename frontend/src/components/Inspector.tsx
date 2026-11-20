import { useEffect } from 'react'
import type { Answer, ModelCatalog } from '../types'
import { fmtCarbon, fmtEnergy, fmtLatency, modelName } from '../utils'

const ledEquivalent = (energyWh: number) => {
  const seconds = (energyWh / 10) * 3600 // illustrative 10 W LED bulb
  if (!Number.isFinite(seconds) || seconds < 0) return 'LED equivalent unavailable'
  if (seconds < 60) return `About ${seconds.toFixed(1)} seconds of a 10 W LED bulb`
  return `About ${(seconds / 60).toFixed(1)} minutes of a 10 W LED bulb`
}


type TileProps = { label: string; value: string; unit: string; note: string; delay: number }

function Tile({ label, value, unit, note, delay }: TileProps) {
  return (
    <div className="tile" style={{ ['--d' as string]: `${delay}ms` }}>
      <span className="tile-label">{label}</span>
      <span className="tile-dots" aria-hidden="true">•••</span>
      <strong>{value}<small>{unit}</small></strong>
      <div className="neon">{note}</div>
    </div>
  )
}

export default function Inspector({ answer: a, catalog, onClose }: { answer: Answer; catalog: ModelCatalog | null; onClose: () => void }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const details = a.routingDetails
  const routing = details?.routing
  const inference = details?.inference
  const pipeline = details?.pipeline
  const comparison = routing?.comparison ?? a.comparison
  const idealCarbon = routing?.ideal_estimated_carbon_g ?? comparison.find((candidate) => candidate.ideal)?.estimated_carbon_g ?? null
  const selectedCarbon = routing?.selected_estimated_carbon_g ?? comparison.find((candidate) => candidate.selected)?.estimated_carbon_g ?? null
  // The "ideal" candidate is the highest-ranked candidate, not a measured
  // counterfactual. Show a signed estimate difference instead of claiming savings.


  const maxCarbon = Math.max(idealCarbon ?? 0, selectedCarbon ?? 0)
  const width = (value: number | null) => `${maxCarbon && value != null ? (value / maxCarbon) * 100 : 0}%`
  const complexity = pipeline?.task?.complexity

  const modelMetadata = (id: string) => catalog?.models.find((model) => model.model_id === id)
  const displayName = (id: string, provided?: string | null) => modelName(id, provided || modelMetadata(id)?.display_name)

  return (
    <>
      <div className="scrim" onClick={onClose} />
      <aside className="inspector" role="dialog" aria-label="Response details">
        <header className="insp-head">
          <div>
            <span className="fine">Actually answered by</span>
            <h2>{displayName(a.model)}</h2>
          </div>
          <button className="icon-btn" onClick={onClose} aria-label="Close details">×</button>
        </header>

        <div className="insp-body">
          <div className="tiles two">
            <Tile delay={0} label="Response time" value={fmtLatency(a.latencyMs)} unit="" note="Backend benchmark" />
            <Tile delay={60} label="Task fit" value={a.fitScore.toFixed(1)} unit="/10" note={a.taskType} />
          </div>

          <section className="card impact-panel">
            <div className="impact-panel-heading">
              <div><h3>Environmental impact</h3><p>Estimated footprint of this inference</p></div>
              <span className={`impact-source ${a.sustainabilitySource === 'ecologits' ? 'is-ecologits' : ''}`}>
                {a.sustainabilitySource === 'ecologits' ? 'EcoLogits estimate' : 'GreenLens fallback'}
              </span>
            </div>
            <div className="impact-metric-grid">
              <div className="impact-metric energy-impact">
                <span className="impact-icon">⚡</span><span className="impact-label">Electricity</span>
                <strong>{fmtEnergy(a.energyWh)}</strong>
                <small>{ledEquivalent(a.energyWh)}</small>
              </div>
              <div className="impact-metric carbon-impact">
                <span className="impact-icon">☁</span><span className="impact-label">GHG emissions</span>
                <strong>{fmtCarbon(a.carbonG)}</strong>
                <small>Greenhouse gases, expressed as CO₂ equivalent</small>
              </div>
              
            </div>
            
          </section>

          <section className="card">
            <h3>Routing decision</h3>
            <div className="route-row">
              <span>Ideal model<small>{displayName(routing?.ideal_model ?? a.idealModel, routing?.ideal_display_name)}{(routing?.ideal_is_free ?? a.idealIsFree) ? ' · free' : ' · paid'}</small></span>
              <div className="bar"><i className="amber" style={{ width: width(idealCarbon) }} /></div>
              <b>{idealCarbon != null ? fmtCarbon(idealCarbon) : '—'}</b>
            </div>
            <div className="route-row">
              <span>Selected model<small>{displayName(routing?.selected_model ?? a.selectedModel, routing?.selected_display_name)}{(routing?.selected_is_free ?? a.selectedIsFree) ? ' · free' : ' · paid'}</small></span>
              <div className="bar"><i style={{ width: width(selectedCarbon) }} /></div>
              <b>{selectedCarbon != null ? fmtCarbon(selectedCarbon) : '—'}</b>
            </div>
            
            <p className="reason">{routing?.summary || routing?.reason || a.reason}</p>
            
          </section>

          <section className="card">
            <h3>Execution details</h3>
            <div className="rows">
              <div className="row"><span className="row-main"><strong>Requested model</strong><small>Selected by the routing pipeline</small></span><span className="row-meta">{displayName(inference?.selected_model ?? routing?.selected_model ?? a.selectedModel)}</span></div>
              <div className="row"><span className="row-main"><strong>Actual model</strong><small>Returned by the inference provider</small></span><span className="row-meta">{displayName(inference?.actual_model ?? a.model)}</span></div>
              <div className="row"><span className="row-main"><strong>Fallback</strong></span><span className="row-meta">{inference?.fallback_used ? 'Used' : 'Not used'}</span></div>
             
            </div>
            {inference?.attempts?.length ? (
              <>
                <h4>Execution attempts</h4>
                <div className="rows">
                  {inference.attempts.map((attempt, index) => (
                    <div className="row" key={`${attempt.model}-${index}`}>
                      <span className="row-main"><strong>{displayName(attempt.model)}</strong></span>
                      <span className="row-meta">{attempt.success ? 'Success' : 'Failed'}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : null}
          </section>

          <section className="card">
            <h3>Task analysis</h3>
            <div className="rows">
              <div className="row"><span className="row-main"><strong>Task type</strong></span><span className="row-meta">{pipeline?.task?.task_type || a.taskType}</span></div>
              <div className="row"><span className="row-main"><strong>Complexity</strong><small>{complexity?.level || 'Not reported'}</small></span><span className="row-meta">{complexity?.score != null ? `${complexity.score}/10` : '—'}</span></div>
              <div className="row"><span className="row-main"><strong>Embedding dimensions</strong></span><span className="row-meta">{pipeline?.task?.embedding_dimensions ?? '—'}</span></div>
            </div>
           
          </section>

          <section className="card">
            <h3>Model landscape</h3>
            <div className="table-scroll">
              <table>
                <thead><tr><th>#</th><th>Model</th><th>Fit</th><th>Context</th><th>Carbon</th><th>Energy</th><th>Status</th></tr></thead>
                <tbody>
                  {comparison.map((candidate) => (
                    <tr key={`${candidate.rank}-${candidate.model}`} className={candidate.selected ? 'sel' : ''}>
                      <td>{candidate.rank}</td>
                      <td><strong>{displayName(candidate.model, candidate.display_name)}</strong><small>{candidate.provider || modelMetadata(candidate.model)?.provider || '—'}</small></td>
                      <td>{candidate.fit_score.toFixed(2)}</td>
                      <td>{modelMetadata(candidate.model)?.context_length ? `${modelMetadata(candidate.model)?.context_length?.toLocaleString()} tokens` : '—'}</td>
                      <td>{candidate.estimated_carbon_g != null ? fmtCarbon(candidate.estimated_carbon_g) : '—'}</td>
                      <td>{candidate.estimated_energy_wh != null ? fmtEnergy(candidate.estimated_energy_wh) : '—'}</td>
                      <td>{candidate.selected ? 'Selected' : candidate.ideal ? 'Ideal' : candidate.is_free ? 'Free' : 'Paid'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="fine">Showing {comparison.length} of {routing?.candidate_count ?? comparison.length} ranked candidates. Ranking and estimates are supplied by the backend; context limits come from the live model catalogue. Environmental figures are estimates, not measured emissions.</p>
          </section>

          <section className="card">
            <h3>Token usage</h3>
            <div className="rows">
              <div className="row"><span className="row-main"><strong>Prompt tokens</strong></span><span className="row-meta">{details?.usage?.prompt_tokens ?? '—'}</span></div>
              <div className="row"><span className="row-main"><strong>Completion tokens</strong></span><span className="row-meta">{details?.usage?.completion_tokens ?? '—'}</span></div>
              <div className="row"><span className="row-main"><strong>Total tokens</strong></span><span className="row-meta">{details?.usage?.total_tokens ?? '—'}</span></div>
              {details?.context ? <div className="row"><span className="row-main"><strong>Context window</strong></span><span className="row-meta">{(details.context.input_tokens_actual ?? details.context.input_tokens_estimated).toLocaleString()} / {details.context.context_window_tokens.toLocaleString()}</span></div> : null}
            </div>
          </section>
        </div>
      </aside>
    </>
  )
}

export { Tile }
