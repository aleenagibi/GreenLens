import { useEffect, useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'
import './App.css'

type ComparisonModel = {
  rank: number
  model: string
  display_name?: string | null
  provider?: string | null
  is_free: boolean
  fit_score: number
  capability_score?: number | null
  capability_source: string
  carbon_score?: number | null
  latency_score?: number | null
  complexity_score?: number | null
  estimated_energy_wh?: number | null
  estimated_carbon_g?: number | null
  selected?: boolean
  ideal?: boolean
}

type ChatResponse = {
  provider: string
  model: string
  content: string
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
  recommendation: {
    task_type: string
    score: number
    reason: string
  }
  benchmark: {
    latency_ms: number
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
    provider: string
    model: string
    success: boolean
  }
  sustainability: {
    energy_wh: number
    carbon_g: number
    green_score: number
  }
  pipeline: {
    task?: {
      prompt?: string
      task_type?: string
      complexity?: {
        score?: number
      }
      embedding_dimensions?: number
    }
    selection?: Record<string, unknown>
    explanation?: Record<string, unknown>
  }
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
    comparison: ComparisonModel[]
  }
}

type HistoryItem = {
  id: string
  prompt: string
  content: string
  createdAt: string
  model: string
  idealModel: string
  selectedModel: string
  taskType: string
  carbonG: number
  energyWh: number
  latencyMs: number
  fitScore: number
  comparison: ComparisonModel[]
}

type Page = 'chat' | 'history' | 'insights' | 'how'

const API_URL = 'http://127.0.0.1:8000/chat'
const HISTORY_KEY = 'greenlens_history_v1'
const MAX_HISTORY = 20

const pipelineStages = [
  'Task understanding',
  'Semantic analysis',
  'Complexity estimation',
  'Capability evaluation',
  'Environmental impact',
  'Optimization',
  'Model selection',
  'Explanation',
]

