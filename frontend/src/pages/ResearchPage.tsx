import { FlaskConical, ShieldCheck, Database, BarChart3, AlertCircle } from 'lucide-react'

const stages = [
  ['Dataset audit', 'Locate and freeze the existing GreenLens evaluation prompts.'],
  ['Calibration snapshot', 'Freeze task-specific historical reliability and latency before evaluation.'],
  ['Paired execution', 'Run CHR and GreenLens on identical prompts, three attempts each.'],
  ['Manual quality review', 'Blind the response source and score correctness, relevance, completeness and instruction adherence.'],
  ['Comparison and radar', 'Aggregate raw measurements and generate fixed-scale comparison data.'],
]

export default function ResearchPage() {
  return (
    <main className="research-page">
      <div className="research-heading">
        <div>
          <span className="research-eyebrow">LOCAL EXPERIMENTAL WORKSPACE</span>
          <h1>Research Evaluation</h1>
          <p>Compare conventional heuristic routing with GreenLens sustainability-aware routing.</p>
        </div>
        <span className="research-local-tag"><ShieldCheck size={15}/> Local development only</span>
      </div>

      <section className="research-notice">
        <AlertCircle size={19}/>
        <div><strong>Evaluation runner is not connected yet</strong><p>The source archive did not contain a confirmed executable prompt dataset. This workspace is a local research scaffold; it does not run inference or display fabricated results.</p></div>
      </section>

      <section className="research-stat-grid">
        <article><span>Baseline</span><strong>CHR</strong><small>50% fit · 30% reliability · 20% latency</small></article>
        <article><span>Candidate pool</span><strong>Shared</strong><small>Same eligible models for both systems</small></article>
        <article><span>Repetitions</span><strong>3 × 2</strong><small>Three attempts per prompt, per system</small></article>
        <article><span>Quality review</span><strong>Manual</strong><small>Blind four-criterion scoring</small></article>
      </section>

      <section className="research-panel">
        <div className="research-panel-title"><Database size={18}/><h2>Experiment protocol</h2></div>
        <div className="research-stage-list">
          {stages.map(([title, description], index) => <div className="research-stage" key={title}>
            <span className="research-stage-number">{index + 1}</span>
            <div><strong>{title}</strong><p>{description}</p></div>
            <span className="research-stage-state">Pending</span>
          </div>)}
        </div>
      </section>

      <section className="research-panel research-metrics-panel">
        <div className="research-panel-title"><BarChart3 size={18}/><h2>Comparison metrics</h2></div>
        <div className="research-metric-list">
          {['Reliability','Carbon per attempt and successful response','Energy per attempt and successful response','Median and P95 latency','Manual response quality','Router selection overhead'].map(metric => <span key={metric}>{metric}</span>)}
        </div>
        <p className="research-footnote">Energy and carbon measurements must retain their provenance (measured, modelled, estimated or unavailable). Failed attempts remain included in per-attempt resource accounting.</p>
      </section>

      <section className="research-footer-note">
        <FlaskConical size={18}/>
        <p><strong>Production isolation:</strong> CHR is not registered in the live model catalogue, does not receive production chat requests, and does not write to live inference records or Insights.</p>
      </section>
    </main>
  )
}