function formatModelName(displayName?: string | null, model?: string): string {
  if (displayName) return displayName
  if (!model) return 'Unknown model'
  const clean = model.includes('/') ? model.split('/').pop() ?? model : model
  return clean
    .replace(/:free$/i, '')
    .replace(/[-_]/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function formatLatency(ms: number): string {
  if (ms < 1000) return `${Math.round(ms)} ms`
  return `${(ms / 1000).toFixed(1)} sec`
}

function formatCarbon(value: number): string {
  if (value < 0.01) return `${value.toFixed(4)} g CO₂e`
  return `${value.toFixed(2)} g CO₂e`
}

function formatEnergy(value: number): string {
  if (value < 0.01) return `${value.toFixed(4)} Wh`
  return `${value.toFixed(2)} Wh`
}

function impactLabel(carbon: number): string {
  if (carbon < 0.5) return 'Low estimated impact'
  if (carbon < 2) return 'Moderate estimated impact'
  return 'Higher estimated impact'
}

function impactDescription(carbon: number): string {
  if (carbon < 0.5) return 'This response used a relatively low-impact inference route.'
  if (carbon < 2) return 'This response used a moderate-impact inference route.'
  return 'This response required a higher-impact inference route.'
}

function loadHistory(): HistoryItem[] {
  try {
    const saved = localStorage.getItem(HISTORY_KEY)
    return saved ? JSON.parse(saved) : []
  } catch {
    return []
  }
}

function compactHistoryItem(response: ChatResponse, prompt: string): HistoryItem {
  const routing = response.routing
  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
    prompt,
    content: response.content,
    createdAt: new Date().toISOString(),
    model: response.benchmark.model,
    idealModel: formatModelName(routing.ideal_display_name, routing.ideal_model),
    selectedModel: formatModelName(routing.selected_display_name, routing.selected_model),
    taskType: response.recommendation.task_type,
    carbonG: response.sustainability.carbon_g,
    energyWh: response.sustainability.energy_wh,
    latencyMs: response.benchmark.latency_ms,
    fitScore: routing.fit_score,
    comparison: routing.comparison.slice(0, 30),
  }
}

function App() {
  const [page, setPage] = useState<Page>('chat')
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState<ChatResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState<HistoryItem[]>(loadHistory)
  const [modal, setModal] = useState<'why' | 'impact' | 'landscape' | null>(null)

  useEffect(() => {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, MAX_HISTORY)))
  }, [history])

  const routing = response?.routing
  const sustainability = response?.sustainability
  const benchmark = response?.benchmark

  const selectedModel = routing
    ? formatModelName(routing.selected_display_name, routing.selected_model)
    : ''
  const idealModel = routing
    ? formatModelName(routing.ideal_display_name, routing.ideal_model)
    : ''

  const actualModel = response ? formatModelName(undefined, response.benchmark.model) : ''

  const selectedCandidate = routing?.comparison?.find((candidate) => candidate.selected)
  const idealCandidate = routing?.comparison?.find((candidate) => candidate.ideal)

  const carbonDifference = useMemo(() => {
    if (!idealCandidate?.estimated_carbon_g || selectedCandidate?.estimated_carbon_g == null) return null
    return idealCandidate.estimated_carbon_g - selectedCandidate.estimated_carbon_g
  }, [idealCandidate, selectedCandidate])

  const carbonReduction = useMemo(() => {
    if (carbonDifference == null || !idealCandidate?.estimated_carbon_g || carbonDifference <= 0) return null
    return Math.round((carbonDifference / idealCandidate.estimated_carbon_g) * 100)
  }, [carbonDifference, idealCandidate])

  const submitPrompt = async (value = prompt) => {
    const trimmedPrompt = value.trim()
    if (!trimmedPrompt || loading) return

    setPrompt(trimmedPrompt)
    setLoading(true)
    setError('')
    setResponse(null)
    setModal(null)
    setPage('chat')

    try {
      const result = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: trimmedPrompt }),
      })
      const data = await result.json()
      if (!result.ok) {
        throw new Error(data?.detail?.message || data?.detail || 'GreenLens could not process this request.')
      }
      setResponse(data)
      setHistory((current) => [compactHistoryItem(data, trimmedPrompt), ...current].slice(0, MAX_HISTORY))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong while contacting GreenLens.')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      event.preventDefault()
      submitPrompt()
    }
  }

  const startNewChat = () => {
    setPrompt('')
    setResponse(null)
    setError('')
    setModal(null)
    setPage('chat')
  }

  const openHistoryItem = (item: HistoryItem) => {
    const restored: ChatResponse = {
      provider: 'OpenRouter',
      model: item.model,
      content: item.content,
      usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
      recommendation: { task_type: item.taskType, score: item.fitScore, reason: 'Restored from conversation history.' },
      benchmark: {
        latency_ms: item.latencyMs,
        prompt_tokens: 0,
        completion_tokens: 0,
        total_tokens: 0,
        provider: 'OpenRouter',
        model: item.model,
        success: true,
      },
      sustainability: { energy_wh: item.energyWh, carbon_g: item.carbonG, green_score: 0 },
      pipeline: {},
      routing: {
        ideal_model: item.idealModel,
        ideal_display_name: item.idealModel,
        ideal_is_free: false,
        selected_model: item.selectedModel,
        selected_display_name: item.selectedModel,
        selected_is_free: true,
        fit_score: item.fitScore,
        used_free_alternative: item.idealModel !== item.selectedModel,
        capability_gap: null,
        reason: 'This conversation was restored from history. Full live routing metadata is not stored for historical conversations.',
        summary: 'Historical conversation',
        comparison: item.comparison,
      },
    }
    setPrompt(item.prompt)
    setResponse(restored)
    setModal(null)
    setPage('chat')
  }

  const clearHistory = () => {
    setHistory([])
    localStorage.removeItem(HISTORY_KEY)
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <button className="brand" onClick={() => setPage('chat')} aria-label="Go to GreenLens chat">
          <div className="brand-mark"><span /><span /><span /></div>
          <div>
            <div className="brand-name">GREENLENS</div>
            <div className="brand-tagline">TASK IN. RIGHT MODEL OUT.</div>
          </div>
        </button>

        <nav className="top-navigation" aria-label="Main navigation">
          <button className={page === 'chat' ? 'active' : ''} onClick={() => setPage('chat')}>CHAT</button>
          <button className={page === 'history' ? 'active' : ''} onClick={() => setPage('history')}>HISTORY</button>
          <button className={page === 'insights' ? 'active' : ''} onClick={() => setPage('insights')}>INSIGHTS</button>
          <button className={page === 'how' ? 'active' : ''} onClick={() => setPage('how')}>HOW IT WORKS</button>
        </nav>

        <button className="new-inference-button" onClick={startNewChat}>
          <span>+</span> NEW CHAT
        </button>
      </header>

      {page === 'chat' && (
        <main className="chat-page">
          <div className={`chat-column ${response ? 'has-response' : ''}`}>
            {!response && !loading && (
              <section className="welcome-block">
                <div className="welcome-kicker"><span /> CARBON-AWARE AI ROUTING</div>
                <h1>Ask anything.<br /><em>GreenLens chooses the route.</em></h1>
                <p>Get the answer you need while GreenLens quietly considers model capability, performance and environmental impact.</p>
              </section>
            )}

            {response && (
              <section className="conversation-prompt">
                <span className="prompt-label">YOUR TASK</span>
                <p>{prompt}</p>
              </section>
            )}

            {loading && (
              <section className="loading-card">
                <div className="loading-orb"><span /></div>
                <div>
                  <span className="prompt-label">GREENLENS IS WORKING</span>
                  <h2>Finding a suitable route for your task...</h2>
                  <p>Evaluating models before generating your answer.</p>
                </div>
              </section>
            )}

            {error && (
              <section className="error-card">
                <strong>GreenLens couldn't complete the inference.</strong>
                <p>{error}</p>
              </section>
            )}

            {response && routing && sustainability && benchmark && (
              <section className="answer-section">
                <div className="generated-row">
                  <div className="generated-by">
                    <span className="model-dot">✦</span>
                    <span>Generated by</span>
                    <strong>{actualModel}</strong>
                    {routing.selected_is_free && <span className="free-pill">FREE</span>}
                  </div>
                  <span className="answer-time">{formatLatency(benchmark.latency_ms)}</span>
                </div>

                <article className="answer-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]}
                    rehypePlugins={[rehypeKatex]}>{response.content}</ReactMarkdown>
                </article>

                <div className="greenlens-tools">
                  <button className="impact-chip" onClick={() => setModal('impact')}>
                    <span className="chip-icon">⌁</span>
                    <span><strong>{impactLabel(sustainability.carbon_g)}</strong><small>{impactDescription(sustainability.carbon_g)}</small></span>
                    <b>›</b>
                  </button>

                  <button className="why-chip" onClick={() => setModal('why')}>
                    <span><strong>Why this model?</strong><small>{idealModel} → {selectedModel}</small></span>
                    <b>›</b>
                  </button>

                  <button className="landscape-link" onClick={() => setModal('landscape')}>
                    View model landscape <span>→</span>
                  </button>
                </div>
              </section>
            )}

            <section className="composer-wrap">
              <textarea
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Message GreenLens..."
                disabled={loading}
                rows={response ? 3 : 4}
              />
              <div className="composer-footer">
                <span>Ctrl + Enter to send</span>
                <button className="send-button" onClick={() => submitPrompt()} disabled={!prompt.trim() || loading}>
                  {loading ? <span className="button-spinner" /> : '↑'}
                </button>
              </div>
            </section>
          </div>
        </main>
      )}

      {page === 'history' && (
        <main className="page-container">
          <div className="page-heading">
            <div><span className="welcome-kicker"><span /> CONVERSATIONS</span><h1>History</h1><p>Your recent GreenLens conversations.</p></div>
            {history.length > 0 && <button className="text-button danger" onClick={clearHistory}>Clear history</button>}
          </div>
          {history.length === 0 ? (
            <div className="empty-state"><div>◌</div><h2>No conversations yet</h2><p>Your GreenLens conversations will appear here after you ask a question.</p><button className="primary-button" onClick={startNewChat}>Start a chat</button></div>
          ) : (
            <div className="history-list">
              {history.map((item) => (
                <button className="history-item" key={item.id} onClick={() => openHistoryItem(item)}>
                  <div className="history-main"><strong>{item.prompt}</strong><span>{item.content.replace(/[#*_`|]/g, '').slice(0, 150)}{item.content.length > 150 ? '…' : ''}</span></div>
                  <div className="history-meta"><span>{formatModelName(undefined, item.model)}</span><small>{new Date(item.createdAt).toLocaleString()}</small></div>
                  <span className="history-arrow">→</span>
                </button>
              ))}
            </div>
          )}
        </main>
      )}

      {page === 'insights' && (
        <main className="page-container">
          <div className="page-heading"><div><span className="welcome-kicker"><span /> GREENLENS INSIGHTS</span><h1>Your AI footprint</h1><p>A simple view of the conversations recorded in this browser.</p></div></div>
          <section className="insight-grid">
            <div className="insight-stat"><span>CONVERSATIONS</span><strong>{history.length}</strong><small>Stored in this browser</small></div>
            <div className="insight-stat"><span>ESTIMATED ENERGY</span><strong>{formatEnergy(history.reduce((sum, item) => sum + item.energyWh, 0))}</strong><small>Across recorded responses</small></div>
            <div className="insight-stat"><span>ESTIMATED CARBON</span><strong>{formatCarbon(history.reduce((sum, item) => sum + item.carbonG, 0))}</strong><small>Estimated CO₂e</small></div>
            <div className="insight-stat"><span>MODELS USED</span><strong>{new Set(history.map((item) => item.model)).size}</strong><small>Actual answering models</small></div>
          </section>
          <section className="insight-card">
            <div className="insight-card-header"><div><span className="prompt-label">MODEL LANDSCAPE</span><h2>Recent routing decisions</h2></div><span>{history.length} recorded</span></div>
            {history.length === 0 ? <p className="muted">Run a few tasks to build your GreenLens history.</p> : <div className="decision-list">{history.slice(0, 10).map((item) => <div className="decision-row" key={item.id}><div><strong>{item.selectedModel}</strong><span>{item.prompt}</span></div><div><strong>{item.fitScore.toFixed(2)}</strong><span>fit</span></div><div><strong>{formatCarbon(item.carbonG)}</strong><span>impact</span></div></div>)}</div>}
          </section>
          <p className="insight-note">These dashboard figures are based on conversations stored by this browser. They are estimates, not a claim of measured real-world emissions.</p>
        </main>
      )}

      {page === 'how' && (
        <main className="page-container how-page">
          <div className="page-heading"><div><span className="welcome-kicker"><span /> UNDER THE HOOD</span><h1>How GreenLens works</h1><p>GreenLens evaluates a task before inference and uses that analysis to choose a route.</p></div></div>
          <div className="pipeline-grid">{pipelineStages.map((stage, index) => <div className="pipeline-step" key={stage}><span>{String(index + 1).padStart(2, '0')}</span><strong>{stage}</strong>{index < pipelineStages.length - 1 && <i>→</i>}</div>)}</div>
          <section className="how-cards"><article><span>01</span><h2>Capability</h2><p>GreenLens uses available benchmark signals to estimate how well a model fits the task.</p></article><article><span>02</span><h2>Impact</h2><p>Model-specific sustainability estimates are used where available, with a fallback estimate when coverage is unavailable.</p></article><article><span>03</span><h2>Optimization</h2><p>The system combines the available signals into a GreenLens score and identifies an ideal route.</p></article><article><span>04</span><h2>Free execution</h2><p>When the ideal route is paid, GreenLens can select a suitable free alternative for actual execution.</p></article></section>
        </main>
      )}

      {modal && response && routing && sustainability && benchmark && (
        <div className="modal-backdrop" onMouseDown={() => setModal(null)}>
          <div className={`modal-panel ${modal === 'landscape' ? 'wide' : ''}`} onMouseDown={(event) => event.stopPropagation()}>
            <button className="modal-close" onClick={() => setModal(null)}>×</button>
            {modal === 'why' && <>
              <span className="welcome-kicker"><span /> ROUTING EXPLANATION</span><h2>Why this model?</h2>
              <p className="modal-lead">GreenLens evaluated the task before answering and separated the <strong>ideal model</strong> from the <strong>model actually used</strong>.</p>
              <div className="route-flow"><div><span>IDEAL</span><strong>{idealModel}</strong><small>{routing.ideal_is_free ? 'Free' : 'Paid'}</small></div><b>→</b><div className="selected-box"><span>SELECTED</span><strong>{selectedModel}</strong><small>{routing.selected_is_free ? 'Free ✓' : 'Paid'}</small></div></div>
              <div className="reason-box"><span>GREENLENS' REASON</span><p>{routing.reason}</p></div>
              <div className="modal-stats"><div><span>Task fit</span><strong>{routing.fit_score.toFixed(2)}/10</strong></div><div><span>Response time</span><strong>{formatLatency(benchmark.latency_ms)}</strong></div><div><span>Actual model</span><strong>{actualModel}</strong></div></div>
            </>}
            {modal === 'impact' && <>
              <span className="welcome-kicker"><span /> ENVIRONMENTAL IMPACT</span><h2>{impactLabel(sustainability.carbon_g)}</h2><p className="modal-lead">{impactDescription(sustainability.carbon_g)} The values below are estimates.</p>
              <div className="impact-detail-hero"><strong>{formatCarbon(sustainability.carbon_g)}</strong><span>estimated carbon impact</span></div>
              <div className="modal-stats"><div><span>Energy</span><strong>{formatEnergy(sustainability.energy_wh)}</strong></div><div><span>Green score</span><strong>{sustainability.green_score.toFixed(2)}/10</strong></div><div><span>Response</span><strong>{formatLatency(benchmark.latency_ms)}</strong></div></div>
              {carbonReduction != null && <div className="saving-note"><strong>{carbonReduction}% lower estimated carbon</strong><span>than the ideal model's pre-inference estimate.</span></div>}
              <p className="modal-footnote">Environmental figures are model estimates and can vary with infrastructure, location and inference conditions.</p>
            </>}
            {modal === 'landscape' && <>
              <span className="welcome-kicker"><span /> MODEL LANDSCAPE</span><h2>How the candidates compared</h2><p className="modal-lead">The full candidate set considered for this request. Values are GreenLens estimates.</p>
              <div className="table-scroll"><table className="landscape-table"><thead><tr><th>#</th><th>MODEL</th><th>FIT</th><th>CARBON</th><th>ENERGY</th><th>STATUS</th></tr></thead><tbody>{routing.comparison.map((candidate) => <tr key={`${candidate.rank}-${candidate.model}`} className={candidate.selected ? 'selected-row' : ''}><td>{candidate.rank}</td><td><strong>{formatModelName(candidate.display_name, candidate.model)}</strong><small>{candidate.provider || 'OpenRouter'}</small></td><td>{candidate.fit_score.toFixed(2)}</td><td>{candidate.estimated_carbon_g != null ? formatCarbon(candidate.estimated_carbon_g) : '—'}</td><td>{candidate.estimated_energy_wh != null ? formatEnergy(candidate.estimated_energy_wh) : '—'}</td><td>{candidate.selected ? 'SELECTED' : candidate.ideal ? 'IDEAL' : candidate.is_free ? 'FREE' : 'PAID'}</td></tr>)}</tbody></table></div>
            </>}
          </div>
        </div>
      )}

      <footer className="footer"><span>GREENLENS · SMARTER AI. LOWER IMPACT.</span><span>SDG 13 · CLIMATE ACTION</span></footer>
    </div>
  )
}

export default App
